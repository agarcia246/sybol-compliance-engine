# PAdES Digital Signature System

A comprehensive, modular digital signature system for PDF documents implementing PAdES (PDF Advanced Electronic Signatures) standards with support for both RSA and Elliptic Curve (P-256) cryptography.

## 🏗️ Architecture Overview

The system follows a clean architecture with separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                 PAdESSignatureOrchestrator              │
│                    (Workflow Manager)                   │
├─────────────────────────────────────────────────────────┤
│  PDFManager        │  PAdESEngineRSA   │  PAdESEngineEC  │
│  (PDF Operations)  │  (RSA Signatures) │  (EC Signatures)│
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **PDFManager** (`PDFManager.js`)
Handles all PDF-related operations:
- ✅ PDF parsing and structure analysis
- ✅ Byte range extraction for signature calculation
- ✅ Signature placement and insertion
- ✅ Document validation and metadata extraction
- ✅ Incremental updates for multiple signatures
- ✅ Cross-reference table management

#### 2. **PAdESEngineRSA** (`PAdESEngineRSA.js`)
RSA-specific signature generation:
- ✅ RSA key validation and configuration
- ✅ CAdES (CMS Advanced Electronic Signatures) generation
- ✅ RSA-PSS with SHA-256 signing
- ✅ PAdES-compliant authenticated attributes
- ✅ Signature policy encoding (PAdES-EPES)

#### 3. **PAdESEngineEC** (`PAdESEngineEC.js`)
Elliptic Curve (P-256) signature generation:
- ✅ P-256 curve validation and ECDSA operations
- ✅ EC-specific CAdES structures
- ✅ ECDSA-SHA256 signature algorithm
- ✅ ESSCertIDv2 for certificate references
- ✅ Elliptic curve parameter encoding

#### 4. **PAdESSignatureOrchestrator** (`PAdESSignatureOrchestrator.js`)
Complete workflow management:
- ✅ End-to-end signing workflows
- ✅ Engine coordination
- ✅ Error handling and validation
- ✅ Performance monitoring
- ✅ Multi-signature support

## 🚀 Quick Start

### Basic RSA Signing
```javascript
import PAdESSignatureOrchestrator from './scripts/PAdES/PAdESSignatureOrchestrator.js';

const orchestrator = new PAdESSignatureOrchestrator();

const result = await orchestrator.signPDFWithRSA(
  pdfArrayBuffer,
  rsaCertificatePEM,
  rsaPrivateKeyPEM,
  {
    reason: 'Document approval',
    location: 'Corporate Office',
    timestampUrl: 'http://timestamp.digicert.com'
  }
);

if (result.success) {
  // result.signedPDF contains the signed PDF
  console.log(`Signed with ${result.signatureInfo.algorithm}`);
}
```

### Basic EC (P-256) Signing
```javascript
const result = await orchestrator.signPDFWithEC(
  pdfArrayBuffer,
  ecCertificatePEM,  // P-256 certificate
  ecPrivateKeyPEM,   // P-256 private key
  {
    reason: 'ECDSA document approval',
    location: 'Digital Workspace'
  }
);

if (result.success) {
  console.log(`Signed with ${result.signatureInfo.algorithm} using ${result.signatureInfo.curve}`);
}
```

### Incremental Signatures
```javascript
// Add a second signature to an already signed PDF
const incrementalResult = await orchestrator.addIncrementalSignature(
  signedPdfBuffer,
  secondCertificatePEM,
  secondPrivateKeyPEM,
  'EC',  // or 'RSA'
  {
    reason: 'Counter-signature',
    location: 'Second approval level'
  }
);
```

## 📋 Certificate Management

The system uses existing certificates from files, providing a simple and secure approach to certificate management.

### Certificate Loading (Recommended)
```javascript
import { CertificateLoader } from './examples.js';

// Load certificates from directory
const certLoader = new CertificateLoader('./certificates');

// Check if certificate files exist
const filesExist = await certLoader.checkCertificateFiles();
if (!filesExist) {
  console.error('Certificate files not found in ./certificates/');
  return;
}

// Load certificate and private key
const cert = await certLoader.loadCertificate();

// Get certificate information
const info = certLoader.getCertificateInfo();
console.log('Certificate Info:', info);

// Use certificates for signing
const result = await orchestrator.signPDFWithRSA(
  pdfData, 
  cert.certificate, 
  cert.privateKey, 
  options
);
```

### Certificate Directory Structure
```
./certificates/
├── cert.pem    # X.509 certificate in PEM format
└── priv.pem    # Private key in PEM format (RSA or EC)
```

### Manual OpenSSL Commands (Alternative)

#### RSA Certificate (4096-bit)
```bash
# Generate RSA private key (4096-bit)
openssl genrsa -out rsa-private.key 4096

# Generate certificate signing request
openssl req -new -key rsa-private.key -out rsa.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=RSA Signer"

# Generate self-signed certificate (valid for 1 year)
openssl x509 -req -in rsa.csr -signkey rsa-private.key \
  -out rsa-cert.pem -days 365 -sha256
```

#### Elliptic Curve Certificate (P-256)
```bash
# Generate EC private key using P-256 curve
openssl ecparam -genkey -name prime256v1 -out ec-private.key

# Generate certificate signing request
openssl req -new -key ec-private.key -out ec.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=EC Signer"

# Generate self-signed certificate
openssl x509 -req -in ec.csr -signkey ec-private.key \
  -out ec-cert.pem -days 365 -sha256
```

### Test Certificate Generation
```bash
# Run the test script to generate and test certificates
node scripts/PAdES/test-certificate-generation.js

# This will create:
# - ./test-certificates/rsa-cert.pem
# - ./test-certificates/rsa-private.key
# - ./test-certificates/ec-cert.pem
# - ./test-certificates/ec-private.key
```

## 🔧 API Reference

### PDFManager Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `loadPDF(pdfData)` | Load and parse PDF document | `{success, documentInfo, pageCount, hasSignatures}` |
| `extractBytesForSignature(byteRange)` | Extract bytes for signature calculation | `Uint8Array` |
| `calculateSignatureByteRange(signatureLength)` | Calculate optimal byte range | `{byteRange, insertionPoint, reservedSpace}` |
| `addSignatureToPDF(signatureHex, signatureDict, placement)` | Add signature to PDF | `Uint8Array` (modified PDF) |
| `validatePDFForSigning()` | Validate PDF compatibility | `{isValid, warnings, errors, recommendations}` |
| `createIncrementalUpdate(signatureHex, signatureDict)` | Create incremental update | `Uint8Array` |

### PAdESEngine Methods (RSA & EC)

| Method | Description | Returns |
|--------|-------------|---------|
| `configureSigningEnvironment(certPem, keyPem, options)` | Configure signing | `{success, certificateSubject, keyType, keySize}` |
| `buildCAdESSignature(content, signingTime)` | Generate CAdES signature | `string` (DER encoded) |
| `buildAuthenticatedAttributes(content, signingTime)` | Build PAdES attributes | `Array` |
| `applyPAdESSignature(content, options)` | Complete signature process | `{signatureBytes, signatureDict, byteRange}` |

### PAdESSignatureOrchestrator Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `signPDFWithRSA(pdfData, certPem, keyPem, options)` | Complete RSA workflow | `{success, signedPDF, signatureInfo}` |
| `signPDFWithEC(pdfData, certPem, keyPem, options)` | Complete EC workflow | `{success, signedPDF, signatureInfo}` |
| `addIncrementalSignature(signedPdf, certPem, keyPem, type, options)` | Add additional signature | `{success, signedPDF, signatureInfo}` |
| `verifyPDFSignatures(pdfData)` | Verify existing signatures | `{success, hasSignatures, signatures}` |
| `analyzePDFDocument(pdfData)` | Analyze document | `{success, analysis}` |

## 🔐 Signature Standards Compliance

### PAdES (PDF Advanced Electronic Signatures)
- ✅ **PAdES-BES**: Basic Electronic Signature
- ✅ **PAdES-EPES**: Explicit Policy-based Electronic Signature
- ✅ **ETSI EN 319 142**: PAdES digital signature formats
- ✅ **ISO 32000-2**: PDF 2.0 specification compliance

### CAdES (CMS Advanced Electronic Signatures)
- ✅ **ETSI EN 319 122**: CAdES digital signature formats
- ✅ **RFC 5652**: Cryptographic Message Syntax (CMS)
- ✅ **PKCS#7**: Cryptographic Message Syntax Standard

### Cryptographic Algorithms
- ✅ **RSA**: RSA-PSS with SHA-256 (recommended key size: 2048-4096 bits)
- ✅ **ECDSA**: P-256 curve with SHA-256 (secp256r1)
- ✅ **Hash**: SHA-256 for all digest operations
- ✅ **Certificate Hash**: ESSCertID (SHA-1) and ESSCertIDv2 (SHA-256)

## 🌐 Integration Examples

### Browser Integration
```javascript
// File input handler
document.getElementById('pdfFile').addEventListener('change', async (event) => {
  const file = event.target.files[0];
  const arrayBuffer = await file.arrayBuffer();
  
  const orchestrator = new PAdESSignatureOrchestrator();
  const result = await orchestrator.signPDFWithRSA(arrayBuffer, certPem, keyPem);
  
  if (result.success) {
    // Trigger download
    const blob = new Blob([result.signedPDF], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'signed-document.pdf';
    a.click();
    URL.revokeObjectURL(url);
  }
});
```

### Node.js Server Integration
```javascript
// Express.js route
app.post('/api/sign-pdf', upload.single('pdf'), async (req, res) => {
  const orchestrator = new PAdESSignatureOrchestrator();
  
  const result = await orchestrator.signPDFWithRSA(
    req.file.buffer,
    process.env.CERT_PEM,
    process.env.KEY_PEM,
    {
      reason: req.body.reason,
      location: req.body.location,
      timestampUrl: process.env.TIMESTAMP_URL
    }
  );
  
  if (result.success) {
    res.setHeader('Content-Type', 'application/pdf');
    res.send(Buffer.from(result.signedPDF));
  } else {
    res.status(500).json({ error: result.error });
  }
});
```

## 📊 Performance Characteristics

### Signature Sizes
- **RSA (2048-bit)**: ~512 bytes signature + ~2KB CAdES overhead
- **RSA (4096-bit)**: ~1024 bytes signature + ~2KB CAdES overhead
- **EC (P-256)**: ~64-72 bytes signature + ~1.5KB CAdES overhead

### Processing Speed (approximate)
- **RSA Signing**: 50-200ms depending on key size
- **EC Signing**: 10-50ms (faster than RSA)
- **PDF Processing**: 10-100ms depending on document size
- **Incremental Updates**: 5-20ms additional overhead

## 🔍 Validation and Verification

The system provides comprehensive validation:

### PDF Document Validation
- PDF version compatibility (1.4+)
- Document encryption status
- Existing signature detection
- Permission restrictions
- File integrity checks

### Certificate Validation
- Certificate format verification
- Key type and size validation
- Certificate chain validation (if provided)
- Expiration date checks
- Certificate usage restrictions

### Signature Validation
- CAdES structure compliance
- Authenticated attributes verification
- Hash algorithm validation
- Signature policy compliance
- Byte range integrity

## 🚨 Security Considerations

### Private Key Protection
- **Never log or store private keys in plain text**
- Use Hardware Security Modules (HSMs) in production
- Implement proper key lifecycle management
- Use secure random number generation

### Certificate Management
- Validate certificate chains to trusted roots
- Check certificate revocation status (CRL/OCSP)
- Implement certificate expiration monitoring
- Use appropriate key usage extensions

### PDF Security
- Validate PDF structure before processing
- Sanitize PDF content to prevent malicious code
- Implement file size limits
- Use secure temporary storage

## 🧪 Testing

### Unit Tests
```bash
# Test individual components
npm test -- --grep "PDFManager"
npm test -- --grep "PAdESEngineRSA"
npm test -- --grep "PAdESEngineEC"
```

### Integration Tests
```bash
# Test complete workflows
npm test -- --grep "SignatureOrchestrator"
npm test -- --grep "EndToEnd"
```

### Compliance Tests
```bash
# Test PAdES compliance
npm test -- --grep "PAdES"
npm test -- --grep "CAdES"
```

## 📖 Examples

See `examples.js` for comprehensive usage examples including:
- Basic RSA and EC signing
- Incremental signatures
- Batch processing
- Browser integration
- Server-side implementation
- Error handling patterns

## 🤝 Contributing

1. Follow the established architecture patterns
2. Maintain separation of concerns
3. Add comprehensive tests for new features
4. Update documentation for API changes
5. Ensure PAdES compliance for signature features

## 📄 License

This digital signature system is provided for educational and development purposes. Ensure compliance with local regulations for digital signature implementations.

## 🔗 Related Standards

- [ETSI EN 319 142-1](https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.01.01_60/en_31914201v010101p.pdf) - PAdES digital signatures
- [ETSI EN 319 122-1](https://www.etsi.org/deliver/etsi_en/319100_319199/31912201/01.01.01_60/en_31912201v010101p.pdf) - CAdES digital signatures
- [RFC 3852](https://tools.ietf.org/html/rfc3852) - Cryptographic Message Syntax (CMS)
- [ISO 32000-2](https://www.iso.org/standard/63534.html) - PDF 2.0 specification
- [FIPS 186-4](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf) - Digital Signature Standard