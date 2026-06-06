"""Mock for the Sybol digital-identity / VC-issuance API.

The real integration submits an *unsigned* W3C VC Data Model 2.0 payload to
Sybol's ``businessLogic`` API (``POST /credentials/issue``). Sybol signs it with
its DID + svault cryptographic layer and returns a fully signed Verifiable
Credential (issuer DID, ``proof``, and a ``credentialStatus`` revocation entry
added).

Open items still TBD with Iñigo (per the project doc) are parameterised here so
tests don't bake in guesses:
* the issuer DID value (``issuer_did``),
* the catalog schema reference,
* whether issuance is one call or a separate signing endpoint.

This mock supports both a high-level ``issue_credential(payload)`` method and a
minimal httpx-style ``post(path, json=...)`` surface, plus failure injection so
QA can exercise the §3.6 "VC Issuance Success Rate >= 95%" threshold and the
TC-004 error-handling path.
"""

from __future__ import annotations

import copy
import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

DEFAULT_ISSUER_DID = "did:web:sybol.id"
DEFAULT_SCHEMA_REF = "https://catalog.sybol.id/schemas/MediaComplianceCredential"
REQUIRED_SUBJECT_FIELDS = (
    "mediaHash",
    "authenticityScore",
    "scoreBreakdown",
    "complianceStatus",
    "regulationRefs",
)


class SybolAPIError(Exception):
    """Raised for simulated Sybol API failures (network / 4xx / 5xx)."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class HTTPResponse:
    """Tiny httpx.Response-like object for the ``post`` surface."""

    status_code: int
    _json: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise SybolAPIError(f"HTTP {self.status_code}", self.status_code)


@dataclass
class RecordedIssue:
    payload: dict[str, Any]
    succeeded: bool


class MockSybolClient:
    """Stand-in for the Sybol businessLogic VC issuance client."""

    def __init__(
        self,
        issuer_did: str = DEFAULT_ISSUER_DID,
        schema_ref: str = DEFAULT_SCHEMA_REF,
        base_url: str = "https://api.sybol.id",
    ) -> None:
        self.issuer_did = issuer_did
        self.schema_ref = schema_ref
        self.base_url = base_url
        self.issued: list[RecordedIssue] = []

        self._fail_queue: list[SybolAPIError] = []
        self._status_counter = 0

    # -- programming ----------------------------------------------------------

    def fail_next(self, error: SybolAPIError | None = None) -> MockSybolClient:
        """Make the next issuance raise (defaults to a 503)."""
        self._fail_queue.append(error or SybolAPIError("Sybol service unavailable", 503))
        return self

    def reset(self) -> None:
        self.issued.clear()
        self._fail_queue.clear()
        self._status_counter = 0

    @property
    def issue_count(self) -> int:
        return len(self.issued)

    @property
    def success_rate(self) -> float:
        if not self.issued:
            return 1.0
        return sum(1 for r in self.issued if r.succeeded) / len(self.issued)

    # -- validation -----------------------------------------------------------

    def _validate(self, payload: dict[str, Any]) -> None:
        if "credentialSubject" not in payload:
            raise SybolAPIError("missing credentialSubject", 400)
        subject = payload["credentialSubject"]
        missing = [f for f in REQUIRED_SUBJECT_FIELDS if f not in subject]
        if missing:
            raise SybolAPIError(f"credentialSubject missing fields: {missing}", 400)

    # -- signing --------------------------------------------------------------

    def _sign(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Attach issuer DID, credentialStatus, and a deterministic mock proof."""
        signed = copy.deepcopy(payload)
        signed.setdefault(
            "@context",
            [
                "https://www.w3.org/ns/credentials/v2",
            ],
        )
        signed.setdefault("id", f"urn:uuid:{uuid.uuid4()}")
        signed.setdefault("type", ["VerifiableCredential", "MediaComplianceCredential"])
        signed["issuer"] = self.issuer_did
        signed.setdefault("validFrom", datetime.now(UTC).isoformat())
        signed.setdefault("credentialSchema", {"id": self.schema_ref, "type": "JsonSchema"})

        self._status_counter += 1
        signed["credentialStatus"] = {
            "id": f"{self.base_url}/status/list#{self._status_counter}",
            "type": "StatusList2021Entry",
            "statusPurpose": "revocation",
            "statusListIndex": str(self._status_counter),
            "statusListCredential": f"{self.base_url}/status/list",
        }

        # Deterministic, fake signature — never represents real cryptography.
        digest = hashlib.sha256((str(signed.get("id")) + self.issuer_did).encode("utf-8")).hexdigest()
        signed["proof"] = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-2022",
            "created": datetime.now(UTC).isoformat(),
            "verificationMethod": f"{self.issuer_did}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": f"z{digest}",  # multibase-ish prefix; mock only
        }
        return signed

    # -- high-level API -------------------------------------------------------

    def issue_credential(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit an unsigned VC payload; return the signed credential."""
        if self._fail_queue:
            err = self._fail_queue.pop(0)
            self.issued.append(RecordedIssue(payload=payload, succeeded=False))
            raise err

        self._validate(payload)
        signed = self._sign(payload)
        self.issued.append(RecordedIssue(payload=payload, succeeded=True))
        return signed

    async def issue_credential_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.issue_credential(payload)

    # -- httpx-style surface --------------------------------------------------

    def post(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> HTTPResponse:
        if path.rstrip("/").endswith("/credentials/issue"):
            try:
                signed = self.issue_credential(json or {})
                return HTTPResponse(200, signed)
            except SybolAPIError as exc:
                return HTTPResponse(exc.status_code, {"error": str(exc)})
        return HTTPResponse(404, {"error": f"unknown path {path}"})
