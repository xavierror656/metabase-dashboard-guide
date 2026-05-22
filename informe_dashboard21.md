# Informe: Dashboard 21 — DETENCIONES

## 1. Información General

| Campo | Valor |
|-------|-------|
| ID | 21 |
| Nombre | DETENCIONES |
| Creado | 2026-04-14 |
| Vistas totales | 56 |
| Total cards con query | 20 |
| Elementos de texto | 4 |
| Tabs | Sin tabs (vista única) |

## 2. Parámetro del Dashboard

| Campo | Valor |
|-------|-------|
| ID | `param_periodo` |
| Nombre | Período |
| Slug (URL) | `?periodo=YYYY-MM-DD~YYYY-MM-DD` |
| Tipo | `date/range` |
| Default | `2025-01-01~2025-12-31` |

## 3. Encabezados de Sección (Texto)

| Dashcard ID | Texto | Posición |
|-------------|-------|----------|
| 610 | FUERO COMÚN | fila 4, col 0 |
| 611 | FUERO FEDERAL | fila 18, col 0 |
| 612 | FALTAS ADMINISTRATIVAS | fila 26, col 0 |
| 614 | ÓRDENES DE APREHENSIÓN DETECTADAS SSPM_dashboard | fila 31, col 0 |

## 4. Cards — Resumen con Resultados (2026-01-01 ~ 2026-12-31)

### Colección: `mv_er_detenidos`

| Card ID | Nombre | Mapping | Resultado 2026 |
|---------|--------|---------|----------------|
| 339 | Total Detenciones | ✅ | **3,917** |
| 340 | Total Fuero Común | ✅ | **2,177** |
| 351 | Total Fuero Federal | ✅ | **88** |

### Colección: `mv_er_clasi_hechos`

| Card ID | Nombre | Mapping | Resultado 2026 |
|---------|--------|---------|----------------|
| 341 | FC - Delitos Contra la Salud | ✅ | **503** |
| 342 | FC - Homicidio | ✅ | **15** |
| 343 | FC - Homicidio en Grado de Tentativa | ✅ | **16** |
| 344 | FC - Lesiones | ✅ | **103** |
| 345 | FC - Posesión de Vehículo con Reporte de Robo | ✅ | **61** |
| 346 | FC - Privación Ilegal de la Libertad | ✅ | **13** |
| 347 | FC - Robo en sus Diversas Modalidades | ✅ | **274** |
| 348 | FC - Delitos Sexuales | ✅ | **20** |
| 349 | FC - Violencia Familiar | ✅ | **292** |
| 350 | FC - Otros Delitos | ✅ | **1,031** |
| 352 | FF - Delitos Contra la Salud | ✅ | **16** |
| 353 | FF - Contra la Ley Federal de Armas de Fuego y Explosivos | ✅ | **105** |
| 354 | FF - Otros Delitos | ✅ | **1,720** |
| 358 | Órdenes de Aprehensión Detectadas SSPM_dashboard | ✅ | **578** |

### Colección: `mv_er_faltas_admin`

| Card ID | Nombre | Mapping | Resultado 2026 |
|---------|--------|---------|----------------|
| 355 | Total Faltas Administrativas | ✅ | **1,226** |
| 356 | FA - Falta de Coordinación General de Policía | ✅ | **1,226** |
| 357 | FA - Faltas de Coordinación General de Seguridad Vial (CERECITO) | ✅ | **1,226** |

## 5. Detalle de Queries por Card

#### Card 339 — Total Detenciones

- **Colección MongoDB:** `mv_er_detenidos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** Sin filtro adicional (total general)
- **Resultado (2026-01-01 ~ 2026-12-31):** **3,917**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 340 — Total Fuero Común

- **Colección MongoDB:** `mv_er_detenidos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `fuero: "Estatal"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **2,177**

  ```json
  [
      {
          "$match": {
              "fuero": "Estatal",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 341 — FC - Delitos Contra la Salud

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "NARCOMENUDEO"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **503**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "NARCOMENUDEO",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 342 — FC - Homicidio

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "HOMICIDIO"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **15**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "HOMICIDIO",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 343 — FC - Homicidio en Grado de Tentativa

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: {$in: ["TENTATIVA DE HOMICIDIO", "TENTATIVA DE FEMINICIDIO"]}`
- **Resultado (2026-01-01 ~ 2026-12-31):** **16**

  ```json
  [
      {
          "$match": {
              "nombre_delito": {
                  "$in": [
                      "TENTATIVA DE HOMICIDIO",
                      "TENTATIVA DE FEMINICIDIO"
                  ]
              },
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 344 — FC - Lesiones

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "LESIONES"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **103**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "LESIONES",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 345 — FC - Posesión de Vehículo con Reporte de Robo

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "POSESIÓN DE VEHICULO CON REPORTE DE ROBO"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **61**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "POSESIÓN DE VEHICULO CON REPORTE DE ROBO",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 346 — FC - Privación Ilegal de la Libertad

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "PRIVACIÓN DE LA LIBERTAD"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **13**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "PRIVACIÓN DE LA LIBERTAD",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 347 — FC - Robo en sus Diversas Modalidades

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "ROBO"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **274**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "ROBO",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 348 — FC - Delitos Sexuales

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: {$in: ["ABUSO SEXUAL", "ACOSO SEXUAL", ...]}`
- **Resultado (2026-01-01 ~ 2026-12-31):** **20**

  ```json
  [
      {
          "$match": {
              "nombre_delito": {
                  "$in": [
                      "ABUSO SEXUAL",
                      "ACOSO SEXUAL",
                      "HOSTIGAMIENTO SEXUAL",
                      "VIOLACIÓN EQUIPARADA",
                      "VIOLACIÓN SIMPLE",
                      "OTROS DELITOS QUE ATENTAN CONTRA LA LIBERTAD Y LA SEGURIDAD SEXUAL"
                  ]
              },
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 349 — FC - Violencia Familiar

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "VIOLENCIA FAMILIAR"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **292**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "VIOLENCIA FAMILIAR",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 350 — FC - Otros Delitos

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: {$nin: [...todos los FC listados...]}`
- **Resultado (2026-01-01 ~ 2026-12-31):** **1,031**

  ```json
  [
      {
          "$match": {
              "nombre_delito": {
                  "$nin": [
                      "NARCOMENUDEO",
                      "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS",
                      "HOMICIDIO",
                      "TENTATIVA DE HOMICIDIO",
                      "TENTATIVA DE FEMINICIDIO",
                      "LESIONES",
                      "POSESIÓN DE VEHICULO CON REPORTE DE ROBO",
                      "PRIVACIÓN DE LA LIBERTAD",
                      "ROBO",
                      "ABUSO SEXUAL",
                      "ACOSO SEXUAL",
                      "HOSTIGAMIENTO SEXUAL",
                      "VIOLACIÓN EQUIPARADA",
                      "VIOLACIÓN SIMPLE",
                      "OTROS DELITOS QUE ATENTAN CONTRA LA LIBERTAD Y LA SEGURIDAD SEXUAL",
                      "VIOLENCIA FAMILIAR"
                  ]
              },
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 351 — Total Fuero Federal

- **Colección MongoDB:** `mv_er_detenidos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `fuero: "Federal"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **88**

  ```json
  [
      {
          "$match": {
              "fuero": "Federal",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 352 — FF - Delitos Contra la Salud

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **16**

  ```json
  [
      {
          "$match": {
              "nombre_delito": "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 353 — FF - Contra la Ley Federal de Armas de Fuego y Explosivos

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: {$in: ["DELITOS EN MATERIA DE ARMAS..."]}`
- **Resultado (2026-01-01 ~ 2026-12-31):** **105**

  ```json
  [
      {
          "$match": {
              "nombre_delito": {
                  "$in": [
                      "DELITOS EN MATERIA DE ARMAS, EXPLOSIVOS Y OTROS MATERIALES DESTRUCTIVOS",
                      "DELITOS EN MATERIA DE ARMAS Y OBJETOS PROHIBIDOS"
                  ]
              },
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 354 — FF - Otros Delitos

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `nombre_delito: {$nin: [...todos los FF listados...]}`
- **Resultado (2026-01-01 ~ 2026-12-31):** **1,720**

  ```json
  [
      {
          "$match": {
              "nombre_delito": {
                  "$nin": [
                      "DELITOS CONTRA LA SALUD",
                      "DELITOS CONTRA LA SALUD FEDERAL",
                      "DELITO CONTRA LA SALUD",
                      "DELITO CONTRA SALUD",
                      "CONTRA LA SALUD",
                      "DELITOS EN MATERIA DE ARMAS, EXPLOSIVOS Y OTROS MATERIALES DESTRUCTIVOS",
                      "DELITOS EN MATERIA DE ARMAS Y OBJETOS PROHIBIDOS",
                      "NARCOMENUDEO",
                      "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS"
                  ]
              },
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 355 — Total Faltas Administrativas

- **Colección MongoDB:** `mv_er_faltas_admin`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** Sin filtro adicional (total general)
- **Resultado (2026-01-01 ~ 2026-12-31):** **1,226**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 356 — FA - Falta de Coordinación General de Policía

- **Colección MongoDB:** `mv_er_faltas_admin`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** Sin filtro adicional — misma colección que 355
- **Resultado (2026-01-01 ~ 2026-12-31):** **1,226**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 357 — FA - Faltas de Coordinación General de Seguridad Vial (CERECITO)

- **Colección MongoDB:** `mv_er_faltas_admin`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** Sin filtro adicional — misma colección que 355
- **Resultado (2026-01-01 ~ 2026-12-31):** **1,226**

  ```json
  [
      {
          "$match": {
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

#### Card 358 — Órdenes de Aprehensión Detectadas SSPM_dashboard

- **Colección MongoDB:** `mv_er_clasi_hechos`
- **Visualización:** `scalar`
- **Template tag:** `{{start}}` (rango completo `YYYY-MM-DD~YYYY-MM-DD`)
- **Filtro de negocio:** `orden_aprehension: "SI"`
- **Resultado (2026-01-01 ~ 2026-12-31):** **578**

  ```json
  [
      {
          "$match": {
              "orden_aprehension": "SI",
              "$expr": {
                  "$and": [
                      {
                          "$gte": [
                              "$fecha_evento",
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
                              "$fecha_evento",
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
          "$count": "total"
      }
  ]
  ```

## 6. Correcciones Aplicadas en Esta Sesión

| # | Descripción |
|---|-------------|
| 1 | **20 cards reescritas**: eliminada lógica `$switch`/`$regexMatch` de ~200 líneas por card |
| 2 | **Tag `{{end}}` eliminado**: causa raíz del bug (siempre usaba valor default) |
| 3 | **Tag único `{{start}}`**: recibe rango `YYYY-MM-DD~YYYY-MM-DD` y extrae ambas fechas con `$substrCP` |
| 4 | **Mappings del dashboard actualizados**: 40 mappings → 20 mappings (1 por card) |
| 5 | **Nombre card 339 restaurado**: de "test" → "Total Detenciones" |

### Patrón de query aplicado (basado en dashboard 17)

```json
[
  {
    "$match": {
      "<filtro_negocio>": "<valor>",
      "$expr": {
        "$and": [
          { "$gte": ["$fecha_evento", { "$substrCP": [{{start}}, 0, 10] }] },
          { "$lte": ["$fecha_evento", { "$substrCP": [{{start}}, 11, 10] }] }
        ]
      }
    }
  },
  { "$count": "total" }
]
```

## 7. Notas sobre Cards 355, 356, 357 (Faltas Administrativas)

Las tres cards consultan la misma colección `mv_er_faltas_admin` sin filtro de negocio diferenciador,
lo que resulta en el mismo conteo (**1,226**) para las tres.
Es posible que la colección ya esté pre-filtrada por unidad, o que falten filtros adicionales.
Se recomienda revisar los campos disponibles en `mv_er_faltas_admin` para diferenciarlas correctamente.

---
*Informe generado automáticamente desde la API de Metabase v0.59.4 — 2026-04-24*