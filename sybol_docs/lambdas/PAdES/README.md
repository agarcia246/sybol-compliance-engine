# PDF Metadata and Form Processing Module

A modular PDF processing system implementing SOLID principles for metadata manipulation and interactive form field creation.

## Architecture

The system follows a layered architecture with clear separation of concerns:

```text
src/
├── interfaces/          # Contract definitions
├── models/             # Data structures
├── processors/         # Core processing logic
├── services/          # Business orchestration
└── factories/         # Object creation patterns
```

### Core Components

#### Interfaces (`IPDFProcessor.js`)

- Define contracts for metadata, form, and document operations
- Enable dependency injection and testability

#### Models (`PDFModels.js`)

- `PDFMetadata`: Encapsulates document metadata with validation
- `PDFField`: Represents form field configuration with type safety

#### Processors

- `PDFMetadataProcessor`: Handles metadata operations (basic + custom properties)
- `PDFFormProcessor`: Manages form field creation and validation
- `PDFDocumentProcessor`: Handles document I/O operations

#### Service Layer (`PDFService.js`)

- Orchestrates processors without implementation dependencies
- Provides high-level API for document processing operations

#### Factories (`PDFFactories.js`)

- `PDFFieldFactory`: Creates form field configurations
- `PDFMetadataFactory`: Generates metadata templates

## Functionality

### Metadata Processing

- Standard PDF metadata (title, author, subject, keywords)
- Custom properties visible in Adobe Reader Properties dialog
- Extraction and validation of existing metadata

### Form Field Creation

- Text fields with validation options
- Checkboxes with state management
- Dropdown menus with option configuration
- Form validation and data export

### Document Operations

- Load from file path or Buffer
- Save to file or return as Buffer
- Create new documents with predefined layouts
- AWS Lambda compatible processing

## API Reference

### PDFProcessor

Main entry point for all operations:

```javascript
import { PDFProcessor } from './index.js';

const processor = new PDFProcessor();

// Process existing PDF
await processor.processExistingPDF(input, config);

// Create new PDF
await processor.createNewPDF(config);

// Extract metadata
await processor.extractMetadata(input);

// Validate form fields
await processor.validateForm(input);
```

### Configuration Structure

```javascript
const config = {
    metadata: {
        title: 'Document Title',
        author: 'Author Name',
        customProperties: {
            Department: 'Value',
            Project_ID: 'Value'
        }
    },
    fields: [
        {
            type: 'text|checkbox|dropdown',
            name: 'field_identifier',
            position: { x: number, y: number },
            size: { width: number, height: number },
            options: { /* type-specific options */ }
        }
    ],
    outputPath: './output.pdf' // Optional
};
```

### Factory Methods

```javascript
import { PDFFieldFactory, PDFMetadataFactory } from './index.js';

// Create field sets
const personalFields = PDFFieldFactory.createPersonalInfoFields();
const signatureFields = PDFFieldFactory.createSignatureFields();
const consentFields = PDFFieldFactory.createConsentFields();

// Create metadata templates
const contractMeta = PDFMetadataFactory.createContractMetadata(title, dept, id);
const formMeta = PDFMetadataFactory.createFormMetadata(title, dept);
const certMeta = PDFMetadataFactory.createCertificateMetadata(title, authority);
```

## Implementation Details

### SOLID Principles Applied

- **Single Responsibility**: Each class handles one aspect of PDF processing
- **Open/Closed**: Extensible through factories without modifying existing code
- **Liskov Substitution**: Processors implement clear interfaces
- **Interface Segregation**: Focused interfaces for specific operations
- **Dependency Inversion**: Service layer depends on abstractions

### Error Handling

The system implements structured error handling with specific error types and messages. All operations validate inputs and provide meaningful feedback for debugging.

### Custom Properties

Custom metadata properties are written to the PDF Info dictionary and are visible in Adobe Reader under File > Properties > Custom tab. The implementation handles encoding and ensures compatibility across PDF readers.

## Usage Example

```javascript
import { PDFProcessor, PDFFieldFactory, PDFMetadataFactory } from './index.js';

const processor = new PDFProcessor();

const result = await processor.createNewPDF({
    metadata: PDFMetadataFactory.createContractMetadata('Service Agreement'),
    fields: [
        PDFFieldFactory.createTextField('client_name', 100, 700, 300, 25, { required: true }),
        PDFFieldFactory.createCheckBox('terms_accepted', 100, 650, 15, { required: true }),
        PDFFieldFactory.createDropdown('service_type', 100, 600, 200, 25, [
            'Consulting', 'Development', 'Support'
        ])
    ],
    outputPath: './contract.pdf'
});
```

## AWS Lambda Integration

```javascript
export async function handler(event) {
    const processor = new PDFProcessor();
    const result = await processor.processExistingPDF(
        Buffer.from(event.inputPdfBase64, 'base64'),
        { metadata: event.metadata, fields: event.fields }
    );
    
    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/pdf' },
        body: result.toString('base64'),
        isBase64Encoded: true
    };
}
```

## Dependencies

The module requires `pdf-lib` for PDF manipulation operations. All other functionality is implemented without external dependencies.
