# Spec: Self-Issue LoA 0 (issue #139)

**Status:** Approved

**Date:** 2026-03-30

**Authors:** dispatcher-agent

---

## User Story

> **As a COMPANY** I want to be able to self-issue credentials with LoA 0
> so that I can assert my own attributes without requiring a third-party issuer.

Issue: #139

---

## Background

The credential issuance flow in the WWC webapp allows a company to select one or more recipient subjects via the `IssueModal`. The subject list already includes a "Self-issue" (Autoalegar) option, prepended with `isSelf: true` by `useSubjectManager`.

However, two problems exist today:

1. `levelOfAssurance` is hardcoded to `2` (medium) for all credentials — including self-issued ones. Self-asserted credentials, by definition, must be LoA 0.
2. Self-issued credentials are propagated to the central node via `propagate()`, even though issuer and recipient share the same wallet — making propagation redundant.

---

## User Flow

1. Company navigates to Catalog and selects one or more claims.
2. Company clicks **Emitir** to open the `IssueModal`.
3. Company selects **Autoalegar** (own DID) as the subject.
4. Company fills in claim values and dates, then clicks **Emitir los atributos seleccionados**.
5. The credential is issued with `levelOfAssurance: 0`.
6. The credential is stored locally (in the company's own wallet). Propagation to the central node is skipped.

---

## UI/UX Changes

### IssueModal — LoA indicator

When the company selects itself (Autoalegar) as a subject, display a small informational note below the subject selector indicating that the credential will be self-asserted (LoA 0).

This is rendered as a MUI `Alert` with severity `info`, using the i18n key `catalog.selfAssertedLoaNote`.

The note is shown when at least one of the selected subjects has `isSelf === true`.

---

## Files to Modify

### `webApps/wwc/src/pages/Catalog/engine.js`

Two changes:

**Change 1 — Force LoA 0 for self-issued credentials:**

In `createCredentialFromDocument`, `isSelf` must be propagated from each subject into its corresponding credential entries. The `claimsToIssue` loop must include `isSelf` from the subject, and `levelOfAssurance` must be derived from it:

```js
// Before
claimsToIssue.push({
  ...entry,
  'recipientDid': subject.did
});

// After
claimsToIssue.push({
  ...entry,
  'recipientDid': subject.did,
  'isSelf': subject.isSelf || false
});
```

And the `levelOfAssurance` field must reference `isSelf` from the subject at the point where `claimsToIssuePerCustomer` is built. Because `claimsToIssuePerCustomer` is subject-agnostic (built before the subject loop), the final `levelOfAssurance` must be resolved per-entry after the subject is known.

Implementation: move `levelOfAssurance` out of `claimsToIssuePerCustomer` and set it per entry in the subject-crossing loop:

```js
claimsToIssue.push({
  ...entry,
  'recipientDid': subject.did,
  'isSelf': subject.isSelf || false,
  'levelOfAssurance': subject.isSelf ? 0 : 2
});
```

**Change 2 — Skip propagation for self-issued credentials:**

In the issuance loop:

```js
// Before
await propagate(cResponse.signed_token);

// After
if (!credentialData.isSelf) {
  await propagate(cResponse.signed_token);
}
```

### `webApps/wwc/src/pages/Catalog/Components/IssueModal.js`

Add a conditional `Alert` after the `SubjectList` component, shown when any currently-selected subject has `isSelf === true`.

### `webApps/wwc/public/locales/es/translation.json`

Add under `catalog`:
```json
"selfAssertedLoaNote": "Este atributo se emitirá como auto-alegado (LoA 0) y permanecerá en tu propia cartera."
```

### `webApps/wwc/public/locales/en/translation.json`

Add under `catalog`:
```json
"selfAssertedLoaNote": "This attribute will be self-asserted (LoA 0) and will remain in your own wallet."
```

---

## State & Data Flow

```
useSubjectManager
  → availableSubjects includes { did, businessName, tenant, isSelf: true } for own identity

SubjectList (IssueModal)
  → user selects Autoalegar → subject.value = { did, businessName, isSelf: true }

IssueModal.handleSubmit
  → selectedSubjectsList = subjects.filter(s => s.value).map(s => s.value)
  → issueData.subjects = [{ did, businessName, isSelf: true }, ...]

engine.createCredentialFromDocument(issueData, issuerKey, onError)
  → per subject: isSelf === true → levelOfAssurance = 0; isSelf spread into credentialData
  → sybolIssueCredential(credentialData) → cResponse
  → credentialData.isSelf === true → propagate() skipped
```

---

## Backend Impact

None. The backend schema already accepts `levelOfAssurance` values 0–4. No new routes, migrations, or service changes are required.

---

## Out of Scope

- Displaying LoA on the credential card in the wallet (separate issue)
- Multi-LoA selection for third-party issuance (separate issue)
- Validation that the issuerDid matches the recipientDid server-side (defensive backend work, separate issue)
- Self-issuance for presentation requests (already handled: propagation already skipped when `iss === sub`)
