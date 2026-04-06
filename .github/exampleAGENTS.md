# AGENTS.md

# Academic purpose only section

## Qué debe contener

Aquí pondría solo reglas transversales, no detalle fino de Angular o Express.

## Ideas de contenido
Arquitectura general del repo.
Regla de separación de responsabilidades entre Angular, Express y CDK.
Cómo tratar cambios full stack.
Política de pruebas mínimas.
Política de cambios en contratos API.
Política de cambios en infraestructura.
Regla de no sobredelegar si la tarea es pequeña.
Formato de respuesta esperado: cambios, impacto, riesgos, tests.

# ¿Dónde va este fichero?

Es lo mismo que el fichero  .github/copilot-instructions.md con la diferencia de que 
es posible tener más de un agents, ya que podrías tener el global (va en root) y además
podrías tener instrucciones que hagan override para áreas especídicas.


## Objetivo

Este repositorio contiene una aplicación con tres áreas principales:

- **Angular** — frontend (`apps/angular-app/`)
- **Express** — backend (`services/express-api/`)
- **CDK** — infraestructura AWS (`infra/cdk/`)

## Reglas globales

- Antes de proponer código nuevo, busca patrones existentes en el repositorio.
- Si una tarea afecta a más de una capa, explicita el impacto por capa.
- No inventes contratos API si ya existe un tipo, DTO o esquema equivalente.
- Mantén los cambios pequeños y enfocados.
- Señala siempre riesgos, supuestos y pruebas faltantes.
- No mezcles cambios de infraestructura con cambios funcionales si no es necesario.
- Si cambias un contrato entre frontend y backend, revisa consumidor y productor.
- Prioriza compatibilidad hacia atrás cuando sea razonable.

## Separación de responsabilidades

| Capa | Responsabilidad |
|------|-----------------|
| Angular | UI, servicios HTTP, estado, rutas, guards, formularios |
| Express | Rutas REST, controllers, servicios, DTOs, validación, autenticación |
| CDK | Recursos cloud, IAM, secretos, networking, configuración de entornos |

Ninguna capa debe asumir lógica que pertenece a otra. Los contratos entre capas se definen explícitamente (DTOs, schemas) y se mantienen sincronizados.

## Cambios full stack

Cuando una tarea afecte a más de una capa:

1. Identifica todas las capas impactadas antes de escribir código.
2. Empieza por el contrato (DTO / schema / endpoint) antes de implementar.
3. Propaga el cambio en orden: contrato → backend → frontend → infra si aplica.
4. Usa el agente `app-orchestrator` para coordinar tareas multi-capa.

## Política de pruebas mínimas

- **Frontend**: tests unitarios de todo componente o servicio nuevo o modificado.
- **Backend**: tests unitarios de servicios y tests de integración de rutas nuevas.
- **Infra**: `cdk diff` revisado y documentado antes de cualquier deploy.
- No se hace PR sin haber ejecutado los tests del área afectada.

## Política de cambios en contratos API

- Ningún cambio de endpoint, DTO o método HTTP se hace sin actualizar ambos lados (Express y Angular).
- Los cambios breaking en la API requieren revisión del agente `integration-reviewer`.
- Documentar siempre si el cambio es backward-compatible o no.

## Política de cambios en infraestructura

- Todo cambio en `infra/cdk/` debe indicar impacto en cada entorno (dev / staging / prod).
- Los cambios destructivos en CDK requieren aprobación manual antes de ejecutar `cdk deploy`.
- No ejecutar migraciones de base de datos automáticamente en producción.
- Documentar el rollback siempre que haya cambios que no se puedan revertir fácilmente.

## Delegación recomendada

Usa el agente especialista adecuado para cada área:

- `frontend-angular` — UI, servicios frontend, rutas, guards y formularios.
- `backend-express` — rutas, controllers, servicios, DTOs, validación y errores.
- `infra-cdk` — recursos cloud, IAM, secretos, networking y despliegues.
- `integration-reviewer` — cuando una tarea afecte a varias capas o cambie contratos.
- `app-orchestrator` — cualquier tarea multi-stack o que requiera coordinación.

> No uses un agente especialista si la tarea es pequeña y autocontenida en una sola capa. Resuélvela directamente.

## Formato de respuesta esperado

Cuando termines una tarea:

1. **Qué se ha cambiado** — lista concisa de ficheros y lógica modificada.
2. **Impacto por capa** — indica si afecta a Angular, Express o CDK.
3. **Riesgos y supuestos** — qué puede fallar, qué se ha asumido.
4. **Pruebas** — qué tests se han ejecutado o cuáles faltan.
