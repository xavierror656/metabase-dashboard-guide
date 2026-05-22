
Actúa como arquitecto senior de BI, Metabase API y MongoDB Analytics.

Necesito que construyas una solución de dashboards para la Plataforma de Gestión Digital SSPM_dashboard usando Metabase como capa principal de visualización y MongoDB como fuente de datos.

Contexto técnico:
Ya existe un proceso de vistas materializadas en MongoDB.

Base origen:
- SSPM_dashboard.ParteInformativa

Base analítica:
- SSPM_dashboard_vistas

La estructura original de ParteInformativa usa un arreglo campos[] con claves PI_1 a PI_53, pero el script de materialización ya convierte esos datos en colecciones planas, limpias y consumibles por BI.

Colecciones/vistas principales disponibles:
- mv_resumen_pi
- mv_delitos_distrito
- mv_temporal
- mv_operativa
- mv_er_agentes
- mv_er_detenidos
- mv_er_victimas
- mv_er_armas
- mv_er_vehiculos
- mv_er_sustancias
- mv_er_emergencias
- mv_er_clasi_hechos
- mv_er_faltas_admin
- mv_er_objetos
- mv_iph
- mv_ubicacion
- mv_reporte_detenidos_faltas
- mv_excel_faltas_informativas
- mv_puestas_ordenes_vehiculos
- vista_departamento_estadisticas
- mv_armasyordenesreporte
- mv_reporte_vehiculos_general
- mv_bitacora_armas
- mv_menores_delitos
- mv_metadata

Objetivo:
Crear dashboards profesionales en Metabase usando la API de Metabase para automatizar:

1. Conexión a MongoDB
2. Sincronización de metadata
3. Creación de colecciones de Metabase
4. Creación de preguntas/cards
5. Creación de dashboards
6. Inserción de cards en dashboards
7. Creación de filtros globales
8. Mapeo de filtros a campos
9. Organización visual de dashboards
10. Permisos básicos por colección
11. Exportación/documentación del setup

- METABASE_COLLECTION_PREFIX=SSPM_dashboard

Arquitectura deseada:

MongoDB:
SSPM_dashboard.ParteInformativa
    ↓ proceso ETL/materialización
SSPM_dashboard_vistas.mv_*

Metabase:
Database: SSPM_dashboard Vistas MongoDB
Collections:
- SSPM_dashboard / 00 Ejecutivo
- SSPM_dashboard / 01 Operativo
- SSPM_dashboard / 02 Delitos
- SSPM_dashboard / 03 Faltas Administrativas
- SSPM_dashboard / 04 Detenidos
- SSPM_dashboard / 05 Víctimas
- SSPM_dashboard / 06 Vehículos
- SSPM_dashboard / 07 Armas
- SSPM_dashboard / 08 Sustancias
- SSPM_dashboard / 09 Objetos
- SSPM_dashboard / 10 Agentes
- SSPM_dashboard / 11 Emergencias
- SSPM_dashboard / 12 Geoespacial
- SSPM_dashboard / 13 Reportes Oficiales

Dashboards a crear:

1. Dashboard Ejecutivo General

Colección:
SSPM_dashboard / 00 Ejecutivo

Fuente principal:
- mv_resumen_pi
- mv_temporal
- mv_operativa
- mv_ubicacion

Cards/KPIs:
- Total de Partes Informativas
- Total de detenidos
- Total de víctimas
- Total de armas aseguradas
- Total de vehículos involucrados
- Total de sustancias aseguradas
- Total de objetos asegurados
- Total de eventos con coordenadas

Gráficas:
- Eventos por mes
  Fuente: mv_temporal
  Agrupar por: anio_mes
  Métrica: count
  Tipo: line/bar

- Eventos por distrito
  Fuente: mv_resumen_pi
  Agrupar por: distrito
  Métrica: count
  Tipo: bar

- Eventos por turno
  Fuente: mv_resumen_pi
  Agrupar por: turno
  Métrica: count
  Tipo: pie/bar

- Motivos de intervención
  Fuente: mv_resumen_pi
  Agrupar por: motivo_intervencion
  Métrica: count
  Tipo: bar

- Top colonias
  Fuente: mv_resumen_pi
  Agrupar por: colonia
  Métrica: count
  Orden: descendente
  Límite: 10

- Mapa de eventos
  Fuente: mv_ubicacion
  Campos: latitud, longitud, distrito, colonia, folio, fecha_evento, motivo_intervencion

Filtros globales:
- fecha_evento
- distrito
- turno
- sector
- colonia
- motivo_intervencion
- estatus

2. Dashboard Operativo

Fuente:
- mv_operativa
- mv_er_agentes
- mv_resumen_pi

Cards:
- Total eventos operativos
- Total participaciones de agentes
- Promedio de agentes por evento
- Total detenidos por turno
- Total víctimas por turno
- Total armas por turno

Gráficas:
- Carga operativa por distrito y turno
- Agentes por unidad
- Participaciones por puesto
- Participaciones por agente
- Detenidos por distrito/turno
- Armas por distrito/turno

3. Dashboard Delitos

Fuente:
- mv_er_clasi_hechos
- mv_delitos_distrito
- mv_ubicacion

Cards:
- Total delitos
- Total delitos con violencia
- Total órdenes de aprehensión
- Total por clasificación
- Distrito con más delitos

Gráficas:
- Top delitos por nombre_delito
- Delitos por clasificación_delito
- Delitos por distrito
- Delitos por modalidad
- Delitos con violencia vs sin violencia
- Delitos por mes
- Mapa de delitos

Tabla:
- folio
- fecha_evento
- distrito
- colonia
- nombre_delito
- nombre_subdelito
- clasificacion_delito
- modalidad
- hubo_violencia
- orden_aprehension

4. Dashboard Faltas Administrativas

Fuente:
- mv_er_faltas_admin
- mv_reporte_detenidos_faltas
- mv_excel_faltas_informativas

Cards:
- Total faltas administrativas
- Total detenidos por faltas
- Distrito con más faltas
- Clasificación más frecuente
- Fracción más frecuente

Gráficas:
- Faltas por distrito
- Faltas por clasificación
- Faltas por fracción
- Faltas por turno
- Faltas por colonia
- Tendencia mensual

5. Dashboard Detenidos

Fuente:
- mv_er_detenidos

Cards:
- Total detenidos
- Promedio de edad
- Detenidos por género
- Detenidos con atención médica
- Detenidos por fuero
- Detenidos por situación jurídica

Gráficas:
- Detenidos por distrito
- Detenidos por género
- Detenidos por rango de edad
- Detenidos por presentado_ante
- Detenidos por fuero
- Detenidos por país_origen / estado_origen / ciudad_origen

Crear campo calculado o query para rango de edad:
- 0-17: Menor de edad
- 18-29: Joven
- 30-44: Adulto
- 45-59: Adulto maduro
- 60+: Adulto mayor

Importante:
Por protección de datos, las cards públicas no deben mostrar nombre completo de detenidos salvo en dashboards restringidos.

6. Dashboard Víctimas

Fuente:
- mv_er_victimas

Cards:
- Total víctimas
- Víctimas por género
- Víctimas con atención médica
- Víctimas con atención psicológica
- Víctimas con atención legal
- Delito más frecuente asociado a víctima

Gráficas:
- Víctimas por distrito
- Víctimas por delito
- Víctimas por género
- Víctimas por edad
- Víctimas por canalización
- Víctimas por origen

Regla:
Anonimizar nombres en vistas generales.

7. Dashboard Vehículos

Fuente:
- mv_er_vehiculos
- mv_reporte_vehiculos_general

Cards:
- Total vehículos
- Marca más frecuente
- Tipo más frecuente
- Modelo más frecuente
- Motivo de aseguramiento más frecuente
- Entidad de emplacado más frecuente

Gráficas:
- Vehículos por distrito
- Vehículos por marca
- Vehículos por tipo
- Vehículos por color
- Vehículos por entidad_emplacado
- Vehículos por motivo_aseguramiento
- Mapa de vehículos

8. Dashboard Armas

Fuente:
- mv_er_armas
- mv_armasyordenesreporte
- mv_bitacora_armas

Cards:
- Total armas aseguradas
- Tipo de arma más frecuente
- Calibre más frecuente
- Distrito con más armas
- Total por clasificación

Gráficas:
- Armas por distrito
- Armas por tipo_arma
- Armas por calibre_arma
- Armas por clasificación_arma
- Armas por colonia
- Tendencia mensual

9. Dashboard Sustancias

Fuente:
- mv_er_sustancias

Cards:
- Total registros de sustancias
- Total cantidad_sustancia
- Total gramos
- Total kilogramos
- Sustancia más frecuente
- Distrito con más aseguramientos

Gráficas:
- Sustancias por distrito
- Sustancias por tipo_sustancia
- Peso total por sustancia
- Sustancias por unidad_medida
- Sustancias por colonia
- Tendencia mensual

10. Dashboard Objetos

Fuente:
- mv_er_objetos

Cards:
- Total objetos asegurados
- Tipo de objeto más frecuente
- Cantidad total
- Distrito con más objetos
- Colonia con más objetos

Gráficas:
- Objetos por tipo_objeto
- Objetos por distrito
- Objetos por colonia
- Objetos por unidad_medida

11. Dashboard Emergencias

Fuente:
- mv_er_emergencias

Cards:
- Total emergencias
- Tipo más frecuente
- Clasificación más frecuente
- Distrito con más emergencias
- Colonia con más emergencias

Gráficas:
- Emergencias por tipo
- Emergencias por clasificación
- Emergencias por distrito
- Emergencias por colonia
- Emergencias por turno
- Tendencia mensual

12. Dashboard Geoespacial

Fuente:
- mv_ubicacion

Cards:
- Total eventos georreferenciados
- Eventos sin coordenadas
- Distrito con mayor concentración
- Colonia con mayor concentración

Visualizaciones:
- Mapa de puntos
- Mapa agrupado por distrito
- Tabla de eventos georreferenciados

Tooltip del mapa:
- folio
- fecha_evento
- hora_evento
- distrito
- colonia
- motivo_intervencion
- cantidad_detenidos
- cantidad_armas
- cantidad_sustancias

13. Dashboard Reportes Oficiales

Fuente:
- mv_reporte_detenidos_faltas
- mv_excel_faltas_informativas
- mv_puestas_ordenes_vehiculos
- vista_departamento_estadisticas
- mv_armasyordenesreporte
- mv_reporte_vehiculos_general
- mv_bitacora_armas
- mv_menores_delitos

Cards/tablas:
- Reporte detenidos + faltas
- Excel faltas informativas
- Puestas, órdenes y vehículos
- Departamento de estadísticas
- Armas y órdenes
- Vehículos general
- Bitácora de armas
- Menores delitos

Debe incluir exportación CSV/XLSX desde Metabase.

Lógica API Metabase:

Crear un script en Python o Node.js que haga:

1. Login:
POST /api/session
Guardar X-Metabase-Session

2. Verificar conexión MongoDB:
GET /api/database

3. Crear database si no existe:
POST /api/database

Nombre:
SSPM_dashboard Vistas MongoDB

Engine:
mongo

Details:
- host
- port
- dbname: SSPM_dashboard_vistas
- user
- password
- authdb
- ssl según configuración

4. Sincronizar metadata:
POST /api/database/{database_id}/sync_schema
POST /api/database/{database_id}/rescan_values

5. Crear collections:
POST /api/collection

Crear:
SSPM_dashboard_dashboard / 
SSPM_dashboard / 00 Ejecutivo
SSPM_dashboard / 01 Operativo
SSPM_dashboard / 02 Delitos
SSPM_dashboard / 03 Faltas Administrativas
SSPM_dashboard / 04 Detenidos
SSPM_dashboard / 05 Víctimas
SSPM_dashboard / 06 Vehículos
SSPM_dashboard / 07 Armas
SSPM_dashboard / 08 Sustancias
SSPM_dashboard / 09 Objetos
SSPM_dashboard / 10 Agentes
SSPM_dashboard / 11 Emergencias
SSPM_dashboard / 12 Geoespacial
SSPM_dashboard / 13 Reportes Oficiales

6. Crear cards/questions:
POST /api/card

Cada card debe tener:
- name
- description
- collection_id
- dataset_query
- display
- visualization_settings

Usar dataset_query de tipo query builder cuando sea posible.
Usar native MongoDB aggregation cuando se requiera lógica avanzada.

7. Crear dashboards:
POST /api/dashboard

8. Insertar cards en dashboards:
POST /api/dashboard/{dashboard_id}/cards

9. Crear filtros del dashboard:
PUT /api/dashboard/{dashboard_id}

Filtros estándar:
- Fecha
- Distrito
- Turno
- Sector
- Colonia
- Motivo intervención
- Estatus

10. Mapear filtros a cada card:
PUT /api/dashboard/{dashboard_id}/cards/{dashcard_id}

Cada filtro debe conectarse al campo correspondiente de la colección usada por la card.

Reglas de diseño:
- Usar layouts ejecutivos.
- KPIs arriba.
- Gráficas en medio.
- Tablas abajo.
- Mapas en dashboards geográficos.
- Filtros globales arriba.
- Usar nombres claros y entendibles para dirección.

Reglas de seguridad:
- No exponer nombres completos de víctimas en dashboards generales.
- No exponer narrativa completa de hechos en dashboards públicos.
- Crear una colección restringida para tablas con datos personales.
- Separar dashboards ejecutivos de dashboards operativos.
- Preparar roles sugeridos:
  - Dirección
  - Estadística
  - Operativo
  - Consulta
  - Administrador

Performance:
Usar preferentemente las colecciones materializadas, no ParteInformativa directamente.
Evitar consultas con arrays anidados.
Evitar lookups pesados dentro de Metabase.
Usar mv_resumen_pi como fact principal.
Usar mv_er_* como tablas de entidades.
Usar mv_temporal para análisis temporal.
Usar mv_ubicacion para mapas.
Usar reportes oficiales ya materializados para exportaciones.

Índices esperados en MongoDB:
- mv_resumen_pi: distrito + fecha_evento
- mv_resumen_pi: motivo_intervencion
- mv_resumen_pi: turno
- mv_resumen_pi: estatus
- mv_temporal: anio_mes + distrito
- mv_operativa: distrito + turno
- mv_er_detenidos: genero, fuero, presentado_ante
- mv_er_victimas: genero + delito
- mv_er_armas: tipo_arma, clasificacion_arma
- mv_er_vehiculos: placas, marca, tipo
- mv_er_sustancias: tipo_sustancia
- mv_er_emergencias: clasificacion, tipo
- mv_er_clasi_hechos: nombre_delito, clasificacion_delito
- mv_er_faltas_admin: clasificacion
- mv_er_objetos: tipo_objeto
- mv_ubicacion: índice geoespacial 2dsphere sobre ubicacion

Entregables esperados:
1. Script completo para crear dashboards en Metabase vía API.
2. Archivo de configuración JSON/YAML con definición de dashboards y cards.
3. Funciones reutilizables:
   - loginMetabase()
   - getOrCreateDatabase()
   - syncDatabase()
   - getOrCreateCollection()
   - createCard()
   - createDashboard()
   - addCardToDashboard()
   - createDashboardFilters()
   - mapFilterToCard()
4. Lista de cards por dashboard.
5. Queries MongoDB Aggregation por card.
6. Layout recomendado por dashboard.
7. Instrucciones para ejecutar.
8. Validación final de que todos los dashboards fueron creados.
9. Manejo de errores si una card ya existe.
10. Modo dry-run para revisar antes de crear.

Importante:
El resultado debe estar listo para producción, pero parametrizado para que pueda ejecutarse primero en ambiente beta.
No uses directamente SSPM_dashboard.ParteInformativa para dashboards salvo diagnóstico técnico.
Usa SSPM_dashboard_vistas como única fuente BI.
```

## Ajuste clave de lógica

Tu flujo debería quedar así:

```text
Laravel / MongoDB actual
        ↓
Script materializador
        ↓
SSPM_dashboard_vistas.mv_*
        ↓
Metabase conectado a SSPM_dashboard_vistas
        ↓
Metabase API crea cards + dashboards
        ↓
Usuarios consultan dashboards / exportan reportes
```

No así:

```text
Dashboard consulta ParteInformativa directo
```

Eso te va a meter problemas con `campos[]`, arrays anidados, rendimiento y filtros inconsistentes.

## Mini prompt extra para que te genere el script de automatización

```text
Genera un script en Python para automatizar Metabase API.

Debe:
1. Leer variables de entorno.
2. Hacer login en Metabase.
3. Buscar si existe la database "SSPM_dashboard Vistas MongoDB".
4. Si no existe, crearla conectando a MongoDB database "SSPM_dashboard_vistas".
5. Sincronizar schema.
6. Crear collections SSPM_dashboard.
7. Crear dashboards.
8. Crear cards usando MongoDB aggregations sobre colecciones mv_*.
9. Agregar cards a dashboards con layout.
10. Crear filtros globales y mapearlos.
11. Evitar duplicados si ya existen.
12. Tener modo DRY_RUN=true.
13. Mostrar resumen final.

Usa requests, python-dotenv y logging.
Entrega el código completo con comentarios.
```

La decisión más importante: **Metabase debe leer colecciones ya materializadas**, no reconstruir la lógica pesada en cada visualización. Eso hace el sistema más rápido, más estable y más fácil de mantener.
