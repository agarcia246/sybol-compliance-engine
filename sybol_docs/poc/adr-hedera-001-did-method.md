# ADR-hedera-001: Seleccion del metodo DID para la POC de identidad descentralizada en Sybol

**Estado:** Aceptado
**Fecha:** 2026-03-30
**Autores:** Equipo Sybol
**Rama:** `feature/eddera-poc`

---

## Contexto

Sybol necesita integrar soporte nativo para identidades descentralizadas (DIDs) con capacidad de anclaje en una red publica distribuida, en el marco de su arquitectura de Verifiable Credentials W3C. La decision sobre el metodo DID determina la red subyacente, el modelo de anclaje, las librerias a utilizar, los costes operacionales y el grado de adopcion en el ecosistema.

Los criterios de evaluacion son:

1. **Conformidad W3C DID Core 1.0** — El metodo debe estar registrado o en proceso de registro en el W3C DID registry.
2. **Soporte JavaScript/Node.js** — Debe existir un SDK o libreria npm mantenida.
3. **Disponibilidad de testnet gratuita** — Para desarrollo y POC sin coste.
4. **Compatibilidad con infraestructura Sybol** — Integracion natural con AWS KMS y el servicio `businessLogic`.
5. **Costes operacionales en mainnet** — Viabilidad economica en produccion.
6. **Adopcion y mantenimiento** — Nivel de actividad en el ecosistema y garantia de longevidad.

---

## Opciones evaluadas

### Opcion 1 — did:hedera (Hedera Hashgraph)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado en W3C CCG; basado en W3C DID Core 1.0 |
| SDK JavaScript | `@hashgraph/did-sdk-js` en npm; `@hashgraph/sdk` oficial |
| Testnet gratuita | Si — Hedera testnet con faucet HBAR |
| Compatibilidad Sybol | Alta — Ed25519 soportado en AWS KMS (ECC_NIST_EDWARDS25519); no requiere EVM |
| Coste mainnet | Muy bajo — crear topic: ~$0.01; mensaje HCS: ~$0.0001 |
| Adopcion | Media-alta — Hedera es miembro W3C; Governing Council incluye empresas Fortune 500 |
| Modelo de anclaje | HCS (Hedera Consensus Service) — sin smart contracts |
| **Valoracion** | **Alta** |

### Opcion 2 — did:key (metodo local sin red)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado; ampliamente soportado |
| SDK JavaScript | `@digitalbazaar/did-method-key`; `@transmute/did-key.js` |
| Testnet gratuita | N/A — no requiere red |
| Compatibilidad Sybol | Muy alta — solo necesita generar un par de claves |
| Coste mainnet | Cero — no hay anclaje on-chain |
| Adopcion | Alta en contextos de prueba/offline |
| Modelo de anclaje | Ninguno — el DID deriva directamente de la clave publica |
| **Valoracion** | No apto — no demuestra anclaje en red distribuida (objetivo de la POC) |

### Opcion 3 — did:web (anclaje via HTTPS)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado; ampliamente soportado |
| SDK JavaScript | `web-did-resolver`; soporte nativo en `did-resolver` |
| Testnet gratuita | N/A — requiere dominio HTTPS propio |
| Compatibilidad Sybol | Alta — cualquier clave |
| Coste mainnet | Coste del dominio + hosting; sin costes de transaccion |
| Adopcion | Alta — adoptado por muchas empresas |
| Modelo de anclaje | Servidor HTTPS — centralizado, no blockchain |
| **Valoracion** | No apto — anclaje centralizado, no distribuido; no es el objetivo de la POC |

### Opcion 4 — did:ion (Bitcoin/ION)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado; proyecto de Microsoft/DIF |
| SDK JavaScript | `@decentralized-identity/ion-tools` |
| Testnet gratuita | Si — ION testnet sobre Bitcoin testnet |
| Compatibilidad Sybol | Media — secp256k1; complejidad de anclaje en Bitcoin |
| Coste mainnet | Variable — depende de Bitcoin fees; mas complejo |
| Adopcion | Media — asociado a Microsoft; uso principalmente en entorno Azure |
| Modelo de anclaje | SIDETREE sobre Bitcoin — complejo, latencia alta |
| **Valoracion** | Media — viable pero mayor complejidad operacional |

### Opcion 5 — did:ebsi (European Blockchain Services Infrastructure)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado; especificacion EBSI |
| SDK JavaScript | `@cef-ebsi/did-resolver`; herramientas de la Comision Europea |
| Testnet gratuita | Si — EBSI playground |
| Compatibilidad Sybol | Media — requiere DID registrado en blockchain EBSI permisionada |
| Coste mainnet | Acceso permisionado — requiere ser entidad reconocida por EBSI |
| Adopcion | Alta en contexto europeo / eIDAS 2.0 |
| Modelo de anclaje | Blockchain permisionada de la UE |
| **Valoracion** | Alta para contexto europeo, pero acceso restringido limita la POC |

### Opcion 6 — did:ala (Alastria — RED DESCARTADA)

| Criterio | Evaluacion |
|----------|-----------|
| Conformidad W3C | Registrado; especificacion Alastria |
| SDK JavaScript | `@alastria/alastria-identity-lib` |
| Testnet gratuita | Limitada — requiere acceso coordinado con Alastria |
| Compatibilidad Sybol | Alta — secp256k1 ya en uso; contratos EVM existentes en el repo |
| Coste mainnet | Permisionado — requiere ser miembro de Alastria |
| Adopcion | Baja fuera de Espana/Europa |
| Modelo de anclaje | Smart contracts EVM en red Alastria (Quorum/Besu) |
| **Valoracion** | No seleccionada — red correcta para la POC es Hedera Hashgraph |

---

## Tabla comparativa resumida

| Metodo | Anclaje distribuido | SDK JS | Testnet libre | KMS compatible | Coste mainnet | Adopcion global |
|--------|---------------------|--------|---------------|----------------|---------------|-----------------|
| did:hedera | Si (HCS) | Si | Si | Si (Ed25519 KMS) | Muy bajo | Media-alta |
| did:key | No | Si | N/A | Si | Cero | Alta (offline) |
| did:web | No (centralizado) | Si | N/A | Si | Bajo | Alta |
| did:ion | Si (Bitcoin) | Si | Si | Medio (secp256k1) | Variable | Media |
| did:ebsi | Si (permisionado) | Si | Si (limitado) | Si | Acceso restringido | Alta (UE) |
| did:ala | Si (EVM) | Si | Limitada | Si (secp256k1) | Permisionado | Baja |

---

## Decision

**Se selecciona `did:hedera` como metodo DID para la POC.**

### Justificacion

1. **Anclaje publico y distribuido real:** HCS provee ordering y timestamping con finality aBFT sin dependencia de smart contracts, lo que simplifica la implementacion y reduce la superficie de error.
2. **Testnet libre y accesible:** El portal de Hedera ofrece cuentas testnet con faucet HBAR. No requiere coordinacion con terceros ni membresia.
3. **Compatibilidad con AWS KMS:** AWS KMS soporta Ed25519 (`ECC_NIST_EDWARDS25519`), el tipo de clave canonico para did:hedera, sin necesidad de claves software.
4. **Costes extremadamente bajos:** Crear un topic cuesta ~$0.01 y cada mensaje HCS ~$0.0001. Viable incluso a escala.
5. **SDK JavaScript oficial:** `@hashgraph/sdk` y `@hashgraph/did-sdk-js` son paquetes mantenidos disponibles en npm.
6. **Miembro W3C:** Hedera es miembro del W3C desde 2020 y la especificacion did:hedera esta registrada y activa.

---

## Consecuencias

### Positivas
- Anclaje en una red publica global con finality garantizada.
- Modelo operacional simple: mensajes HCS, sin smart contracts.
- Costes de transaccion negligibles.
- Compatibilidad directa con la infraestructura AWS KMS de Sybol.

### Negativas / Compromisos
- Requiere cuenta Hedera con HBAR para pagar los fees (aunque sean minimos).
- El SDK `@hashgraph/did-sdk-js` puede estar menos actualizado que la especificacion actual; puede requerir implementacion parcial manual.
- La resolucion del DID requiere acceso al mirror node de Hedera (dependencia de disponibilidad).
- No hay un DID resolver universal HTTP listo para usar sin despliegue propio.

---

## Referencias

- [hashgraph/did-method — Especificacion oficial](https://github.com/hashgraph/did-method)
- [Meeco/hedera-did-method — Especificacion actualizada W3C DID Core 1.0](https://github.com/Meeco/hedera-did-method)
- [HIP-27](https://hips.hedera.com/hip/hip-27)
- [W3C DID Registry](https://www.w3.org/TR/did-spec-registries/)
- [Hedera — Decentralized Identity on HCS](https://hedera.com/blog/decentralized-identity-on-the-hedera-consensus-service/)
- `docs/poc/spec-hedera-did-poc.md` — Especificacion completa de la POC
