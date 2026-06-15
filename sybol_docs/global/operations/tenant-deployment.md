Alta nuevo Tenant / Challenge a GUIA_OPERATIVA_MULTI_TENANT.md
 
Basicamente voy a anotar todos los pasos dados siguiendo la guia GUIA_OPERATIVA_MULTI_TENANT, para ver si soy capaz de levantar un nuevo tenant de forma exitosa. Ire apuntando los errores, fallo y comentarios para intentar actualizar la guia.
 
El tenant de wallet a levantar se denomina Solred.
 
Antes de empezar será necesario configurar en AWS una serie de servicios nuevos (dominio, cloudfront, s3, usuario de cognito, secrets manager, role de IAM, kms key). Y a nivel de wallet habra que configurar el did-document nuevo (postman) y el perfil de base de datos (script de sql y entrada inciial de contact).
 
Accesos necesarios: AWS, postman, RDS (Abrir puertos)

1.1  Crear subdominio

Crear record, el valor de staging es porque estamos en staging, en produccion habra que poner el correspondiente en produccion.

No veo que tenga sentido crera el record primero si no hay valor al que apuntar. Cambiar el orden para cuando este todo lo necesario para crear el record o el subdominio. Prosigo con el 1.2.

1.2 Solicitar certificado ACM

Veo que se indica con la etiqueta de IMPORTANTE, que el ceritifcado debe estar en la region us-east-1. Eso debera indicarse ANTES de ir a crear el certificado. Si hay que vovler luego a una region especifica (eu-west-1 osea Ireland) habra que indicarlo de nuevo. 

2.1 Crear s3 bucket
Hay que especificar en los textos que no se va a crear un bucket, si no una folder dentro del bucket indicado con el nombr edel tenant-id, asi que el punto 2 de ocnfiguracion no aplica. Este paso sera solo crear la folder en sybol-statics/wwc-staging/{tenantid}. Para el caso de produccion se sustituira por staging.

2.2 Crear CloudFront Distribution
La guia esta bastante mal indicada. Voy a poner paso a pasao lo que me va saliendo y que voy configurando para que se sustituya por lo que hay en el 2.2
Primero al darle a create distribution, sale los modelos de pricing. Hay que elegir unos que se llama payasyougo que sale abajo. Luego se indica el nombre de la distribution: StagingSolred para staging, en pro sera solo el nombre de la compañia (Solred). En descripcion pondremos lo mismo. Luego seleccionaremos single website or app. Y luego nos pedira introducir un domain, metermos el usado para el certificado: 	
solred.staging.wallet.sybol.id
Luego todavia en el flujo de creacion nos pedira un origin. Elegiremos amazon s3 y seleccionaremos el s3 sybol-statics. en el path indicaremos el path hasts la nueva carpeta creada en el s3 añadiendo latest: /wwc-staging/{tenantid}/latest. El resto de configuracion de origin lo dejamos como esta (allow private s3 bucket access to cloudfornt , origin settings - use recommended, cache setting - use recommended)
Luego saldra la pantalla de enable security a lo que seleccionaremos do not enable security protections (WAF).
Luego saldra la pantalla de configurar ceritificado tls, y indicaeremos el certificado creado en esta guia y con este paso acabaria el formulario de creacion de distributions. Pero hay que editar ahora mas configuraciones:

 1. En la pestaña general de la distribution, editar:
  1.1 Default root object: introducir index.html y guardar cambios
 2. En la pestaña de origins, hay que crear un nuevo origin:
  2.1 En origin domain introduciremos la url del api correspondiente por entorno: api.staging.wallet.sybol.id (en produccion pondremos la que corresponda) 
  2.2 Dejaremos el protocolo en https only, tls1.2, y asi se quedara y le daremos a create origin
 3. En la pestaña de BEHAVIOURS dos cosas:
  3.1 Editar el behaviour existente del s3:
    3.1.1 Abajo del todo, en function associations, en viewer request seleccionar Cloudfront functions, y seleccionar la function llamada: SPA_routes_handler
  3.2 Crear Behavior
    3.2.1 Poner en path pattern: /api/*, poner en origin and origin groups el origin api.staging.wallet.sybol.id (o el correspondiente en produccion), Poner en cache policy: CachingDisabled, en Origin request policy: AllViewerExceptHostHeeader y en response headers policy: CORST-with-preflight-adn-SecurityHeadersPolicy, y crear behaviour.

Hasta aqui el punto 2.2. Modifica lo que habia.

2.3 y 2.4 son correctos, pero como he dicho antes el 2.4 que seria añadir al record del route 53 el alias del nuevo distribution, se veera afectado por el cambio de orden, pudiendose a pairtir de este momento crearse el record en route 53 si no entiendo mal. 

3. Usuario en cognito

Este apartado va a tener dos versiones. A veces algunos usuarios habra que crearlos a mano pero en produccion algunos usuarios vendran dados por el onboarding y ya estaran creados en cognito, pero habra que editarlos para añadir los atributos custom. 

Si ya existen solo habra que editar sus atributos y añadir custom:tenant_id = {tenantId} y custom:role = {role}, si no existen habra que seguir la guia que es correcta, asi que mantener esos apartados.

4. Database RDS

Respecto a este apartado, esta muy bien documentado. Me gustaria que se hiciera referncia al lugar donde esta el schema.sql cuando hay que usarlo que seria en el apartado 4.6. La ruta es en services/businessLogic/database/schema_v2.sql. Indica que en el schema_v2.sql hay que cambiar el literal '{tenantId}' por el tenantid correspondiente

Tambien, he creado un nuevo sql que se llama setup.sql en el que he recopilado todos los comandos por orden hasta llegar al 4.6 desde que te conectas a la base de datos de tenant_{tenantId}, por si puedes referenciarlo pero sin quitar nada de lo que esta ya indicado pero que ha que cambiar solred por {tenantid}. 

5. Secrets Manager
 En 5.1 Crear SEcret Admin
 En el aparto de credentials, se indica usar la password generada en el paso 4.2. Estaria bien entonces qeu en el paso 4.2 indicara expresamente que hay que anotrala o guardarla para usarla aqui. 
 En el apartado 4. Database, pone select sybol-cluster, poner que se seleccionara la correspondiente segun el entorno.
 Ene l apartado 7. Configure rotation, indicar que si no existe la rotatio function, es porque hay un fallo en el core setup y habra que crearla.

 Antes del 5.2, se habal de crear el campo dbname, te paso aqui el literal que  hay que añadir al editar en plaintext el secret creado: '"dbname": "tenant_tritemius"'

 El resto de secret manager lo veo correcto

6. IAM roles del tenant

