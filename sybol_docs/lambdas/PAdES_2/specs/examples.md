# PAdES PDF Signing Examples

This directory contains a complete example of PDF digital signing using PAdES (PDF Advanced Electronic Signatures) with EC (Elliptic Curve) and RSA certificates.

## File Structure

```
scripts/PAdES/
├── examples.js           # Main example file
├── test.pdf             # Input PDF file to sign
├── certs/               # Certificate directory
│   ├── cert.pem         # Certificate file
│   └── priv.pem         # Private key file
└── signedPDF/           # Output directory
    └── signed-document.pdf  # Signed output file
```

## Usage

### Run All Examples
```bash
cd scripts/PAdES
node examples.js
```

### Quick Signing Mode
```bash
# Sign with default paths
node examples.js --quick

# Sign with custom paths
node examples.js --quick --input=./my-document.pdf --output=./output/signed.pdf
```

## Features Demonstrated

### ✅ Complete Workflow
- Load certificates from `./certs/cert.pem` and `./certs/priv.pem`
- Load PDF from `./test.pdf`
- Add digital signature to first page at coordinates [100, 100, 300, 200]
- Save signed PDF to `./signedPDF/signed-document.pdf`

### ✅ Signature Features
- **EC (Elliptic Curve) signing** with P-256 curve
- **RSA signing** as fallback
- **Visible signature** on first page
- **PAdES-compliant** format
- **Incremental updates** to preserve PDF structure

### ✅ Adobe Reader Compatibility
- Uses proper PDF incremental updates
- Preserves original document structure
- Prevents font BBox corruption errors
- Maintains PDF/A compliance where applicable

## Example Output

```
🚀 Starting PAdES Digital Signature Examples...

=== Example 1: PDF Signing with Existing Certificate ===
🔐 Loading certificate from ./certs...
✅ Certificate and private key loaded successfully
📄 Loaded test PDF: 1598760 bytes
📋 Used EC signing algorithm (P-256 curve)
🎉 PDF signing completed successfully!
📊 Original size: 1598760 bytes
📊 Signed size: 1599419 bytes
📍 Signature placed on page 1 at coordinates [100, 100, 300, 200]
💾 Signed PDF saved to: ./signedPDF/signed-document.pdf
```

## Certificate Setup

The example expects certificate files in the `./certs/` directory:

```bash
# Create certificates (example - use your own certificates in production)
openssl genrsa -out certs/priv.pem 2048
openssl req -new -x509 -key certs/priv.pem -out certs/cert.pem -days 365
```

## Technical Details

### Signature Placement
- **Page**: 1 (first page)
- **Position**: [100, 100, 300, 200] (x1, y1, x2, y2)
- **Visible elements**: Date, reason, location, contact info

### Supported Algorithms
- **ECDSA-SHA256** (preferred, P-256 curve)
- **RSA-SHA256** (fallback)

### PDF Compatibility
- **PDF Version**: Maintains original version
- **Structure**: Uses incremental updates
- **Standards**: PAdES-B compliant
- **Readers**: Adobe Reader, Chrome PDF viewer, etc.

## Production Considerations

1. **Real Certificates**: Replace test certificates with production CA-issued certificates
2. **Timestamp Authority**: Add timestamp server for LTV (Long Term Validation)
3. **Certificate Chain**: Include full certificate chain
4. **Error Handling**: Add comprehensive error handling for production use
5. **Security**: Protect private keys with proper access controls

## Troubleshooting

### Common Issues

1. **Certificate not found**: Ensure `cert.pem` and `priv.pem` exist in `./certs/`
2. **PDF not found**: Ensure `test.pdf` exists in current directory
3. **Permission denied**: Check write permissions for `./signedPDF/` directory
4. **Adobe Reader errors**: Verify incremental updates are working correctly

### Error Messages

- `Certificate files not found`: Missing cert.pem or priv.pem
- `PDF cannot be signed`: Invalid or corrupted PDF input
- `Byte range exceeds PDF file size`: PDF structure issue (auto-handled)

## Integration

Use the exported functions in your own code:

```javascript
import { quickSignPDF, CertificateLoader } from './examples.js';

// Quick signing
await quickSignPDF('./my-document.pdf', './output/signed.pdf');

// Custom certificate loading
const certLoader = new CertificateLoader('./my-certs');
const cert = await certLoader.loadCertificate();
```