# SYBOL – Documento técnico funcional



---

## Página 1


DOCUMENTO TÉCNICO-FUNCIONAL  DE PRODUCTO   
 
 
Building trust in the corporate world


---

## Página 2


Documento Técnico 
 
 2 
CONTROL DE VERSIONES  
  
Realizado por: Revisado por: Iñigo García CTO Raúl López CEO Firma Firma   Número de páginas: 38    Descripción:   Este documento incluye la descripción técnica de la plataforma Sybol, incluyendo todos los componentes y la arquitectura Lista de Distribución:  SYBOL – Equipo fundador Otros – Según valoración del equipo. Lista de distribución restringida  Control de versiones  Versión Fecha Sección modificada Cambios realizados 1 30/06/25 - Versión inicial


---

## Página 3


Documento Técnico 
 
 3 
INDICE  1 INTRODUCCIÓN 5 1.1 ¿Qué es Sybol? 5 1.2 Objetivos 5 1.3 Público objetivo 5 1.4 Estado actual 5 2 CRITERIOS DE DISEÑO 6 2.1 Identidad digital y conﬁanza empresarial 6 2.2 Intercambio estructurado y reutilizable de información 6 2.3 Trazabilidad, seguridad y auditoría 6 2.4 Arquitectura modular orientada a la integración 6 2.5 Funcionalidad de Sybol 7 3 DISEÑO DEL SISTEMA 8 3.1 Arquitectura lógica 8 3.2 Arquitectura física 11 3.3 Tecnologías utilizadas 12 3.4 Flujos de datos 13 3.5 Flujos de estado 15 3.6 Lógica Estados 15 4 PROTOCOLO DE IDENTIDAD 17 4.1 Punto de partida 18 4.2 Creación de Identidad 19 4.3 Documento DID 20 4.4 DID Resolve 24 4.5 Validación de estado 25 4.6 Credentials 25 4.7 Presentation 26 4.8 Presentation Request 26 5 SEGURIDAD Y BUENAS PRÁCTICAS 26 5.1 Protección de claves privadas 26


---

## Página 4


Documento Técnico 
 
 4 
5.2 Activación del segundo factor de autenticación (2FA) 27 5.3 Actualizaciones regulares 27 5.4 Auditoría de actividad 27 5.5 Gestión del ciclo de vida del material criptográﬁco 27 6 CASOS DE USO DEL PRODUCTO 28 6.1 Veriﬁcación de información de proveedores contratistas, empleados y equipamientos para la Coordinación de Actividades empresariales (CAE) 28 6.2 Emisión de credenciales veriﬁcables. Caso de uso de Distintivos de Origen Renovable (DOR) para clientes de suministros energéticos 28 6.3 Gestión de identidades y credenciales de empleados 29 7 PRUEBAS 30 7.1 Objetivos perseguidos 30 7.2 Tipología de pruebas 30 7.3 Herramientas y Automatización 31 7.4 Gestión de entornos de prueba 31 8 DEVOPS 31 8.1 Entornos disponibles 31 8.2 Pipelines CI/CD 32 8.3 Monitorización y logs 33 8.4 Monitorización 34 9 PREGUNTAS FRECUENTES (FAQ) 35


---

## Página 5


Documento Técnico 
 
 5 
1 INTRODUCCIÓN  1.1 ¿Qué es Sybol?  Sybol es una solución Web3 orientada a empresas que permite compartir, veriﬁcar y reutilizar información empresarial de forma segura, trazable y estandarizada. A través del uso de identidad digital y tecnologías descentralizadas como blockchain, Sybol introduce un nuevo paradigma en la gestión documental, facilitando la interoperabilidad entre organizaciones y reduciendo la carga operativa asociada a procesos burocráticos.  Como solución SaaS con arquitectura basada en API, Sybol ofrece una interfaz web inicial para la gestión de credenciales y ﬂujos documentales, permitiendo a los usuarios integrar fácilmente sus operaciones con sistemas externos.  
1.2 Objetivos  El objetivo de Sybol es eliminar redundancias y fricciones en el intercambio de información entre departamentos y empresas, proporcionando una infraestructura de conﬁanza para el onboarding digital, la veriﬁcación documental y el cumplimiento normativo. Además, busca ofrecer un sistema que combine una alta usabilidad para usuarios no técnicos con una tecnología robusta y escalable, promoviendo un modelo híbrido que integre soluciones cerradas con protocolos abiertos de identidad digital.  
1.3 Público objetivo  Sybol está diseñado principalmente para:  • Pymes y autónomos que buscan mejorar sus ﬂujos de validación sin necesidad de conocimientos técnicos.  • Grandes empresas que requieren integraciones seguras con sus sistemas internos.  Gestores, responsables de cumplimiento y personal administrativo, con un enfoque claro en la simplicidad y la automatización.  
1.4 Estado actual  El producto se encuentra en una fase de beta estable, con todas las funcionalidades clave disponibles: emisión y gestión de credenciales, formularios, veriﬁcación de datos y red de contactos.  Se prevé el lanzamiento de un MVP consolidado en septiembre, tras una fase de estabilización técnica.  El roadmap para esa fecha y hasta 2026 contempla:  • Mejoras evolutivas enfocadas fundamentalmente a reforzar la seguridad y conectividad.  • Ampliación de la interoperabilidad con sistemas y estándares de identidad digital.


---

## Página 6


Documento Técnico 
 
 6 
• Evolución hacia una arquitectura abierta y descentralizada, compatible con wallets de identidad.  • Actualización de la experiencia de usuario (UX) y rediseño de interfaces.  Actualmente, el sistema contempla dos roles diferenciados: administrador y usuario operador, con funcionalidades especíﬁcas y complementarias que permitan operar la identidad digital de la compañía de forma eﬁciente y efectiva.   2 CRITERIOS DE DISEÑO  El diseño de Sybol garantiza la autenticidad, integridad y trazabilidad de la información compartida en procesos corporativos. A continuación, se describen sus funcionalidades principales, organizadas en cinco áreas clave:  
2.1 Identidad digital y confianza empresarial  Sybol permite a cada organización gestionar su identidad digital tanto como emisor como receptor de información. A través del uso de credenciales veriﬁcables, se asegura la asociación conﬁable entre la entidad emisora, el dato compartido y su responsable. La solución se basa en un software tipo wallet empresarial, que proporcionan un marco sólido de gestión de la identidad y garantía documental entre compañías.  
2.2 Intercambio estructurado y reutilizable de información  La plataforma permite a las organizaciones emitir credenciales digitales ﬁrmadas por la empresa, generar formularios de solicitud de información con una estructura estandarizada y reutilizar credenciales previamente veriﬁcadas para responder automáticamente a solicitudes de terceros. Estas capacidades habilitan una interacción segura, eﬁciente y estructurada entre entidades, minimizando la duplicación de esfuerzos y reduciendo signiﬁcativamente la fricción operativa.  
2.3 Trazabilidad, seguridad y auditoría  Cada acción realizada en Sybol —desde la emisión de una credencial hasta su recepción o expiración— queda registrada con trazabilidad completa. La infraestructura se apoya en tecnologías blockchain, lo que garantiza la inmutabilidad y la posibilidad de veriﬁcación descentralizada de la información, aportando transparencia, auditabilidad y conﬁanza operacional.  
2.4 Arquitectura modular orientada a la integración  El producto cuenta con una interfaz web organizada en dos espacios funcionales claramente diferenciados: una zona destinada a la gestión de la identidad propia, orientada a la identidad corporativa y su contenido, y otra enfocada en la emisión y solicitud de credenciales, correspondiente


---

## Página 7


Documento Técnico 
 
 7 
al rol de emisor. Esta división permite ofrecer una experiencia de usuario clara, segmentada y adaptada a las necesidades especíﬁcas de cada perﬁl. Además, la plataforma ha sido concebida bajo un enfoque API-ﬁrst, lo que facilita su integración con sistemas empresariales existentes, reduciendo signiﬁcativamente el esfuerzo técnico requerido para su adopción.  
2.5 Funcionalidad de Sybol  En el siguiente mapa de funcionalidad se puede ver, a grandes rasgos, los ﬂujos de información principales de Sybol, y como cada elemento de la cadena de valor los recibe e interactúa con ellos.


---

## Página 8


Documento Técnico 
 
 8 
3 DISEÑO DEL SISTEMA  3.1 Arquitectura lógica  Sybol se concibe como un sistema distribuido compuesto por nodos asignados a múltiples compañías clientes, formando una constelación de posibles emisores, receptores y veriﬁcadores de identidad. Cada cliente dispone de una infraestructura single-tenant para las gestión y almacenamiento de datos, operada y alojada por Sybol, pero aislada del resto, lo que permite mantener silos independientes si así se requiere. Y, en segundo lugar, la capa de ejecución se opera de forma multi-tenant sin almacenamiento de datos, reduciendo el coste de infraestructura y garantizando que el control de la información permanezca siempre en manos del cliente.  Los nodos de Sybol coordinan la información entre sí, asegurando la unicidad del usuario en toda la red. Esto permite que la identidad de un usuario pueda ser utilizada y veriﬁcada por distintos clientes de forma independiente, sin comprometer su control. Esta arquitectura facilita la integración con los sistemas corporativos de cada empresa, optimizando la validación y estandarización de procesos, y reduciendo costes operativos.  La arquitectura de cada nodo, incluido el nodo de backopice de Sybol (con funcionalidades especíﬁcas de administración y gestión), se compone de los siguientes módulos:


---

## Página 9


Documento Técnico 
 
 9 
a) Wallet  El Wallet es el núcleo funcional de Sybol. Se trata de una aplicación, actualmente disponible en versión web y con una versión móvil en desarrollo, que permite a personas jurídicas almacenar, gestionar y presentar credenciales veriﬁcables conforme a los estándares propuestos por el W3C. Este componente actúa como punto de convergencia para la identidad descentralizada, otorgando al usuario control directo sobre sus datos. Para garantizar la integridad y conﬁdencialidad de la información, el Wallet utiliza claves criptográﬁcas, mecanismos de veriﬁcación distribuida y ﬂujos de consentimiento explícito. Además, incorpora medidas de seguridad reforzada, como el control de acceso, la autenticación de dos factores y la segmentación de permisos por rol, asegurando una experiencia segura y conﬁable.  b) API Customer  La API Customer es una interfaz RESTful diseñada para facilitar la integración segura de terceros con las funcionalidades clave de Sybol, como la emisión de credenciales, la gestión de formularios, el control de identidades y el acceso a catálogos. Su enfoque API-ﬁrst garantiza una arquitectura moderna y escalable, mientras que la autenticación se realiza mediante el protocolo OAuth 2.0, asegurando un acceso controlado y conﬁable. Además, incorpora mecanismos de rotación de tokens y aplica el principio de privilegios mínimos para reforzar la seguridad. Todas las operaciones quedan registradas para ﬁnes de auditoría, y se emplean prácticas avanzadas como el cifrado TLS, validaciones estrictas y el almacenamiento seguro de claves en gestores de secretos, lo que garantiza la protección de los datos en todo momento.  c) Lambda Space  Lambda Space es el entorno de ejecución serverless donde se orquestan los procesos de negocio de manera eﬁciente, escalable y sin permanencia de estado. Cada función dentro de este entorno ejecuta una operación especíﬁca —como validar una credencial o propagar un evento— de forma aislada, lo que permite una arquitectura desacoplada y altamente modular. El sistema incluye monitorización en tiempo real a través de AWS CloudWatch, lo que facilita la trazabilidad de errores y el seguimiento de métricas clave. Además, se aplican buenas prácticas en el versionado, el testing y la gestión de excepciones, junto con políticas de ejecución y control de timeouts que garantizan la ﬁabilidad y el rendimiento del entorno  d) Key Manager  El Key Manager es el componente responsable de gestionar el material criptográﬁco de Sybol, abarcando la generación, el almacenamiento y la rotación de claves privadas utilizadas para ﬁrma digital, autenticación y veriﬁcación. Su infraestructura se basa en servicios robustos como AWS KMS y HashiCorp Vault, lo que garantiza altos estándares de seguridad y disponibilidad. Se aplican políticas de acceso basadas en roles, junto con mecanismos de auditoría para asegurar el cumplimiento normativo. Además, el sistema ofrece soporte para módulos HSM certiﬁcados, cifrado en reposo, esquemas de doble custodia y backups fuera de línea, lo que refuerza la protección ante posibles incidentes y facilita la recuperación ante desastres.


---

## Página 10


Documento Técnico 
 
 10 
e) Base de datos  Implementada sobre AWS RDS, la base de datos de Sybol almacena información estructurada que incluye entidades, relaciones, ﬂujos documentales, conﬁguraciones y registros operativos. Para garantizar la seguridad de los datos, se aplican medidas como el respaldo diario automatizado, el cifrado tanto en tránsito como en reposo, y un control de acceso riguroso con segmentación de privilegios. Además, se realizan validaciones periódicas de integridad y consistencia, asegurando la ﬁabilidad y estabilidad del sistema de almacenamiento.  f) Document Storage  El sistema de almacenamiento documental de Sybol se basa actualmente en volúmenes Docker, aunque ya se contemplan planes de evolución hacia soluciones más avanzadas. Este componente aloja los archivos asociados a credenciales, formularios y operaciones, garantizando su disponibilidad y trazabilidad. Entre sus funcionalidades se incluye el borrado programado de archivos obsoletos, la validación de integridad tras la carga de documentos y la auditoría de accesos, lo que permite mantener un control completo sobre el ciclo de vida de los archivos y asegurar su correcta gestión.  g) Blockchain  El módulo de Blockchain permite registrar de forma inmutable eventos clave relacionados con las credenciales, como su emisión, modiﬁcación o revocación. Está diseñado para integrarse con redes compatibles con la Ethereum Virtual Machine (EVM), como Alastria y Hedera, lo que garantiza una amplia interoperabilidad. Su arquitectura admite operación multired, conﬁgurable según el tipo de transacción, lo que aporta ﬂexibilidad y adaptabilidad a distintos entornos. El sistema realiza anclajes mediante hashes, asegurando que no se exponga contenido sensible, y permite la veriﬁcación cruzada y la monitorización directa en la cadena (on-chain). Todo esto se logra manteniendo un equilibrio óptimo entre transparencia, privacidad y eﬁciencia.  h) API Propagate  El componente de API propagate tiene la función de habilitar la interconexión de los distintos nodos de los clientes de Sybol, aunque en un inicio el sistema incluye un modo multi-tenant de ejecución, en el futuro se implementará para poder tener nodos de Sybol de diferentes clientes en silos completamente independientes y con distintos proveedores de cloud. Inicialmente se implementará con un mecanismo de colas para propagar los mensajes entre los distintos clientes de Sybol. La capacidad de propagación puede personalizarse por cliente o caso de uso, lo que permite una integración ﬂexible y eﬁciente con ecosistemas externos  i) BackoQice Sybol  El Backopice de Sybol es la herramienta administrativa destinada a usuarios con perﬁl de gestión o soporte. Permite la emisión y revocación de credenciales por parte de Sybol en procesos administrativos, el seguimiento de ﬂujos, la creación de formularios comunes para todos los clientes, la revisión de logs y la administración de políticas de conﬁanza.  Diseñado con un enfoque centrado en la usabilidad y la seguridad, este componente incorpora controles de acceso basados en roles, mecanismos de autenticación reforzada, sesiones limitadas en tiempo y alcance, y un registro completo de todas las acciones realizadas para garantizar la trazabilidad


---

## Página 11


Documento Técnico 
 
 11 
y facilitar la auditoría. Su diseño modular permite su extensión o personalización según las necesidades especíﬁcas de cada cliente o los requisitos del entorno regulatorio.  j) Catálogo  El servicio de Catálogo permite deﬁnir y mantener los esquemas y formatos de las credenciales disponibles en el ecosistema Sybol. Cada entrada del catálogo especiﬁca el tipo de credencial, el emisor autorizado, los requisitos de validación y el nivel de conﬁanza asociado, garantizando así una gestión estructurada y coherente de los distintos tipos de credenciales dentro del sistema.  Este componente actúa como un estándar interno que garantiza la coherencia en el diseño, emisión y consumo de credenciales. Dispone de una interfaz con control de versiones, incorpora validaciones automáticas y permite la sincronización con fuentes externas cuando es necesario. Además, se realizan revisiones periódicas para asegurar la actualidad de los datos y se gestionan procesos de desactivación de credenciales obsoletas o que no cumplan con los requisitos normativos.  
3.2 Arquitectura física


---

## Página 12


Documento Técnico 
 
 12 
La implementación objetivo de Sybol se basa en el ecosistema de soluciones de AWS, con el ﬁn de optimizar costes, asegurar alta disponibilidad y facilitar una futura portabilidad a otros proveedores de nube pública.  El diseño persigue una arquitectura elástica y bajo demanda, que minimice costes en ausencia de tráﬁco y escale automáticamente ante picos de uso, garantizando una experiencia ﬂuida. Para ello, se ha optado por una arquitectura basada principalmente en AWS Lambda, expuesta mediante API Gateway. No obstante, en esta primera versión, algunos procesos con dependencia de estado se mantienen en EC2, para evitar riesgos relacionados con el cifrado en reposo y la pérdida de datos. El sistema ha sido diseñado bajo el principio stateless, con el objetivo de eliminar estas dependencias en futuras versiones.  Además, se ha priorizado una arquitectura simple y eﬁciente, que facilite la operación, el mantenimiento y la escalabilidad. A medida que la plataforma crezca, la infraestructura se adaptará y se complejizará según las necesidades. Tras auditorías de seguridad externas, se incorporarán los componentes adicionales necesarios para mitigar cualquier vulnerabilidad antes de la puesta en producción.  
3.3 Tecnologías utilizadas  En este apartado se recogen las tecnologías y herramientas utilizadas para el desarrollo de Sybol en las distintas capas de la arquitectura.  3.3.1 Capa de visualización  La interfaz de usuario está desarrollada con React, lo que permite una experiencia moderna, dinámica y adaptable tanto a escritorio como a dispositivos móviles. Su distribución se realiza mediante AWS CloudFront como red de entrega de contenido (CDN), lo que mejora signiﬁcativamente la velocidad de carga y reduce la latencia global. Los artefactos del frontend (HTML, JS, CSS, imágenes), generados con herramientas como React y Webpack, se almacenan de forma estática en Amazon S3. Además, la arquitectura está diseñada bajo un enfoque headless, lo que permite un desarrollo modular, una entrega continua más ágil y una escalabilidad independiente entre el frontend y el backend.  3.3.2 Capa de negocio  La lógica del sistema se implementa principalmente en una arquitectura serverless, lo que permite escalar dinámicamente y reducir la complejidad operativa. Los procesos funcionales, como la emisión, validación, revocación y propagación de credenciales están implementados como funciones en AWS Lambda con entornos de ejecución de NodeJS y Python, mientras que aquellos con dependencia de estado se ejecutan temporalmente en EC2, hasta su externalización completa. La orquestación de tareas se realiza mediante un modelo event-driven basado en AWS SQS, que garantiza una entrega ﬁable, tolerancia a fallos y desacoplamiento entre módulos. La exposición de servicios se gestiona a través de API Gateway, que controla la autenticación, autorización, limitación de peticiones (throttling) y protección contra amenazas, complementado con AWS WAF . Por último, la gestión de usuarios se lleva a cabo mediante AWS Cognito, que administra la autenticación, los tokens, el inicio de sesión federado, la autenticación multifactor (MFA) y el control de sesiones.


---

## Página 13


Documento Técnico 
 
 13 
3.3.3 Capa de datos  El sistema gestiona tres tipos principales de datos: estructurados, documentales y criptográﬁcos. Los datos estructurados se almacenan en AWS RDS, con conﬁguración de alta disponibilidad, cifrado en reposo, copias de seguridad automáticas y replicación multizona (opcional según coste). Los documentos adjuntos, como formularios o archivos vinculados a credenciales, se gestionan en volúmenes de Docker sobre EBS, que ofrece versionado, alta durabilidad y control de acceso. En cuanto a la gestión criptográﬁca, se utiliza HashiCorp Vault sobre instancias EC2 como almacén seguro para claves privadas, certiﬁcados y secretos, aplicando políticas de acceso granulares. Además, se emplea AWS KMS para el cifrado en reposo, la gestión de claves y el cumplimiento de normativas como GDPR y eIDAS, con capacidades de auditoría, rotación de claves y control de acceso federado.  
3.4 Flujos de datos  Emisión de credencial:


---

## Página 14


Documento Técnico 
 
 14 
Validación/veriﬁcación:  
   Delegación:


---

## Página 15


Documento Técnico 
 
 15 
3.5 Flujos de estado  
  
    3.6 Lógica Estados  
  Estado: Validada | Flujo: Credential Request/Credential    
Estado: Rechazada | Flujo: Credential Request


---

## Página 16


Documento Técnico 
 
 16 
 Estado: Revocada | Flujo: Credential      Presentation Request - Presentation     
Estado: Validada | Flujo: Presentation Request/Presentation     
Estado: Rechazada | Flujo: Presentatio Request     
 Estado: Revocada | Flujo: Presentation


---

## Página 17


Documento Técnico 
 
 17 
4 PROTOCOLO DE IDENTIDAD Sybol actualmente está construido sobre el protocolo de identidad Alastria, que se encuentra en su versión 2.2 con la versión 3.0, también conocida como EPIC, pendiente de lanzarse junto con la red ISBE. Se ha de tener en cuenta que Sybol es uno de los proyectos tractores del protocolo de identidad de Alastria e ISBE, liderando las siguientes cuestiones: • Registro único de activos de identidad (credentials, presentations, etc) basado en el ENS de Ethereum. • Sustituir la funcionalidad del proxy de identidad con la posibilidad de incluir SC account siguiendo la EIP 4337 (en un futuro implementando la EIP 6900 [ERC-6900: Modular Smart Contract Accounts and Plugins (ethereum.org)]) asociado al árbol de dominios de identidad. • Habilitar un registro de clave publica generalista con soporte a los principales algoritmos. Inicialmente se incluirán secp256k1, secp256r1 y RS512 (ERC 7518 [RFC 7518 - JSON Web Algorithms (JWA) (ietf.org)]). • Habilitar el uso de recovery keys para las cuentas de control de a identidad. • Facilitar la integración de account abstraction basadas en identidad (RIP 7212 [EIP-7212: Precompiled for secp256r1 Curve Support - RIPs - Fellowship of Ethereum Magicians (ethereum-magicians.org)]). • Habilitar Alastria ID login con OpenId connect basado en VC e ID challenges (RFC 6749: The OAuth 2.0 Authorization Framework (rfc-editor.org) y Final: OpenID Connect Core 1.0 incorporating errata set 2). • Actualizar el modelo de credenciales a W3C v2.0 (Veriﬁable Credentials Data Model v2.0 (w3.org)). • Extender el framework de eIdas 2.0 a Alastria para funcionar como una extensión del mismo en cuanto a nomenclatura y funcionalidad ( ARF ). • Implantar JSON-LD y JWT de forma apropiada siguiendo las deﬁniciones formales de ambos estándares para el intercambio de objetos. • Utilizar JSON-LD y SD-JWT como elementos de contexto de los objetos de identidad para la interoperabilidad. • Implementar un Name Service para hacer resolución de todos los DIDs posibles on-chain, principalmente el DID-document, siguiendo el estandar de ENS, e incluir una posibilidad de tener DID y CID direccionado por alias. • Implementar la derivación de claves en las EOA siguiendo la deﬁnición de EPIC para los paths de derivación diseñados. • Extender JWT en el protocolo con JWS, habilitando ambas posibilidades para el intercambio de objetos ﬁrmados, y, abriendo la posibilidad de utilizar JWE para el intercambio de datos cifrados.


---

## Página 18


Documento Técnico 
 
 18 
4.1 Punto de partida Para tener una visión global del protocolo, primero se aplica el concepto de Identidad de Alastria, que es, el conjunto de EOAs, Clave privadas adicionales y el SC representativo de la identidad, conectados al protocolo para poder registrar claves públicas, objetos de identidad y abriendo la posibilidad de holdear tokens desde la identidad. Se debe habilitar el uso del ERC 165 para la detección de interfaces y prevenir un uso incorrecto de la red que derive en un error. 
 En segundo lugar, el protocolo mantiene su esencia de versiones anteriores, teniendo el gestor principal del protocolo como Identity Manager, y existiendo el registro de objetos (uniﬁcando credenciales y presentaciones), el registro de claves públicas (separado por sencillez y futuros usos) y el conjunto de contratos de identidad. 
  El protocolo de Identidad Digital de Alastria se centra en dos elementos clave: • Vinculación de claves públicas a entidades (y personas) reconocibles (Autenticación). • Sistema de objetos auto veriﬁcables mediante mecanismos de ﬁrma electrónica (Validación). 
IdentityManager –DID registry(subject)
Identityregistry[Credenital, PubKey, Presentation]
US-1.2 Alastria ID Creation
US-2.1.1. Alastria ID Authentication
US-3.1. Alastria ID Identity Recovery
SubjectDID
SubjectPubK
SubjectDIDSubjectPubK Verify SignedObject
SubjectPubK
Subject SignedObjects:-AlastriaSession-Presentation
delete Subject Credential
add Subject Credential
delete Subject Presentation
add Subject Presentation
DID
SubjectPubK
DID


---

## Página 19


Documento Técnico 
 
 19 
Este sistema, además, permite asignar atributos de forma pública y contrastable a estas identidades, permitiendo la asignación de roles, etiquetas y otros mecanismos de transparencia que permitan generar mecanismos de Autenticación autosostenidos, ya que, en la mayoría de los casos, la autenticación requiere de un tercero de conﬁanza que establezca la primera relación fehaciente. Para poder mantener una protección sobre los datos, el protocolo se debe estructurar en torno a dos canales de información, uno privado, que ocurre entre los pares interesados, o más concretamente, un mecanismo op-chain, y una parte de anclaje a un sistema de la información que permita mantener una fuente de verdad única y publica, siendo esta parte del mecanismo on-chain (aunque podría haberse construido entorno a otras tecnologías, la elección de la tecnología blockchain es la mejor alternativa para ello). Los elementos que conforman el protocolo son: la creación de la identidad, la asignación de un identiﬁcador único o DID, la vinculación de atributos, la generación de datos auto veriﬁcables y el registro de estado. 
4.2 Creación de Identidad La creación de la identidad se basa en la generación de un smart contract, en la versión 2.2, y para ello, primero se debe crear un par de claves de acceso y, en caso necesario, un par de claves de ﬁrma. Estas pueden ser las mismas, aunque se recomienda tener sets de claves independientes. En la versión de ISBE se va a sustituir la creación de un Smart contract por una emisión de un DID por parte de ISBE. Para las claves de acceso, se podrá utilizar la EIP 7212 en un futuro para permitir la integración con keypass o similares, pero actualmente, se debe utilizar un wallet externo o EoA, que será utilizado como llave inicial en un smart contract account. Estas claves se generarán como elementos derivados siguiendo lo establecido en el apartado de EPIC. En segundo lugar, se debe crear una clave de ﬁrma, pudiendo utilizarse la generada para el acceso, pero debe ser una soportada por la RFC 7518, que deﬁne las claves posibles para JWS mediante la deﬁnición de la cabecera JOSE (Draft-ietf-jose-fully-speciﬁed-algorithms-05 - Fully-Speciﬁed Algorithms for JOSE and COSE).. "alg" Param Value Digital Signature o MAC Algorithm HS256 HMAC con SHA-256 HS384 HMAC con SHA-384 HS512 HMAC con SHA-512 RS256 RSASSA-PKCS1-v1_5 con SHA-256 RS384 RSASSA-PKCS1-v1_5 con SHA-384 RS512 RSASSA-PKCS1-v1_5 con SHA-512 ES256 ECDSA con P-256 y SHA-256 ES384 ECDSA con P-384 y SHA-384 ES512 ECDSA con P-521 y SHA-512 PS256 RSASSA-PSS con SHA-256 y MGF1 con SHA-256


---

## Página 20


Documento Técnico 
 
 20 
"alg" Param Value Digital Signature o MAC Algorithm PS384 RSASSA-PSS con SHA-384 y MGF1 con SHA-384 PS512 RSASSA-PSS con SHA-512 y MGF1 con SHA-512 none Sin firma digital  Esta lista se puede ampliar mediante la RFC 8037 para las curvas Ed25519 y Ed448, así como mediante la RFC 8812 para los algoritmos WebAuthn (que incluyen la curva secp256k1, la misma utilizada en ethereum). Con esto se cubren los algoritmos EdDSA y ES256K. Con estas claves creadas, la entidad o persona podrá generar su smart contract de identidad y asociar a este su clave pública y su DID document. El ﬂujo simpliﬁcado sería: 1. Generación de claves: a. Clave de acceso siguiendo el path de derivación. b. Clave de ﬁrma bajo el algoritmo deseado. 2. Solicitud de aprobación de creación de identidad a un Service Provider mediante la identiﬁcación de la clave de acceso. 3. Generación del contrato de identidad con una transacción ﬁrmada por la clave de acceso: a. Creación del DID mediante el address del Smart Contract creado. b. Vinculación de la clave pública de ﬁrma con el DID. c. Registro del DID document. La descripción detallada del DID document se encuentra en el siguiente apartado, junto con el DID method. 
4.3 Documento DID Un DID Document es un único objeto JSON que cumple con la RFC7159. En Alastria, la instancia del DID Document asociado a un DID especíﬁco no tiene que existir en un sistema de almacenamiento físico, sino que en realidad es "virtual" . Esto signiﬁca que, dado un DID, existe un procedimiento para construir un DID Document con toda la información relacionada con el AlastriaID básico asociado, según la especiﬁcación de DID.  4.3.1 Ejemplo documento DID Un documento DID simple tiene la siguiente estructura: ```json { "@context": " https://w3id.org/did/v1", "id": "did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1", "publicKey": [{ ... }], "authentication": [{ ... }], "service": [{ ... }] }


---

## Página 21


Documento Técnico 
 
 21 
``` • Context: Proporciona el contexto que permite interpretar correctamente los términos utilizados en el JSON, asociándolos con deﬁniciones especíﬁcas y vocabularios reconocidos. Esto asegura que los datos sean comprensibles y procesables de manera uniforme por diferentes sistemas, facilitando la interoperabilidad y la vinculación de datos en la web semántica. Concretamente es el provisto por el W3C sobre los DID documents. • Id: DID de la identidad a la que hace referencia. • publicKey: campo que contiene las claves públicas que están asociadas con el DID. Estas claves se utilizan para veriﬁcar la autenticidad de las ﬁrmas digitales y pueden admitir varios tipos de algoritmos criptográﬁcos. La presencia de estas claves permite a otros usuarios o sistemas cifrar información que solo el propietario del DID puede descifrar, garantizando la seguridad y privacidad de las comunicaciones. • Ejemplo: ```json "publicKey": [ { "id": "did:example:123456789abcdefghi#keys-1", "type": "RsaVerificationKey2018", "controller": "did:example:123456789abcdefghi", "publicKeyPem": "-----BEGIN PUBLIC KEY...END PUBLIC KEY-----" } ] ``` • Authentication: El campo de autenticación deﬁne los mecanismos mediante los cuales se puede autenticar que una entidad que presenta un DID es realmente el propietario de dicho identiﬁcador. Esto puede incluir métodos como claves públicas, contraseñas o datos biométricos. La autenticación es crucial para la veriﬁcación de identidad en transacciones y comunicaciones seguras, asegurando que solo el propietario legítimo pueda actuar en nombre del DID.  • Ejemplo: ```json "authentication": [ { "id": "did:example:123456789abcdefghi#keys-1", "type": "RsaVerificationKey2018", "controller": "did:example:123456789abcdefghi", "publicKeyPem": "-----BEGIN PUBLIC KEY...END PUBLIC KEY-----" } ] ``` • Service: Este campo describe los servicios asociados con el DID. Puede contener una variedad de servicios, como puntos de acceso para comunicación, servicios de identidad, o cualquier otro servicio que el propietario del DID quiera asociar con su identidad digital. Este campo


---

## Página 22


Documento Técnico 
 
 22 
facilita la interoperabilidad y la vinculación de servicios en diferentes plataformas, permitiendo una integración más ﬂuida en el ecosistema de identidad digital.  • Ejemplo: ```json "service": [ { "id": "did:example:123456789abcdefghi#vcs", "type": "VerifiableCredentialService", "serviceEndpoint": "[URL]/" } ] ``` 4.3.2 Especiﬁcación DID La especiﬁcación DID de Alastria cumple con los requisitos de la especiﬁcación DID del Grupo de la Comunidad de Credenciales del W3C, con algunas advertencias mencionadas en el texto. Alastria, siendo tecnológicamente agnóstica, utiliza Quorum para su red blockchain inicial, pero planea adoptar otras tecnologías como Hyperledger Fabric (https://github.com/hyperledger/fabric) buscando máxima interoperabilidad entre todas las implementaciones de blockchain. Como se describe en la especiﬁcación DID [https://w3c-ccg.github.io/did-spec/]: "Un DID debe ser persistente e inmutable, es decir, estar ligado a una entidad una vez y nunca cambiar (para siempre). Idealmente, un DID sería un identiﬁcador descentralizado completamente abstracto (como un UUID) que podría vincularse a múltiples ledgers o DLTs subyacentes a lo largo del tiempo, manteniendo así su persistencia independiente de cualquier libro mayor o red en particular. Sin embargo, el registro del mismo identiﬁcador en varios libros de contabilidad o redes presenta problemas extremadamente difíciles de entidad y de inicio de autoridad (SOA). También aumenta en gran medida la complejidad de la implementación para los desarrolladores. Para evitar estos problemas, se RECOMIENDA que las especiﬁcaciones del método DID solo produzcan DID y métodos DID vinculados a ledgers o DLTs robustas y estables capaces de realizar el más alto nivel de compromiso con la persistencia del DID y el método DID a lo largo del tiempo.” El enfoque del protocolo Alastria es doble: 1. Por un lado, el formato DID de Alastria incluye el tipo de red en el DID para que los resolutores puedan utilizarla para acceder a la red adecuada para la resolución de DID document. 2. Por otro lado, Alastria incluirá una implementación temprana de la propiedad "equivID" sugerida, tan pronto como haya otra red blockchain.


---

## Página 23


Documento Técnico 
 
 23 
4.3.3 Esquema Alastria DID Los DID de Alastria tienen el siguiente formato del w3c [Decentralized Identiﬁers (DIDs) v1.0 (w3.org)]: 
 Ilustración: Ejemplo DID  Componente Descripción Scheme "did" Method "ala":["quor"|"fabr"|"besu"]:"net-id" Specific Identifier depende de la red, ver más abajo  Los componentes especíﬁcos del Alastria DID method son los siguientes: 1. "ala": especiﬁca que se trata de un DID para el framework de Alastria. 2. "network ": especiﬁca la tecnología subyacente para la red Alastria especíﬁca. Los mecanismos y algoritmos utilizados para resolver y administrar documentos DID pueden ser muy diferentes en todas las tecnologías, por lo que este componente indica a los desarrolladores de aplicaciones qué algoritmo usar para una instancia DID determinada. El valor actual de este componente es "quor" para la red basada en Quorum, "besu" para la red basada en Besu, pero se espera que pronto se agregue una red que use "fabr". Se añadirán otros valores a medida que Alastria ID se implemente sobre otras tecnologías. 3. "net-id ": deﬁne la instancia especíﬁca de la red blockchain de Alastria. Actualmente, las valoraciones aceptadas son "redT" y "redB". Ejemplos de DID pueden ser: Para la redT actual de Alastria: "did:ala:quor:redT:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1" Para la actual Red B de Alastria: "did:ala:besu:redB:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1" Para la red Red T actual, "speciﬁc-idstring" es la dirección de Ethereum del contrato de proxy que representa el AlastriaID de la entidad, codiﬁcada en hexadecimal con o sin preﬁjo 0x. La creación de un contrato de representación se especiﬁca en el apartado anterior de creación de identidad.


---

## Página 24


Documento Técnico 
 
 24 
4.4 DID Resolve 4.4.1 Public keys Las claves asociadas a la identidad de Alastria, en la implementación de Quorum, deben generarse de acuerdo con las especiﬁcaciones de Ethereum. En la versión actual de la especiﬁcación DID "Identiﬁcadores Descentralizados (DIDs) v0.11" , dichas claves aún no son compatibles, por lo que debemos deﬁnir un nuevo tipo de clave. El nombre sugerido es "EcdsaKoblitzPublicKey" , dado que Bitcoin y Ethereum usan la curva elíptica Koblitz, también conocida como secp256k1. Esto también es consistente con la próxima deﬁnición de un nuevo conjunto de ﬁrmas en el Modelo de Datos de Credenciales Veriﬁcables, llamado “EcdsaKoblitzSignature2016” . Un ejemplo de entrada de publicKey en el Documento DID, con una sola clave, podría ser: ... "publicKey": [{     "id": "did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",     "type": ["CryptographicKey", "EcdsaKoblitzPublicKey"],     "curve": "secp256k1",     "expires": "2019-06-11T22:07:10Z",     "publicKeyHex": "0xf42987b7faee8b95e2c3a3345224f00e00dfc67ba88266b35efd6fc481e162b7f3471617b2433cdc74d04c81ef6db911ca416efa296cd2c4962e35d804560104" }], ... El "id" de la “publicKey” tiene dos componentes: "did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1" es el DID del propietario de la clave, que corresponde al sujeto del DID. "#keys-1" es un fragmento URI que especiﬁca la clave en particular del sujeto del DID. Por el momento, un Alastria.ID solo tiene una clave, pero este es el mecanismo genérico en la especiﬁcación del DID para identiﬁcar varias claves con distintos propósitos. Con el ﬁn de garantizar la compatibilidad futura, se recomienda usar un fragmento URI para identiﬁcar la clave, aunque actualmente no sea estrictamente necesario. 4.4.2 Resolución documento de DID El proceso de resolución del documento DID describe cómo obtener el Documento DID asociado a un DID dado. En el protocolo de Alastria, el proceso es el siguiente: • A partir del DID, determina el tipo de red (Quorum o Fabric) y el nombre de la red. • Utiliza el DID para obtener la clave pública asociada mediante el Smart Contract "AlastriaPublicKeyRegistry", que en ISBE se registrará bajo el Name Service • Crear el DID-document en base a la información recuperada.


---

## Página 25


Documento Técnico 
 
 25 
4.4.3 Registro único de objetos Este registro puede contener cualquier estado de objeto. Esto incluye, pero no se limita a, Credential, Presentation, Presentation Request, DIDs y Public Keys. Los estados se indexarán por el hash del objeto en el registro único para poder validar el estado de forma descentralizada. 4.4.4 Alineamiento con ARF eIDAS ARF deﬁne 4 estados diferentes de atestación: Emitido, Válido, Revocado, Expirado. Para alinear los estados de atestación de ARF con la implementación del protocolo sobre ISBE, se tendrán en cuenta las siguientes consideraciones: • Emitido: cuando el hash de la credencial por parte del emisor tiene el estado Válido o "Ask Owner", el hash de la credencial por parte del sujeto es Válido o "Ask Owner", y la fecha actual es anterior al atributo "nbf" . • Válido: cuando el hash de la credencial por parte del emisor tiene el estado Válido o "Ask Owner", el hash de la credencial por parte del sujeto es Válido o "Ask Owner", y la fecha actual está entre el atributo "nbf" y antes del atributo "exp" . • Revocado: cuando el hash de la credencial por parte del emisor tiene el estado Revocado y el hash de la credencial por parte del sujeto es Revocado. • Expirado: cuando el hash de la credencial por parte del emisor tiene el estado Válido o "Ask Owner", el hash de la credencial por parte del sujeto es Válido o "Ask Owner" y la fecha actual es anterior al atributo "nbf" Y la fecha actual es posterior al atributo "exp" . El modelo de Alastria EPIC administra dos hashes diferentes por objeto: el hash Emisor/Sujeto para Credenciales y el hash Sujeto/Proveedor de Servicio para las Presentaciones. Otros objetos como las Claves Públicas tendrán un único hash registrado por el propietario. 
4.5 Validación de estado Para validar el estado de un objeto se siguen los siguientes pasos: 1) Se veriﬁca el estado del objeto como JWT, incluyendo la validez de la ﬁrma en el registro de claves púbicas. 2) Se veriﬁca que el objeto no está revocado mediante el registro público de objetos. 3) Se veriﬁca recursivamente cada nivel del objeto que contenga otros objetos anidados. Tras estos pasos se puede situar un objeto de forma fehaciente en alguno de los 4 estados válidos: emitido, válido, revocado, expirado. 
4.6 Credentials Por simplicidad, se utilizará el término Credential para referirse a una Veriﬁable Credential, ya que son las únicas relevantes en el contexto de Alastria ID. Para facilitar la gestión de las credentials en Alastria, actualmente se están representando en el formato denominado JSON-LD junto con JWTs según el documento Veriﬁable Credentials Implementation Guidelines 1.0. Esto signiﬁca que se empleará el formato JSON Web Token para representar una Credential. Un token JWT se compone de tres partes: el encabezado, el payload y la ﬁrma.


---

## Página 26


Documento Técnico 
 
 26 
4.7 Presentation Una Presentation es una colección de una o más credentials emitidas por uno o varios emisores, que expresa un aspecto de una persona, organización o entidad. La Presentation es también un JWT ﬁrmado por el sujeto, que contiene una o más Credentials y datos adicionales especíﬁcos de su identidad. 
4.8 Presentation Request Este es un modelo de objeto que no está incluido en el estandar W3C Veriﬁable Credentials Data Model 1.0. En Alastria, un objeto Presentation Request es una colección de uno o más elementos de datos que el proveedor de servicios está solicitando a un sujeto. La entidad que recibe el Presentation Request lo utiliza para crear un objeto Presentation apropiado que cumpla los requisitos del proveedor de servicios. El Presentation Request es un JWT ﬁrmado (ﬁrmado por la entidad que envía la solicitud) que contiene en su payload la colección de uno o más elementos de datos y el LoA requerido.  5 SEGURIDAD Y BUENAS PRÁCTICAS  La protección efectiva de los sistemas de identidad digital requiere un enfoque integral que combine herramientas tecnológicas, políticas internas y capacitación continua. A continuación, se detallan las principales líneas de actuación y buenas prácticas que Sybol ha puesto en práctica o tiene en su Roadmap para los próximos meses:  
5.1 Protección de claves privadas  Las claves privadas son el núcleo de cualquier sistema de identidad digital y su compromiso supone un riesgo crítico. Para protegerlas, se recomienda almacenar las claves en dispositivos especializados como HSMs (Hardware Security Modules) o hardware wallets, que ofrecen máxima protección frente a ataques físicos y lógicos. En entornos con recursos limitados, puede optarse por wallets de software cifrados, asegurándose de que estén protegidos mediante PIN o autenticación biométrica. Es fundamental implementar políticas de acceso restringido, limitando el manejo de estas claves a personal previamente autorizado y registrando todo acceso en sistemas de auditoría. Además, se deben habilitar mecanismos de recuperación como frases semilla almacenadas opline en soportes seguros y bajo esquemas de doble custodia.  Es por ello que Sybol ha creado una estructura basada en mecanismos serverless para poder atender estas necesidades de seguridad. Las claves de cada compañía se diferencian en: claves de ﬁrma, dedicadas a la emisión de credenciales y formularios vinculados con la identidad, y claves de anclaje con las cadenas de bloques.


---

## Página 27


Documento Técnico 
 
 27 
5.2 Activación del segundo factor de autenticación (2FA)  Desde Sybol, se fomenta el uso de MFA para la gestión de los activos bajo la identidad digital. Por ello, en el Roadmap se contempla como parte de las medidas de seguridad integrar tecnología MFA en el corto plazo, ya que el segundo factor de autenticación refuerza la seguridad al añadir una capa adicional a las credenciales de acceso a la plataforma. Se prevé integrar aplicaciones autenticadoras líderes en el mercado como Google Authenticator o Authenticator de Microsoft. De esta forma Sybol impone la aplicación del 2FA obligatoriamente en todos los sistemas. Asimismo, se establecerá un canal seguro y alternativo para la recuperación de accesos en caso de pérdida de dispositivos o bloqueo. 
5.3 Actualizaciones regulares  Como parte de las políticas de seguridad, Sybol establece la revisión y despliegue de las actualizaciones pertinentes en cada uno de los sistemas, asegurando de esta forma que no se producen vulnerabilidades evitables en los sistemas gracias a la implantación de protocolos de prevención. 
5.4 Auditoría de actividad  Toda actividad relacionada con el sistema de identidad debe quedar registrada. Cada evento debe incluir metadatos con información del usuario, la acción realizada, la fecha y el origen. Estos registros deben almacenarse en sistemas inmutables (WORM) o ser respaldados por mecanismos de integridad criptográﬁca. Se recomienda revisar los logs periódicamente mediante dashboards e incluir alertas ante comportamientos anómalos, como accesos fuera de horario o errores repetidos.  
5.5 Gestión del ciclo de vida del material criptográfico  Para mantener las claves seguras, Sybol aplicará una política de gestión de claves según el nivel de contratación del cliente, garantizando siempre la seguridad mínima necesaria. Esta política cubrirá todo el ciclo de vida de las claves desde su ceremonia de creación, almacenamiento, uso, rotación, hasta su revocación. El ciclo de vida de una identidad debe estar claramente deﬁnido desde su creación hasta su eliminación. Para ello, la creación de identidades requiere documentos de prueba, aprobación y validación técnica.


---

## Página 28


Documento Técnico 
 
 28 
6 CASOS DE USO DEL PRODUCTO  6.1 Verificación de información de proveedores contratistas, empleados y equipamientos para la Coordinación de Actividades empresariales (CAE)  
  Sybol está integrando el nuevo modelo de Identidad Digital Descentralizada en los procesos de Coordinación de Actividades Empresariales (CAE), que abarcan la veriﬁcación de datos de proveedores, contratistas, empleados y equipamientos (por ejemplo, vehículos). Para ello, está desplegando el proyecto CAE360, un programa orientado a implantar esta solución en sectores clave. Su objetivo es lograr una adopción progresiva por parte de proveedores y clientes, adaptando los procesos para mejorar la eﬁciencia y la competitividad.  En este contexto, Sybol, Repsol y la Confederación Española de Transporte de Mercancías (CETM) están pilotando el despliegue en el sector de la logística y el transporte de mercancías, considerado estratégico para asegurar la transversalidad y el escalado del modelo.  Objetivos clave:  • Transformación digital – Proyecto País  • Impulsar la competitividad del sector mediante:  o Mayor eficiencia operativa  o Agilidad en la gestión  o Ahorro de costes estructurales  o Refuerzo de la seguridad    6.2 Emisión de credenciales verificables. Caso de uso de Distintivos de Origen Renovable (DOR) para clientes de suministros energéticos  ¿Qué son los distintivos ambientales de Sybol?   Son una evidencia digital veriﬁcable y segura que, en forma de credencial, queda vinculada a la identidad digital de los consumidores y de los emisores, es decir, de empresas que producen, comercializan y distribuyen productos y suministros sostenibles o de origen renovable.


---

## Página 29


Documento Técnico 
 
 29 
  ¿Para qué sirven? Objetivo  Los distintivos ambientales Sybol permiten a sus titulares demostrar el origen renovable de los productos y suministros que consumen. Además, pueden utilizarse como evidencia de control y compliance ante procesos de auditoría energética (privados) a la vez que establecen una diferenciación comercial.   En el caso de Repsol, estos distintivos permiten “poner en valor” las garantías de origen de la CNMC acercándolo su utilidad al usuario ﬁnal.  ¿Cómo funcionan y como se vinculan a la identidad digital?   Los distintivos ambientales son comprobantes digitales y nominales autenticados con tecnología blockchain y vinculados a la identidad digital del emisor y a la identidad digital de su titular, el consumidor. Los wallets de empresas y consumidores habilitan el intercambio de los distintivos en forma de credenciales de identidad veriﬁcables, que permiten a terceros (receptores de esos datos) comprobar la autenticidad y la vigencia del distintivo en tiempo real.  
6.3 Gestión de identidades y credenciales de empleados  La plataforma permite emitir credenciales digitales veriﬁcables que certiﬁcan cualiﬁcaciones profesionales de forma segura, escalable y en tiempo real. Estas credenciales pueden ser utilizadas tanto por estudiantes como por profesionales y empresas, facilitando procesos como la identiﬁcación de talento, la promoción de la meritocracia o la gestión de datos de empleados en cualquier proceso interno de recursos humanos. En el siguiente ﬂujograma a alto nivel se muestran los casos de uso que está explorando Repsol a través de pruebas de concepto con Sybol:


---

## Página 30


Documento Técnico 
 
 30 
 En este contexto, el modelo otorga a los usuarios (empleados, estudiantes, candidatos, contratistas) credenciales de identidad vinculadas a sus cualiﬁcaciones o capacidades profesionales, que pueden implementarse en procesos de gestión de recursos humanos y organización, como formación y aprendizaje o control de accesos, permisos y roles.  7 PRUEBAS La metodología de pruebas de cara a la versión inicial de Sybol se ha diseñado para garantizar la máxima calidad, robustez y conformidad del producto. Su estructura abarca una rigurosa estrategia de validación funcional, técnica, de seguridad e interoperabilidad.  
7.1 Objetivos perseguidos  • Funcionalidad: veriﬁcar que cada componente implementado se ajusta a los requisitos especiﬁcados en la deﬁnición funcional.  • Integración: validar la ﬁabilidad de los ﬂujos completos (emisión, solicitud, veriﬁcación, revocación) incluyendo la gestión de errores y recuperación.  • Compatibilidad e interoperabilidad: asegurar la correcta integración con wallets estándar (con o sin DID), y la interoperabilidad con otros sistemas de estandarización (EBSI, eIDAS2, AlastriaID).  • Seguridad: validar el estado en cuanto a vulnerabilidades conocidas del código desplegado.  
7.2 Tipología de pruebas  Se aplica una combinación de pruebas automatizadas y manuales, escalables y reproducibles:  • Pruebas unitarias: ejecutadas con NodeJS, cubriendo funciones especíﬁcas de backend para asegurar precisión y detección de regresiones tempranas.  • Pruebas de integración: realizadas mediante colecciones de Postman para validar ﬂujos completos basados en escenarios.


---

## Página 31


Documento Técnico 
 
 31 
• Pruebas de interfaz / UI: manuales sobre React, simulando escenarios de uso reales (rol administrador, operador, issuer, holder).  • Pruebas de aceptación funcional (UAT): ejecutadas junto a stakeholders en entornos de prueba para validar la solución frente a escenarios operacionales reales.  • Pruebas de seguridad: Análisis estático con herramientas como SonarQube para asegurar la ausencia de dependencias inseguras y el cumplimiento de los estándares de calidad y seguridad.  
7.3 Herramientas y Automatización  Para garantizar un proceso de validación sólido, escalable y alineado con estándares de calidad, se emplean las siguientes herramientas:  Newman: ejecuta colecciones de Postman mediante línea de comandos, ideal para automatizar pruebas API sin necesidad de la interfaz gráﬁca. Permite ejecutar las colecciones exportadas (.json), parametrizar entornos y generar informes detallados (HTML, JSON o CLI), facilitando el análisis de resultados y detección de errores   GitHub Actions: herramienta de integración continua donde, tras cada push o pull request, se puede disparar un pipeline que ejecute los tests, los despliegues y aquellas acciones asociadas a la gestión del ciclo de vida que permitan asegurar la máxima calidad del producto de Sybol.  
7.4 Gestión de entornos de prueba  Se utilizan entornos replicables y aislados en AWS, con despliegues conﬁgurados mediante Docker Compose y archivos .env. Cada instancia opera de forma independiente, con variables de entorno separadas garantizando reproducibilidad y trazabilidad. Estos archivos también están disponibles para la conﬁguración de la ejecución de las instancias serverless.  8 DEVOPS  8.1 Entornos disponibles  En el ciclo de vida del desarrollo del producto, se han implementado tres entornos clave que permiten un ﬂujo de trabajo ágil y controlado, asegurando la estabilidad, calidad y disponibilidad de las funcionalidades a lo largo del proceso de desarrollo. Estos tres entornos son: Desarrollo, Staging (o Demo) y Producción. A continuación, se detallan las funciones y características de cada uno:  8.1.1 Entorno de Desarrollo:  • Propósito: Este entorno está destinado al desarrollo de nuevas funcionalidades y la implementación de cambios en el sistema. En él, los desarrolladores trabajan para escribir, probar e iterar sobre el código antes de que se considere para pruebas de funcionalidad.


---

## Página 32


Documento Técnico 
 
 32 
• Características: Es un entorno dinámico donde se realizan cambios rápidos y experimentales. No se garantiza que esté libre de errores y no es accesible para los usuarios ﬁnales. En este entorno, se llevan a cabo las primeras pruebas de integración y funcionalidad.  • Uso principal: Creación de nuevas características, pruebas unitarias y pruebas de integración iniciales.  8.1.2 Entorno de Staging (o Demo):  • Propósito: Este entorno se utiliza para probar versiones completas del producto en un ambiente lo más parecido posible al entorno de producción. Su objetivo principal es garantizar que las nuevas funcionalidades, mejoras y correcciones de errores funcionen correctamente en un entorno de "casi producción" , validando la interacción de todas las piezas del sistema antes de que se desplieguen en producción.  • Características: El entorno de staging reﬂeja ﬁelmente la conﬁguración y las condiciones del entorno de producción, incluyendo conﬁguraciones de base de datos, servidores y servicios externos. En este entorno se realizan pruebas de aceptación, validación de versiones completas y demostraciones del producto a las partes interesadas.  • Uso principal: Validación de la funcionalidad del sistema con una versión más estable y completa, pruebas de integración ﬁnal, pruebas de carga y demostraciones de producto.  8.1.3 Entorno de Producción:  • Propósito: Este es el entorno en el que el producto se pone a disposición de los clientes ﬁnales. Es el entorno que soporta las operaciones en vivo del sistema, donde se sirven las funcionalidades completas a los usuarios y donde se gestionan los datos reales.  • Características: El entorno de producción debe ser altamente disponible, escalable y optimizado para asegurar un servicio continuo sin interrupciones. Está sujeto a rigurosos procedimientos de monitoreo, seguridad y respaldo para garantizar la integridad de los datos y la estabilidad de la aplicación. Solo se despliegan en producción versiones completamente validadas y probadas previamente en los entornos de desarrollo y staging.  • Uso principal: Entorno de uso ﬁnal para los usuarios, con acceso en tiempo real al producto y gestión de los datos de los clientes y las transacciones.  De esta manera, se asegura que cada etapa del desarrollo del producto sea cuidadosamente revisada antes de que cualquier cambio llegue al entorno de producción, garantizando la estabilidad y ﬁabilidad del producto ﬁnal para los usuarios.  
8.2 Pipelines CI/CD  Los pipelines CI/CD (Integración Continua y Despliegue Continuo) son una práctica clave para asegurar un proceso de desarrollo ágil, automatizado y sin interrupciones. Implementar un pipeline CI/CD proporciona una serie de ventajas:  • Automatización de procesos: Se automatizan tareas repetitivas como la construcción, prueba y despliegue del software, lo que minimiza la intervención manual y reduce los errores humanos.


---

## Página 33


Documento Técnico 
 
 33 
• Reducción de tiempos de entrega: Gracias a la integración continua, los cambios de código se integran y prueban de manera rápida y continua, lo que acelera el proceso de desarrollo y permite entregas más frecuentes.  • Calidad mejorada: Con pruebas automatizadas y despliegues controlados, se asegura que cada versión del software sea estable, funcional y lista para producción.  • Feedback rápido: Los equipos de desarrollo reciben retroalimentación instantánea sobre el código que han subido, permitiendo detectar errores de manera temprana y mejorar la calidad del software en tiempo real.  • Escalabilidad: Permite gestionar múltiples entornos (desarrollo, staging, producción) de forma eﬁciente, sin comprometer la calidad ni el tiempo de entrega.  8.2.1 Flujo del Pipeline CI/CD  El pipeline CI/CD diseñado sigue un proceso estructurado, dependiendo del entorno en el que se ejecute (desarrollo, staging o producción), y realiza los siguientes pasos en orden:  • Conexión a la máquina y obtención del código fuente: El pipeline se conecta automáticamente a la máquina y se actualiza para obtener la última versión del código fuente desde el repositorio. Esto asegura que siempre se trabajará con la versión más actual del código.  • Generación de los microservicios: Una vez obtenido el código, se procede con la construcción de los microservicios. En este paso, se crean las versiones actualizadas de los microservicios, asegurando que todo el sistema esté listo para ejecutarse con los últimos cambios.  • Despliegue en el entorno adecuado:  o Desarrollo: Si el entorno es de desarrollo, el pipeline simplemente ejecuta un script para levantar los servicios necesarios. Esto permite que los desarrolladores trabajen rápidamente en el entorno local y validen sus cambios.  o Staging o Producción: Si el entorno es de staging o producción, el pipeline va un paso más allá. Publica las imágenes de los microservicios a ECR (Elastic Container Registry) de AWS, donde las imágenes se almacenan de forma segura y centralizada. Posteriormente, se conecta a la máquina de destino y lee las imágenes almacenadas en ECR para actualizar el entorno con las últimas versiones de los microservicios, asegurando que los cambios estén reﬂejados en el entorno en vivo.  Este enfoque garantiza que, independientemente del entorno, el proceso de despliegue sea eﬁciente, controlado y escalable, permitiendo a los equipos de desarrollo centrarse en la creación de nuevas funcionalidades y mejoras sin preocuparse por los detalles del despliegue manual.  
8.3 Monitorización y logs  La correcta gestión de los logs es esencial para la monitorización, depuración y análisis de los servicios en un entorno de producción. Cada microservicio en el sistema está conﬁgurado para generar logs en diferentes niveles de severidad, lo que facilita la identiﬁcación de problemas y el monitoreo del estado general de los servicios. Los niveles de log más comunes utilizados son:  • DEBUG: Este nivel proporciona información detallada sobre el ﬂujo de ejecución del sistema. Está orientado principalmente al diagnóstico durante el desarrollo y la resolución de


---

## Página 34


Documento Técnico 
 
 34 
problemas. No debe estar habilitado en producción debido a la cantidad de información generada.  • INFO: Los mensajes de información informan sobre el estado general del servicio, como el inicio o la ﬁnalización de operaciones importantes, así como otros eventos relevantes del sistema que no indican ningún problema.  • WARNING: Los mensajes de advertencia indican situaciones que no son críticas pero que podrían llevar a problemas si no se atienden. Son señales de que algo no funciona como se esperaba, pero el sistema sigue funcionando.  • ERROR: Este nivel de log se utiliza para capturar fallos y errores que afectan el funcionamiento del servicio, aunque no siempre son críticos para la operación del sistema. Los errores se registran para ser corregidos por el equipo de desarrollo.  • TRACE: Este nivel de log proporciona información extremadamente detallada y granular sobre el comportamiento del sistema. Es útil para el diagnóstico a nivel muy bajo y, al igual que el DEBUG, se recomienda solo en entornos de desarrollo.  8.3.1 Almacenamiento y Gestión de Logs  Cada servicio genera estos logs tanto en la consola (para facilitar el acceso en tiempo real durante el desarrollo y la ejecución de pruebas) como en archivos locales. Los archivos de log generados por cada servicio son almacenados de manera individual para poder hacer un seguimiento detallado de cada uno de ellos.  Posteriormente, los logs generados por los servicios son enviados a un bucket de S3 de AWS, donde se centralizan para su almacenamiento y análisis a largo plazo. Este enfoque facilita la recopilación y consulta de los logs sin la necesidad de acceder directamente a las máquinas o servicios individuales. El uso de S3 permite un almacenamiento seguro, escalable y duradero de los logs, lo que es ideal para mantener un historial accesible y fácil de gestionar.  
8.4 Monitorización  Se implementará una monitorización a nivel de infraestructura utilizando el stack de servicios de AWS. Esto incluirá la supervisión del rendimiento y la salud de la infraestructura subyacente, como instancias EC2, bases de datos, redes y otros recursos de AWS. Esta monitorización complementará los logs de los servicios y permitirá obtener una visión más completa del estado del sistema en su conjunto.


---

## Página 35


Documento Técnico 
 
 35 
9 PREGUNTAS FRECUENTES (FAQ) ¿Qué es la tecnología blockchain y en qué me beneficia? La tecnología blockchain permite crear redes distribuidas, descentralizadas y seguras que registran transacciones cifradas de forma cronológica e inalterable. A diferencia de los sistemas tradicionales, estas redes no dependen de una autoridad central: la propia tecnología garantiza la veracidad de los datos y transacciones en tiempo real, sin necesidad de intermediarios. Gracias a esta estructura, se generan relaciones de conﬁanza entre los participantes, lo que facilita procesos clave como la autenticación, la veriﬁcación de activos digitalizados o la gestión de identidades. Todo ello de manera eﬁciente, segura y ágil, reduciendo costes y aumentando la transparencia. Además, en línea con los estándares de la Web3, esta tecnología habilita el uso de identidades digitales descentralizadas, que permiten establecer un modelo completamente nuevo, seguro y conﬁable para gestionar relaciones entre agentes en internet, ya sean individuos, organizaciones o dispositivos (como IoT, agentes de inteligencia artiﬁcial, entre otros).  ¿Qué es la Identidad Digital Descentralizada o Web3? La Identidad Digital Descentralizada (DID, por sus siglas en inglés) es un nuevo modelo de gestión de identidad que, gracias al uso de tecnología blockchain, permite a personas y organizaciones controlar sus propios datos de forma segura y autónoma. Este enfoque simpliﬁca los procesos de identiﬁcación electrónica y facilita la veriﬁcación automática de información, eliminando intermediarios y reduciendo riesgos de fraude o suplantación. En el contexto de Web3, la identidad se convierte en un activo interoperable, portátil y veriﬁcable en múltiples plataformas digitales. En este modelo, los usuarios gestionan su identidad a través de un wallet digital o “billetera de credenciales” . ¿Qué es un wallet de identidad digital descentralizada y cómo funciona? El wallet o cartera de credenciales veriﬁcables en un entorno Web3 es la aplicación o interfaz que permite a los usuarios —ya sean ciudadanos (personas físicas) o empresas (personas jurídicas)— gestionar su identidad digital de forma uniﬁcada. A diferencia del modelo tradicional, en el que se establecen múltiples relaciones 1:1 con distintos servicios, este enfoque permite que los usuarios dispongan de una única identidad (relación 1:N) para interactuar con múltiples plataformas y aplicaciones, garantizando mayor control, privacidad y portabilidad de los datos personales.  ¿Qué interfaces de usuario ofrecen los wallet de Sybol?   Sybol está diseñado para todo tipo de usuarios. Ofrece interfaces adaptadas a cada perﬁl:  • Organizaciones (personas jurídicas): aplicación de escritorio para gestionar múltiples identidades y representantes dentro de grandes empresas.  • Personas físicas, autónomos y consumidores: una versión APP móvil (en desarrollo) para la gestión básica de credenciales con una gran usabilidad y portabilidad.


---

## Página 36


Documento Técnico 
 
 36 
¿Qué son las Credenciales Verificables (VCs)?   Son credenciales digitales seguras, veriﬁcables y resistentes a manipulaciones, vinculadas a las identidades digitales tanto del emisor como del receptor. Estas credenciales pueden ser emitidas por instituciones públicas o empresas privadas. El marco de gobernanza y conﬁanza de Sybol garantiza relaciones ﬁables entre emisores reconocidos y registrados, y las Credenciales Veriﬁcables que estos generan.  ¿Para qué sirven las Credenciales Verificables?   El sistema de credenciales digitales de Sybol permite a empresas y consumidores veriﬁcar en línea si una credencial es auténtica y válida. Las Credenciales Sybol pueden utilizarse como distintivo comercial —por ejemplo, para demostrar cumplimiento o calidad— o como mecanismo de control en procesos de cumplimiento normativo en tiempo real, así como en veriﬁcaciones KYC (Conoce a tu Cliente) y KYB (Conoce a tu Empresa).  ¿Cómo se intercambian (envían/reciben) las Credenciales Verificables?   Sybol establece un canal de comunicación wallet-to-wallet que conecta de forma segura y ﬂuida a emisores, usuarios y receptores de credenciales de identidad veriﬁcables (VCs). Por ejemplo, las credenciales energéticas permiten a terceros —como reguladores, proveedores de servicios o socios— veriﬁcar en tiempo real la autenticidad de políticas relacionadas con la energía. Esto facilita procesos de cumplimiento normativo, auditoría y conﬁanza entre partes sin necesidad de intermediarios.  ¿Qué formatos tienen las credenciales verificables y como pueden utilizarse?   Una credencial veriﬁcable representa un atributo de identidad digital, como un certiﬁcado de formación, y puede presentarse en tres formatos distintos según el tipo de información que se necesite compartir:  • Evidencia ZKP (Zero-Knowledge Proof): Permite veriﬁcar una condición sin revelar el dato completo. Ejemplos: ¿Tienes más de 18 años?, ¿Has completado el curso de ciberseguridad? Y con respuestas tipo: sí/no, apto/no apto, OK/KO.  • Dato: Proporciona un valor concreto como un número, código, fecha o puntuación. Ejemplos: ¿Cuál es tu fecha de nacimiento?, ¿Qué puntuación obtuviste en el curso?, ¿Cuál es tu número de DNI?  • Documento: Un archivo o representación “física” (por ejemplo, PDF) que contiene todos los datos de la credencial. Puede formar parte del hash criptográﬁco de la propia credencial para garantizar que el documento sea único, veriﬁcable e infalsiﬁcable.  ¿Qué es un hash y qué función cumple en una credencial verificable?


---

## Página 37


Documento Técnico 
 
 37 
Un hash es un código criptográﬁco alfanumérico que representa de forma única el registro de una transacción dentro de un bloque de blockchain. En el caso de una credencial de identidad, como un certiﬁcado de formación, el hash se genera a partir de la combinación de:   • Los metadatos de la credencial (como fecha, tipo, emisor, etc.)    • El DID (Identiﬁcador Descentralizado) de la entidad emisora    • El DID del titular (propietario de la credencial)  Este hash garantiza que la credencial es única, no ha sido alterada y puede veriﬁcarse de forma segura y transparente en la red blockchain.  ¿Cómo beneficia el modelo de identidad digital descentralizada a todos los actores del ecosistema digital?   El modelo de identidad digital descentralizada se apoya en un sistema de incentivos circulares que garantiza su escalabilidad y sostenibilidad, ofreciendo beneﬁcios transversales en distintas dimensiones:  • Eﬁciencia: Elimina procesos duplicados, reduce errores y fraudes, y simpliﬁca los ﬂujos de trabajo.  • Impacto social: Mejora la experiencia del usuario, acercando a ciudadanos y empresas a las ventajas de la Web3.  • Competitividad a nivel sectorial: Impulsa nuevos modelos de negocio y facilita interacciones más ágiles en todo el entorno empresarial y profesional.  ¿Cómo construye confianza Sybol sin necesidad de intermediarios?  Sybol permite establecer relaciones de conﬁanza de forma directa mediante credenciales veriﬁcables. Una entidad reconocida puede emitir una credencial digital (como un certiﬁcado de formación o una acreditación energética) que el usuario guarda en su wallet. Desde allí, puede consultarla, compartirla directamente con terceros (wallet-to-wallet) y demostrar su validez en tiempo real. Los receptores pueden veriﬁcar su autenticidad a través de la red blockchain, sin necesidad de contactar al emisor original, comprobando la identidad del emisor y del titular, así como la validez y trazabilidad de la credencial.


---

## Página 38


Documento Técnico 
 
 38