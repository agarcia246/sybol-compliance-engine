# src/credentials/ — Darius

Your job here is to take the unsigned VC payload from Javier and submit
it to Sybol's businessLogic API to get back a fully signed Verifiable Credential.

Before you can implement this, you need three things from Iñigo.
You are the one who reaches out to him for these — contact him directly:

1. The issuer DID value for Sybol
2. Confirmation that MEDIA_COMPLIANCE_CREDENTIAL is registered
   in the Sybol catalog schema
3. Whether the signing endpoint is /credentials/issue or a
   dedicated signing endpoint

Contact Iñigo at: inigo@sybol.id
Copy Javier on any technical questions so he stays in the loop.

While you are waiting for the above, scaffold the API call with
placeholder values so the structure is ready to plug in the moment
Iñigo confirms. The function signature, request format, error handling,
and response parsing should all be done — just swap in the real values.

Also make sure errors are surfaced clearly to the team.
If the Sybol API returns unexpected responses or schema mismatches,
log them in detail and flag in the WhatsApp group immediately.
