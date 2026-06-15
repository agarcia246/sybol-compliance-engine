# Ethereum Signature Verification Scripts

This directory contains scripts for signing Ethereum transactions with AWS KMS and verifying signatures using ethers.js ecrecover functionality.

## Files

### `index.mjs`

- Main Lambda function for signing transactions with AWS KMS
- Handles transaction encoding, hashing, and KMS signing

### `verifySignature.mjs`

- Core signature verification functions using ethers.js
- Supports personal message and transaction signature verification
- Uses `ethers.utils.recoverAddress()` for ecrecover functionality

### `kmsEthereumUtils.mjs`

- Utility functions for KMS-Ethereum integration
- Address derivation from public keys
- Signature format conversion helpers

### `testVerification.mjs`

- Comprehensive test suite for signature verification
- Creates test signatures and verifies them
- Demonstrates proper usage of verification functions

## Usage

### Running Tests

```bash
# Run the verification tests
node testVerification.mjs

# Run the basic verification examples
node verifySignature.mjs

# Run KMS utility tests
node kmsEthereumUtils.mjs
```

### Verifying a Personal Message Signature

```javascript
import { verifyPersonalMessage } from './verifySignature.mjs';

const message = "Hello, Ethereum!";
const signature = "0x1234567890abcdef..."; // Your signature
const signerAddress = "0xabcdef1234567890..."; // Expected signer

const isValid = verifyPersonalMessage(message, signature, signerAddress);
console.log(`Signature is ${isValid ? 'valid' : 'invalid'}`);
```

### Verifying a Transaction Signature

```javascript
import { verifyTransactionSignature } from './verifySignature.mjs';

const transaction = {
  to: "0x742d35Cc6634C0532925a3b8D9C9D5B7A5e3Bf1e",
  value: "1000000000000000000", // 1 ETH in wei
  nonce: 0,
  gasLimit: "21000",
  gasPrice: "20000000000", // 20 gwei
  chainId: 1
};

const signature = "0x1234567890abcdef..."; // Your signature
const signerAddress = "0xabcdef1234567890..."; // Expected signer

const isValid = verifyTransactionSignature(transaction, signature, signerAddress);
console.log(`Transaction signature is ${isValid ? 'valid' : 'invalid'}`);
```

### Raw Hash Verification

```javascript
import { verifySignature } from './verifySignature.mjs';

const messageHash = "0x1234567890abcdef..."; // Keccak256 hash
const signature = "0xabcdef1234567890..."; // Your signature
const signerAddress = "0x1234567890abcdef..."; // Expected signer

const isValid = verifySignature(messageHash, signature, signerAddress);
console.log(`Signature is ${isValid ? 'valid' : 'invalid'}`);
```

## Signature Formats

The verification functions support both hex and base64 signature formats:

- **Hex format**: `0x1234567890abcdef...`
- **Base64 format**: `MTIzNDU2Nzg5MGFiY2RlZi4uLg==`

The functions will automatically detect and convert between formats.

## Integration with KMS

To integrate with your existing KMS signing workflow:

1. Use your existing `signMessage()` function to get the KMS signature
2. Convert the DER-encoded KMS signature to Ethereum format (see `kmsEthereumUtils.mjs`)
3. Use the verification functions to validate the signature

```javascript
import { signMessage } from './index.mjs';
import { convertKMSSignatureToEthereum } from './kmsEthereumUtils.mjs';
import { verifySignature } from './verifySignature.mjs';

// Example integration
const kmsSignature = await signMessage(keyId, messageHash, "DIGEST", "ECC_SECG_P256K1");
const ethSignature = convertKMSSignatureToEthereum(kmsSignature, messageHash, publicKey);
const isValid = verifySignature(messageHash, ethSignature, expectedAddress);
```

## Notes

- **KMS Signature Format**: AWS KMS returns DER-encoded signatures that need to be converted to Ethereum's r,s,v format
- **Recovery ID**: Ethereum signatures include a recovery ID (v) that helps determine which of the possible public keys was used
- **Message Hashing**: Personal messages are hashed using `ethers.utils.hashMessage()` which adds Ethereum's message prefix
- **Transaction Hashing**: Transactions are serialized and hashed using `ethers.utils.keccak256()`

## Error Handling

All verification functions include proper error handling and will return `false` for invalid signatures rather than throwing errors. Check the console output for detailed error messages.

## Dependencies

- `ethers`: For Ethereum utilities and signature verification
- `@aws-sdk/client-kms`: For KMS integration (in main.js)
- `buffer`: For binary data handling

## Testing

The test suite creates random wallets, signs test messages and transactions, then verifies the signatures to ensure the verification functions work correctly. This provides confidence that the ecrecover functionality is working properly.
