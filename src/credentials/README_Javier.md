# src/credentials/ — Javier

Your job here is to build the unsigned W3C VC Data Model 2.0 payload
using the scoring output from src/scoring/ and the regulationRefs
from src/rag/.

Build the payload with all of these fields:

- id: UUID URN for the credential
- type: ["VerifiableCredential", "MediaComplianceCredential"]
- issuer: Sybol DID — get the value from Darius once he confirms with Iñigo
- validFrom: ISO 8601 timestamp
- credentialSchema: Sybol catalog schema reference
- credentialStatus: StatusList2021 revocation entry
- credentialSubject.id: urn:media:{sha256}
- credentialSubject.mediaHash: SHA-256 of raw file before resizing
- credentialSubject.authenticityScore: float 0.0 → 1.0
- credentialSubject.scoreBreakdown: [m, a, v, p]
- credentialSubject.complianceStatus: compliant / non-compliant / review
- credentialSubject.regulationRefs: structured array from Alex's RAG output
- credentialSubject.modelVersion: model version string
- credentialSubject.analysisTimestamp: ISO 8601 timestamp of analysis
- credentialSubject.evidenceUrl: link to Qdrant audit trail record

Raw images are never stored here — only the hash and feature signals.
This is a hard GDPR data minimisation requirement.

Once the payload is built, hand it to Darius — he handles the signing.
