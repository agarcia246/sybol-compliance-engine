# PAdES Lambda — Architecture

## Propósito

Lambda para procesamiento de PDFs con firma **PAdES** (PDF Advanced Electronic Signatures). Implementa un sistema modular con principios SOLID para manipulación de metadatos PDF y creación de campos de formulario interactivos.

## Componentes

```
PAdES/src/
├── interfaces/     ← Contratos (IPDFProcessor) para DI y testabilidad
├── models/         ← PDFMetadata, PDFField (estructuras de datos con validación)
├── processors/
│   ├── PDFMetadataProcessor.js   ← Operaciones sobre metadatos PDF
│   ├── PDFFormProcessor.js       ← Creación y validación de campos de formulario
│   └── PDFDocumentProcessor.js   ← I/O de documentos PDF
├── services/
│   └── PDFService.js             ← Orquestación de alto nivel
└── factories/      ← Object creation patterns
```

## Flujo

```
Trigger (API Gateway / S3 event)
        ↓
  PDFService (orchestrator)
        ↓
  PDFMetadataProcessor + PDFFormProcessor + PDFDocumentProcessor
        ↓
  PDF firmado / procesado → S3 / respuesta
```

## Documentación relacionada

- [README](../README.md)
- [PAdES_2 (variante)](../../PAdES_2/README.md)
