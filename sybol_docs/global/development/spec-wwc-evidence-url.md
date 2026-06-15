# SPEC: Añadir evidencia a credenciales (WWC — Mi Identidad)

**Feature:** Evidence URL v0 — frontend
**Service:** `webApps/wwc`
**Issue:** [#8 — Gestor documental con acceso privado](https://github.com/Sybolid/sybolRelases/issues/8)
**Backend spec:** [ADR-0006](../decisions/0006-evidence-url-external-document-reference.md)
**Status:** Ready to implement

---

## User Story

> Como **holder**, quiero poder añadir un enlace de evidencia a una credencial desde el panel Mi Identidad, para poder referenciar el documento externo que respalda esa credencial sin salir de la plataforma.

---

## User Flow

```
Mi Identidad (/holder/credentials)
  └── Lista de credenciales
        └── Click en una fila → InfoDrawer se abre
              └── Botón "Añadir evidencia" (abajo, junto a Present/Delegate)
                    └── EvidenceModal se abre
                          ├── Campo URL + botón Guardar
                          │     └── POST /api/bo/credentials/{jti}  { evidence_url }
                          │           ├── ✅ Success → alerta verde + drawer muestra URL como enlace
                          │           └── ❌ Error  → alerta roja
                          └── Botón Cancelar → cierra modal sin cambios
```

---

## UI/UX

### Botón en el InfoDrawer

Añadir un botón **"Añadir evidencia"** (o "Ver evidencia" si ya existe `evidence_url`) en la sección de acciones del `InfoDrawer`, entre los botones existentes (Present/Delegate) y el botón Revocar.

**Comportamiento:**
- Solo se muestra si `selectedForInfo.ioType === 'VerifiableCredential'`
- Si `evidence_url` ya existe → botón muestra "Ver / Editar evidencia" con icono de enlace externo
- Si no existe → botón muestra "Añadir evidencia" con icono `AddLink`

```
[ Responder ]  [ Reenviar ]
[ Añadir evidencia ]
[ Revocar (disabled) ]
```

### EvidenceModal

Modal centrado (MUI `Dialog`), patrón idéntico a `PresentationModal`.

```
┌─────────────────────────────────────────┐
│  Evidencia del documento                 │
│  ─────────────────────────────────────  │
│  Enlace al documento de evidencia        │
│                                          │
│  [ https://drive.google.com/...       ] │
│                                          │
│  ⓘ El acceso al documento es gestionado │
│     por el sistema externo.              │
│                                          │
│              [ Cancelar ] [ Guardar ]   │
└─────────────────────────────────────────┘
```

**Validación del campo URL:**
- No puede estar vacío al guardar
- Debe ser una URL válida (`/^https?:\/\/.+/`)
- Longitud máxima: 2048 caracteres
- Permitir `null` / campo vacío para limpiar la evidencia

### Sección en el InfoDrawer (cuando ya hay URL)

Si `evidence_url` está presente, mostrarla como enlace en el cuerpo del drawer (antes de la sección de botones):

```
Evidencia
  🔗 Ver documento →  [enlace externo]
```

---

## Files to Create

### `EvidenceModal.js`
**Path:** `src/pages/Holder/Components/EvidenceModal.js`
**Pattern:** `PresentationModal.js`

```jsx
// Props:
// - open: boolean
// - onClose: () => void
// - onSave: (url: string | null) => Promise<void>
// - currentUrl: string | null  (pre-fills the field)
// - t: TFunction
// - loading: boolean

const EvidenceModal = ({ open, onClose, onSave, currentUrl, t, loading }) => { ... }
```

**Internals:**
- MUI `Dialog` (not `Modal`) for accessibility
- `TextField` controlled with `useState(currentUrl || '')`
- URL validation on submit (inline error message below field)
- `SybolButton variant="dark"` for Guardar, `variant="outlined-green"` for Cancelar
- Disable Guardar while `loading`

---

## Files to Modify

### 1. `InfoDrawer.js`
**Path:** `src/components/InfoDrawer/InfoDrawer.js`

**Changes:**
- Add prop `onAddEvidence: Function | undefined`
- Render `EvidenceSection` in `renderItem()` when `evidence_url` is present
- Add "Añadir / Editar evidencia" button in `#info-drawer-pr-buttons`, visible only for `VerifiableCredential`

```jsx
// New prop
const onAddEvidence = props.onAddEvidence || null;

// In renderItem(), after CompliancePathSection:
{selectedForInfo.evidence_url && (
  <EvidenceSection evidenceUrl={selectedForInfo.evidence_url} t={t} />
)}

// In #info-drawer-pr-buttons, before onRevoke:
{onAddEvidence && selectedForInfo.ioType === 'VerifiableCredential' && (
  <Box className="info-drawer-present-section">
    <SybolButton
      variant="outlined-green"
      onClick={onAddEvidence}
      className="info-drawer-present-button"
      startIcon={selectedForInfo.evidence_url ? <LinkIcon /> : <AddLinkIcon />}
    >
      {selectedForInfo.evidence_url
        ? t('info.editEvidence')
        : t('info.addEvidence')}
    </SybolButton>
  </Box>
)}
```

**New MUI icon imports:** `AddLink`, `Link` from `@mui/icons-material`

---

### 2. `EvidenceSection.js` (new sub-component)
**Path:** `src/components/InfoDrawer/components/EvidenceSection.js`
**Pattern:** `CompliancePathSection.js`

Renders the existing `evidence_url` as a clickable external link inside the drawer body.

```jsx
const EvidenceSection = ({ evidenceUrl, t }) => (
  <Box className="item-section">
    <Typography variant="subtitle2" color="sybol.darkGreen" className="item-subtitle">
      {t('info.evidence')}
    </Typography>
    <Box className="item-subsection">
      <Link href={evidenceUrl} target="_blank" rel="noopener noreferrer">
        {t('info.viewDocument')}
      </Link>
    </Box>
  </Box>
);
```

---

### 3. `CredentialsContent.js`
**Path:** `src/pages/Holder/Components/CredentialsContent.js`

**Changes:**
- Add `evidenceModalOpen` state (`useState(false)`)
- Add `evidenceLoading` state (`useState(false)`)
- Add `handleAddEvidence()` → opens modal
- Add `handleSaveEvidence(url)` → calls API, closes modal on success, shows alert
- Pass `onAddEvidence={handleAddEvidence}` to `<InfoDrawer>`
- Render `<EvidenceModal>` with controlled state
- After successful save, refresh the selected credential to update `evidence_url` in the drawer

```jsx
const [evidenceModalOpen, setEvidenceModalOpen] = useState(false);
const [evidenceLoading, setEvidenceLoading] = useState(false);

const handleAddEvidence = () => setEvidenceModalOpen(true);

const handleSaveEvidence = async (url) => {
  setEvidenceLoading(true);
  try {
    await updateCredentialEvidenceUrl(selectedCredential.jti, url);
    setSelectedCredential(prev => ({ ...prev, evidence_url: url }));
    setEvidenceModalOpen(false);
    addAlert({ type: 'success', message: t('holder.credentials.evidenceSaved') });
  } catch (err) {
    addAlert({ type: 'error', message: t('holder.credentials.evidenceError') });
  } finally {
    setEvidenceLoading(false);
  }
};
```

---

### 4. `engine.js`
**Path:** `src/pages/Holder/engine.js`

**Add function:**
```javascript
export const updateCredentialEvidenceUrl = async (jti, evidenceUrl) => {
  const response = await sybolPost(`/api/bo/credentials/${jti}`, {
    evidence_url: evidenceUrl || null
  });
  return response.data;
};
```

---

### 5. `sybol.js` (service)
**Path:** `src/services/sybol.js`

If `sybolPost` is not a general helper, ensure `POST /api/bo/credentials/:id` is reachable via the existing axios instance. No new service file needed — use the existing wrapper.

---

## i18n Keys

### `public/locales/es/translation.json`

```json
"info": {
  "...existing keys...",
  "evidence": "Evidencia",
  "addEvidence": "Añadir evidencia",
  "editEvidence": "Editar evidencia",
  "viewDocument": "Ver documento externo →",
  "evidenceHelperText": "El acceso al documento es gestionado por el sistema externo (Google Drive, SharePoint, etc.)."
},
"holder": {
  "credentials": {
    "...existing keys...",
    "evidenceSaved": "Evidencia guardada correctamente.",
    "evidenceError": "Error al guardar la evidencia. Inténtalo de nuevo."
  }
}
```

### `public/locales/en/translation.json`

```json
"info": {
  "evidence": "Evidence",
  "addEvidence": "Add evidence",
  "editEvidence": "Edit evidence",
  "viewDocument": "View external document →",
  "evidenceHelperText": "Access to the document is managed by the external system (Google Drive, SharePoint, etc.)."
},
"holder": {
  "credentials": {
    "evidenceSaved": "Evidence saved successfully.",
    "evidenceError": "Failed to save evidence. Please try again."
  }
}
```

---

## State & Data Flow

```
CredentialsContent
  ├── selectedCredential (state) ← includes evidence_url from API
  ├── evidenceModalOpen (state)
  ├── evidenceLoading (state)
  │
  ├── <InfoDrawer
  │     item={selectedCredential}          ← evidence_url rendered in EvidenceSection
  │     onAddEvidence={handleAddEvidence}  ← opens modal
  │   />
  │
  └── <EvidenceModal
        open={evidenceModalOpen}
        currentUrl={selectedCredential?.evidence_url}
        onSave={handleSaveEvidence}        ← calls API + updates selectedCredential
        loading={evidenceLoading}
      />
```

---

## API Contract

```http
POST /api/bo/credentials/{jti}
Authorization: Bearer <access_token>
x-id-token: <id_token>
Content-Type: application/json

{ "evidence_url": "https://drive.google.com/file/d/1ABC..." }
```

Response includes the updated credential object with `evidence_url` at top level.

> ℹ️ The backoffice service (`/api/bo/`) proxies to businessLogic — confirm the proxy route exists for `POST /credentials/:id` before implementing. If not, the route needs to be added in `services/backoffice`.

---

## Out of Scope (v0)

- Showing `evidence_url` in the credentials table (list view) — only in the drawer
- Multiple evidence URLs per credential
- File upload (only URL input)
- Access control or authentication for the external document
- Evidence URL on presentation requests or presentations (only on `VerifiableCredential`)

---

## Dependencies

- Backend: `POST /api/bo/credentials/:id` must accept and persist `evidence_url` (see ADR-0006 — pending implementation in `services/businessLogic`)
- No new npm packages required
