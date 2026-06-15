# SybolComponents — Components Overview

## Propósito

Librería de componentes React reutilizables compartidos entre las aplicaciones web de la plataforma Sybol. Garantiza consistencia visual y de comportamiento entre `wwc` y `OnBoardingWeb`.

## Catálogo de componentes

### `Footer`

Pie de página estándar con branding Sybol.

```
Footer/
├── Footer.js       ← Componente React
├── Footer.css      ← Estilos
└── index.js        ← Export
```

**Props:** Ninguna (componente estático de presentación).

### `SybolButton`

Botón con variantes de estilo de la plataforma.

```
SybolButton/
├── SybolButton.js      ← Componente React
├── SybolButton.css     ← Estilos
└── index.js            ← Export
```

**Props:**
| Prop | Tipo | Descripción |
|---|---|---|
| `onClick` | function | Handler de click |
| `variant` | string | Variante visual (primary, secondary, ghost) |
| `disabled` | boolean | Estado deshabilitado |
| `children` | ReactNode | Contenido del botón |

## Uso en proyectos

```js
import Footer from '../SybolComponents/Footer';
import SybolButton from '../SybolComponents/SybolButton';

// Uso
<SybolButton variant="primary" onClick={handleAction}>
  Confirmar
</SybolButton>
<Footer />
```

## Convenciones

- Los componentes son importados directamente por path relativo (no hay publicación como npm package).
- Cada componente tiene su propio `index.js` como barrel export.
- Los estilos son CSS puro (sin CSS-in-JS).
