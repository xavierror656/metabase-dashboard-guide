# Informe: Dashboard 17 — ESTADÍSTICAS COMPLETAS

## 1. Información General

| Campo | Valor |
|-------|-------|
| ID | 17 |
| Nombre | ESTADÍSTICAS COMPLETAS |
| Creado | 2026-04-11 |
| Última actualización | 2026-04-14 |
| Vistas totales | 270 |
| Total cards | 43 |
| Tabs | KPIs, Gráficas |

## 2. Parámetros del Dashboard

| Campo | Valor |
|-------|-------|
| ID | `param_periodo` |
| Nombre | Período |
| Slug (URL) | `?periodo=YYYY-MM-DD~YYYY-MM-DD` |
| Tipo | `date/range` |
| Default | `2025-01-01~2025-12-31` |

## 3. Cards por Tab

### Tab: KPIs

| Card ID | Nombre | Tipo | Mapping OK |
|---------|--------|------|-----------|
| 223 | Armas cortas aseguradas | `scalar` | ✅ |
| 224 | Armas largas aseguradas | `scalar` | ✅ |
| 225 | Cargadores asegurados | `scalar` | ✅ |
| 226 | Cartuchos de diferentes calibres | `scalar` | ✅ |
| 227 | Dosis de droga asegurada | `scalar` | ✅ |
| 231 | Dólares asegurados | `scalar` | ✅ |
| 213 | Emergencias Atendidas por CERI 9-1-1 | `scalar` | ✅ |
| 229 | Fentanilo (piezas) | `scalar` | ✅ |
| 230 | Kilogramos de droga asegurada (diversa) | `scalar` | ✅ |
| 215 | Nombres consultados Plataforma México | `scalar` | ✅ |
| 216 | Personas detenidas faltas administrativas | `scalar` | ✅ |
| 217 | Personas detenidas por delitos | `scalar` | ✅ |
| 232 | Pesos asegurados | `scalar` | ✅ |
| 228 | Piezas de psicotrópicos asegurados | `scalar` | ✅ |
| 220 | Vehículos asegurados por actos ilícitos | `scalar` | ✅ |
| 219 | Vehículos asegurados por placas SP | `scalar` | ✅ |
| 214 | Vehículos consultados Plataforma México | `scalar` | ✅ |
| 218 | Vehículos recuperados con reporte de robo | `scalar` | ✅ |
| 222 | Órdenes aprehensión detectadas OPERATIVOS | `scalar` | ✅ |
| 221 | Órdenes aprehensión detectadas S.S.P.M. | `scalar` | ✅ |

### Tab: Gráficas

| Card ID | Nombre | Tipo | Mapping OK |
|---------|--------|------|-----------|
| 236 | Armas aseguradas por día | `bar` | ✅ |
| 247 | Armas cortas aseguradas por día | `bar` | ✅ |
| 248 | Armas largas aseguradas por día | `bar` | ✅ |
| 249 | Cargadores asegurados por día | `bar` | ✅ |
| 250 | Cartuchos asegurados por día | `bar` | ✅ |
| 251 | Dosis droga asegurada por día | `bar` | ✅ |
| 254 | Dólares asegurados por día | `bar` | ✅ |
| 239 | Emergencias CERI 9-1-1 por día | `bar` | ✅ |
| 253 | Fentanilo (piezas) por día | `bar` | ✅ |
| 233 | Incidencia diaria de hechos | `bar` | ✅ |
| 238 | Kg droga asegurada por día | `bar` | ✅ |
| 241 | Nombres consultados Plataforma México por día | `bar` | ✅ |
| 234 | Personas detenidas por delito por día | `bar` | ✅ |
| 242 | Personas faltas administrativas por día | `bar` | ✅ |
| 255 | Pesos asegurados por día | `bar` | ✅ |
| 252 | Piezas psicotrópicos asegurados por día | `bar` | ✅ |
| 237 | Sustancias aseguradas por día | `bar` | ✅ |
| 244 | Vehículos asegurados placas SP por día | `bar` | ✅ |
| 235 | Vehículos asegurados por día | `bar` | ✅ |
| 240 | Vehículos consultados Plataforma México por día | `bar` | ✅ |
| 243 | Vehículos recuperados con reporte de robo por día | `bar` | ✅ |
| 246 | Órdenes aprehensión OPERATIVOS por día | `bar` | ✅ |
| 245 | Órdenes aprehensión S.S.P.M. por día | `bar` | ✅ |

## 4. Detalle de Queries por Card

### Tab: KPIs

#### Card 223 — Armas cortas aseguradas

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$ARMA_CORTA"
              }
          }
      }
  ]
  ```

#### Card 224 — Armas largas aseguradas

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$ARMA_LARGA"
              }
          }
      }
  ]
  ```

#### Card 225 — Cargadores asegurados

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$CARGADOR"
              }
          }
      }
  ]
  ```

#### Card 226 — Cartuchos de diferentes calibres

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$CARTUCHOS"
              }
          }
      }
  ]
  ```

#### Card 227 — Dosis de droga asegurada

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$DOSIS"
              }
          }
      }
  ]
  ```

#### Card 231 — Dólares asegurados

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$MONEDA_AMERICANA"
              }
          }
      }
  ]
  ```

#### Card 213 — Emergencias Atendidas por CERI 9-1-1

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`, `end`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [{"$limit": 1}, {"$project": {"_id": 0, "Total": {"$literal": 0}}}]
  ```

  > ⚠️ **PROBLEMA:** Query placeholder — siempre devuelve 0. No tiene lógica real de consulta.

  > ⚠️ **AVISO:** El tag `end` existe pero no tiene mapping al parámetro del dashboard.

#### Card 229 — Fentanilo (piezas)

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$FENTANILO"
              }
          }
      }
  ]
  ```

#### Card 230 — Kilogramos de droga asegurada (diversa)

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$PESO_ASEGURADO"
              }
          }
      }
  ]
  ```

#### Card 215 — Nombres consultados Plataforma México

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`, `end`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [{"$limit": 1}, {"$project": {"_id": 0, "Total": {"$literal": 0}}}]
  ```

  > ⚠️ **PROBLEMA:** Query placeholder — siempre devuelve 0. No tiene lógica real de consulta.

  > ⚠️ **AVISO:** El tag `end` existe pero no tiene mapping al parámetro del dashboard.

#### Card 216 — Personas detenidas faltas administrativas

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              },
              "motivo_intervencion": "Falta Administrativa"
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$_total_detenidos"
              }
          }
      }
  ]
  ```

#### Card 217 — Personas detenidas por delitos

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              },
              "motivo_intervencion": "Presunto delito"
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$_total_detenidos"
              }
          }
      }
  ]
  ```

#### Card 232 — Pesos asegurados

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$MONEDA_NACIONAL"
              }
          }
      }
  ]
  ```

#### Card 228 — Piezas de psicotrópicos asegurados

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$PSICOTROPICOS"
              }
          }
      }
  ]
  ```

#### Card 220 — Vehículos asegurados por actos ilícitos

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$_total_vehiculos"
              }
          }
      }
  ]
  ```

#### Card 219 — Vehículos asegurados por placas SP

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": null,
              "Total": {
                  "$sum": "$VEHICULO_INV_EN_DELITO"
              }
          }
      }
  ]
  ```

#### Card 214 — Vehículos consultados Plataforma México

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`, `end`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [{"$limit": 1}, {"$project": {"_id": 0, "Total": {"$literal": 0}}}]
  ```

  > ⚠️ **PROBLEMA:** Query placeholder — siempre devuelve 0. No tiene lógica real de consulta.

  > ⚠️ **AVISO:** El tag `end` existe pero no tiene mapping al parámetro del dashboard.

#### Card 218 — Vehículos recuperados con reporte de robo

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              },
              "DELITO_PRIMARIO": "POSESIÓN DE VEHICULO CON REPORTE DE ROBO"
          }
      },
      {
          "$count": "Total"
      }
  ]
  ```

#### Card 222 — Órdenes aprehensión detectadas OPERATIVOS

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              },
              "DELITO_PRIMARIO": "ORDEN DE APREHENSION VIGENTE"
          }
      },
      {
          "$count": "Total"
      }
  ]
  ```

#### Card 221 — Órdenes aprehensión detectadas S.S.P.M.

- **Tipo de visualización:** `scalar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      0,
                                      10
                                  ]
                              }
                          ]
                      },
                      {
                          "$lte": [
                              "$fecha_evento_iso",
                              {
                                  "$substrCP": [
                                      {{start}},
                                      11,
                                      10
                                  ]
                              }
                          ]
                      }
                  ]
              },
              "DELITO_PRIMARIO": "ORDEN DE APREHENSION VIGENTE"
          }
      },
      {
          "$count": "Total"
      }
  ]
  ```

### Tab: Gráficas

#### Card 236 — Armas aseguradas por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": {
                      "$add": [
                          {
                              "$ifNull": [
                                  "$ARMA_CORTA",
                                  0
                              ]
                          },
                          {
                              "$ifNull": [
                                  "$ARMA_LARGA",
                                  0
                              ]
                          }
                      ]
                  }
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 247 — Armas cortas aseguradas por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$ARMA_CORTA"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 248 — Armas largas aseguradas por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$ARMA_LARGA"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 249 — Cargadores asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$CARGADOR"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 250 — Cartuchos asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$CARTUCHOS"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 251 — Dosis droga asegurada por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$DOSIS"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 254 — Dólares asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$MONEDA_AMERICANA"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 239 — Emergencias CERI 9-1-1 por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": {
                      "$cond": [
                          {
                              "$and": [
                                  {
                                      "$ne": [
                                          "$POSITIVO_EN_CERI",
                                          null
                                      ]
                                  },
                                  {
                                      "$ne": [
                                          "$POSITIVO_EN_CERI",
                                          ""
                                      ]
                                  }
                              ]
                          },
                          1,
                          0
                      ]
                  }
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 253 — Fentanilo (piezas) por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$FENTANILO"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 233 — Incidencia diaria de hechos

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": 1
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 238 — Kg droga asegurada por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$PESO_ASEGURADO"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 241 — Nombres consultados Plataforma México por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$DETENIDO_1035_SP"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 234 — Personas detenidas por delito por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$_total_detenidos"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 242 — Personas faltas administrativas por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              },
              "motivo_intervencion": "Falta Administrativa"
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": 1
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 255 — Pesos asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$MONEDA_NACIONAL"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 252 — Piezas psicotrópicos asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$PSICOTROPICOS"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 237 — Sustancias aseguradas por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": {
                      "$add": [
                          {
                              "$ifNull": [
                                  "$DOSIS",
                                  0
                              ]
                          },
                          {
                              "$ifNull": [
                                  "$PSICOTROPICOS",
                                  0
                              ]
                          },
                          {
                              "$ifNull": [
                                  "$FENTANILO",
                                  0
                              ]
                          }
                      ]
                  }
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 244 — Vehículos asegurados placas SP por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$VEHICULO_INV_EN_DELITO"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 235 — Vehículos asegurados por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$_total_vehiculos"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 240 — Vehículos consultados Plataforma México por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": "$VEHICULO_1035_SP"
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 243 — Vehículos recuperados con reporte de robo por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": {
                      "$cond": [
                          {
                              "$eq": [
                                  "$DELITO_PRIMARIO",
                                  "POSESIÓN DE VEHICULO CON REPORTE DE ROBO"
                              ]
                          },
                          1,
                          0
                      ]
                  }
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 246 — Órdenes aprehensión OPERATIVOS por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              },
              "DELITO_PRIMARIO": "ORDEN DE APREHENSION VIGENTE"
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": 1
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

#### Card 245 — Órdenes aprehensión S.S.P.M. por día

- **Tipo de visualización:** `bar`
- **Template tags:** `start`
- **Parameter mappings:** 1
  - `param_periodo` → `['variable', ['template-tag', 'start']]`
- **Query MongoDB:**

  ```json
  [
      {
          "$addFields": {
              "_fc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              "$fecha_evento_iso",
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_sc": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              0,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              5,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              8,
                              2
                          ]
                      }
                  ]
              },
              "_ec": {
                  "$concat": [
                      {
                          "$substrCP": [
                              {{start}},
                              11,
                              4
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              16,
                              2
                          ]
                      },
                      {
                          "$substrCP": [
                              {{start}},
                              19,
                              2
                          ]
                      }
                  ]
              }
          }
      },
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$_fc",
                              "$_sc"
                          ]
                      },
                      {
                          "$lte": [
                              "$_fc",
                              "$_ec"
                          ]
                      }
                  ]
              },
              "DELITO_PRIMARIO": "ORDEN DE APREHENSION VIGENTE"
          }
      },
      {
          "$group": {
              "_id": {
                  "f": "$FECHA",
                  "s": "$_fc"
              },
              "Total": {
                  "$sum": 1
              }
          }
      },
      {
          "$sort": {
              "_id.s": 1
          }
      },
      {
          "$project": {
              "_id": "$_id.f",
              "Total": 1
          }
      }
  ]
  ```

## 5. Resumen de Problemas Detectados

| Card ID | Nombre | Tab | Problema |
|---------|--------|-----|---------|
| 213 | Emergencias Atendidas por CERI 9-1-1 | KPIs | Query placeholder (Total: 0 fijo) |
| 213 | Emergencias Atendidas por CERI 9-1-1 | KPIs | Tag 'end' sin mapping |
| 215 | Nombres consultados Plataforma México | KPIs | Query placeholder (Total: 0 fijo) |
| 215 | Nombres consultados Plataforma México | KPIs | Tag 'end' sin mapping |
| 214 | Vehículos consultados Plataforma México | KPIs | Query placeholder (Total: 0 fijo) |
| 214 | Vehículos consultados Plataforma México | KPIs | Tag 'end' sin mapping |

---
*Informe generado automáticamente desde la API de Metabase v0.59.4*