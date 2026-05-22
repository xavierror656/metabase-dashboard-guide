# Guía: Crear y mantener dashboards en Metabase (MongoDB) vía API

## Requisitos

- Metabase v0.59+ con base de datos MongoDB
- API key con permisos de escritura
- Python 3 (usar `http.client` directamente — `urllib` da HTTP 403 en este servidor)

```python
import http.client, ssl, json
from urllib.parse import urlparse

API_BASE = "https://tu-metabase.ejemplo.com"
API_KEY  = "mb_TU_API_KEY"
HEADERS  = {"Content-Type": "application/json", "x-api-key": API_KEY}
_SSL_CTX = ssl.create_default_context()

def req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    hdrs = dict(HEADERS)
    if data:
        hdrs["Content-Length"] = str(len(data))
    c = http.client.HTTPSConnection(urlparse(API_BASE).hostname, context=_SSL_CTX)
    c.request(method, f"/api{path}", body=data, headers=hdrs)
    r = c.getresponse(); raw = r.read(); c.close()
    if r.status >= 400:
        raise RuntimeError(f"HTTP {r.status} {method} {path}: {raw.decode()[:300]}")
    return json.loads(raw) if raw.strip() else {}
```

> **Por qué `http.client` y no `requests`/`urllib`:** este servidor devuelve HTTP 403 con `urllib`. Usar `http.client.HTTPSConnection` directamente funciona correctamente.

---

## 1. Regla crítica: comillas en template tags (MongoDB)

| Sintaxis en la query | Lo que Metabase envía a Mongo | Resultado |
|---|---|---|
| `"{{tag}}"` (con comillas) | valor crudo sin comillas → `2026-03-07` | ❌ JSON inválido |
| `{{tag}}` (sin comillas) | valor con comillas → `"2026-03-07"` | ✅ válido |

**Regla:** Nunca pongas comillas alrededor de `{{tag}}` en la query JSON de MongoDB.

**Truco para construir queries con tags en Python:**

```python
PH = "__PH_START__"  # placeholder sin comillas especiales

pipeline = [{"$match": {"$expr": {"$gte": [f"$fecha", {"$substrCP": [PH, 0, 10]}]}}}]
q = json.dumps(pipeline, ensure_ascii=False)
q = q.replace(f'"{PH}"', "{{start}}")  # quita las comillas del placeholder
```

---

## 2. Problema con parámetro `date/range` y dos tags

Cuando el dashboard tiene un parámetro tipo `date/range` mapeado a dos tags (`start` y `end`), Metabase **solo envía el valor al tag `start`**; el tag `end` siempre usa su valor por defecto.

**Solución:** Usar un solo tag `{{start}}` que recibe el rango completo (`"YYYY-MM-DD~YYYY-MM-DD"`) y extraer ambas fechas con `$substrCP`.

---

## 3. Estructura de query para filtrar por rango de fechas

### 3a. Card de número/KPI

```json
[
  {
    "$match": {
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

> `$substrCP [{{start}}, 0, 10]` extrae la fecha de inicio (chars 0–9).  
> `$substrCP [{{start}}, 11, 10]` extrae la fecha de fin (chars 11–20).

### 3b. Card con suma agregada (`$group + $sum`)

Si usas `$group + $sum` en lugar de `$count`, el resultado tiene dos columnas `[null, valor]` y el display "scalar" muestra el primero (null). Solución: agregar `$project` para eliminar el `_id`:

```json
[
  { "$match": { ... } },
  { "$group": { "_id": null, "total": { "$sum": "$campo" } } },
  { "$project": { "_id": 0, "total": 1 } }
]
```

### 3c. Card de gráfica por día

```json
[
  {
    "$addFields": {
      "_fc": { "$concat": [
        { "$substrCP": ["$fecha_evento", 0, 4] },
        { "$substrCP": ["$fecha_evento", 5, 2] },
        { "$substrCP": ["$fecha_evento", 8, 2] }
      ]},
      "_sc": { "$concat": [
        { "$substrCP": [{{start}}, 0, 4] },
        { "$substrCP": [{{start}}, 5, 2] },
        { "$substrCP": [{{start}}, 8, 2] }
      ]},
      "_ec": { "$concat": [
        { "$substrCP": [{{start}}, 11, 4] },
        { "$substrCP": [{{start}}, 16, 2] },
        { "$substrCP": [{{start}}, 19, 2] }
      ]}
    }
  },
  {
    "$match": {
      "$expr": {
        "$and": [
          { "$gte": ["$_fc", "$_sc"] },
          { "$lte": ["$_fc", "$_ec"] }
        ]
      }
    }
  },
  {
    "$group": {
      "_id": { "f": "$fecha_evento", "s": "$_fc" },
      "Total": { "$sum": 1 }
    }
  },
  { "$sort": { "_id.s": 1 } },
  { "$project": { "_id": "$_id.f", "Total": 1 } }
]
```

> `_fc`, `_sc`, `_ec` son strings `YYYYMMDD` comparables lexicográficamente. Esta técnica evita `$dateFromString` que no funciona bien con fechas en formato string sin timezone.

---

## 4. Template tag (solo uno por card)

```json
{
  "start": {
    "id": "uuid-aqui",
    "name": "start",
    "display-name": "Período",
    "type": "text",
    "required": false,
    "default": "2025-01-01~2025-12-31"
  }
}
```

---

## 5. Filtros opcionales con `[[ ... ]]`

Metabase soporta bloques opcionales: si el tag no tiene valor, el bloque entero se elimina de la query enviada a MongoDB.

### Patrón para agregar filtros opcionales a un `$match` existente

Envuelve el cuerpo del `$match` en `$and` y agrega los filtros opcionales:

```json
[
  {
    "$match": {
      "$and": [
        { "$expr": { ... } }
        [[ ,{"distrito": {{distrito}}} ]]
        [[ ,{"sector": {{sector}}} ]]
      ]
    }
  },
  { "$count": "total" }
]
```

- Cuando `distrito` tiene valor → se agrega `{"distrito": "ORIENTE"}` al `$and`
- Cuando `distrito` está vacío → el bloque `[[ ... ]]` desaparece completamente

### Algoritmo para inyectar filtros en queries existentes (Python)

```python
def find_match_body_bounds(query_str):
    """Encuentra el inicio y fin del cuerpo del primer $match usando conteo de llaves."""
    idx = query_str.find('"$match"')
    if idx == -1:
        return None, None
    brace_start = query_str.index('{', idx + len('"$match"'))
    depth = 0
    for i in range(brace_start, len(query_str)):
        if query_str[i] == '{':
            depth += 1
        elif query_str[i] == '}':
            depth -= 1
            if depth == 0:
                return brace_start, i
    return None, None

def inject_optional_filters(query_str):
    """Envuelve el $match en $and con filtros opcionales de distrito y sector."""
    start, end = find_match_body_bounds(query_str)
    if start is None:
        return query_str

    original_body = query_str[start:end + 1]
    optional = (
        ' [[ ,{"distrito": {{distrito}}} ]]'
        ' [[ ,{"sector": {{sector}}} ]]'
    )
    new_body = f'{{"$and": [{original_body}{optional}]}}'
    return query_str[:start] + new_body + query_str[end + 1:]
```

> **Nota sobre el conteo de llaves:** `{{start}}` contribuye +2 y -2 de profundidad (neto cero), por lo que el algoritmo identifica correctamente el cierre del `$match` incluso cuando la query contiene template tags.

### Template tags para los filtros opcionales

```python
for field in ("distrito", "sector"):
    ttags[field] = {
        "id":           str(uuid.uuid4()),
        "name":         field,
        "display-name": field.capitalize(),
        "type":         "text",
        "required":     False,
        # Sin "default" — cuando está vacío el filtro no aplica
    }
```

### Nombres de campo por colección

El nombre del campo en el filtro depende de la colección MongoDB:

| Colección | Campo distrito | Campo sector |
|---|---|---|
| `mv_er_detenidos`, `mv_er_armas`, `mv_er_sustancias`, `mv_er_clasi_hechos`, `mv_er_faltas_admin`, `mv_reporte_vehiculos_general` | `distrito` (minúsculas) | `sector` (minúsculas) |
| `vista_departamento_estadisticas` | `DISTRITO_DE_EVENTO` (mayúsculas) | `CUADRANTE` (mayúsculas) |

---

## 6. Crear o actualizar una card

```python
card = req("GET", f"/card/{card_id}")
dq = card["dataset_query"]
dq["stages"][0]["native"] = query_str
dq["stages"][0]["template-tags"] = template_tags
dq["stages"][0]["collection"] = "nombre_coleccion_mongo"

req("PUT", f"/card/{card_id}", {
    "dataset_query":          dq,
    "name":                   card["name"],
    "display":                card.get("display", "scalar"),
    "visualization_settings": card.get("visualization_settings", {}),
    "collection_id":          card.get("collection_id"),
})
```

Para crear una card nueva usa `POST /api/card` con la misma estructura de `dataset_query`:

```python
req("POST", "/card", {
    "name": "Nombre de la card",
    "display": "bar",
    "dataset_query": {
        "lib/type": "mbql/query",
        "database": DB_ID,
        "stages": [{
            "lib/type":      "mbql.stage/native",
            "collection":    "nombre_coleccion",
            "template-tags": ttags,
            "native":        query_str,
        }],
    },
    "visualization_settings": {},
    "collection_id": COL_ID,
})
```

---

## 7. Parámetros del dashboard

### Parámetro de rango de fechas

```python
req("PUT", f"/dashboard/{DASH_ID}", {
    "parameters": [
        {
            "id":      "param_periodo",
            "name":    "Período",
            "slug":    "periodo",
            "type":    "date/range",
            "default": "2025-01-01~2025-12-31",
        }
    ]
})
```

### Parámetro de texto con dropdown (lista de selección)

Para que aparezca como dropdown en lugar de campo de texto libre, se necesitan **tres campos**:

```python
{
    "id":                  "param_distrito",
    "name":                "Distrito",
    "slug":                "distrito",
    "type":                "string/=",
    "values_query_type":   "list",           # ← OBLIGATORIO para dropdown
    "values_source_type":  "static-list",    # ← tipo de fuente
    "values_source_config": {
        "values": ["CENTRO", "ORIENTE", "PONIENTE", "RIVERAS", "SUR", "UNIVERSIDAD", "VALLE"]
    }
}
```

> Si falta `values_query_type: "list"` el widget se muestra como campo de texto aunque `values_source_type` sea `"static-list"`.

---

## 8. Crear tabs y agregar cards al dashboard

La API `PUT /api/dashboard/:id/cards` crea tabs y dashcards en una sola llamada.  
Usa IDs negativos para tabs y dashcards nuevos; Metabase asigna los IDs reales.

```python
tabs = [
    {"id": -1, "name": "KPIs",     "position": 0},
    {"id": -2, "name": "Gráficas", "position": 1},
]

cards = [
    {
        "id":                  -1,       # nuevo dashcard
        "card_id":             233,
        "row": 0, "col": 0,
        "size_x": 12, "size_y": 6,
        "dashboard_tab_id":    -2,       # tab "Gráficas"
        "visualization_settings": {},
        "parameter_mappings": [
            {
                "parameter_id": "param_periodo",
                "card_id":      233,
                "target":       ["variable", ["template-tag", "start"]],
            },
            {
                "parameter_id": "param_distrito",
                "card_id":      233,
                "target":       ["variable", ["template-tag", "distrito"]],
            },
            {
                "parameter_id": "param_sector",
                "card_id":      233,
                "target":       ["variable", ["template-tag", "sector"]],
            },
        ],
    },
]

req("PUT", f"/dashboard/{DASH_ID}/cards", {"cards": cards, "tabs": tabs})
```

> **Importante:** Siempre incluye `"tabs"` en el body. Si se omite, la FK de `dashboard_tab_id` falla con error 500.

---

## 9. Actualizar mappings de cards existentes

Si el dashboard ya tiene tabs y dashcards pero los mappings son incorrectos:

```python
dash = req("GET", f"/dashboard/{DASH_ID}")
tabs = dash.get("tabs", [])

updated_cards = []
for dc in dash["dashcards"]:
    cid = dc["card_id"]
    entry = {
        "id":                     dc["id"],
        "card_id":                cid,
        "row":                    dc["row"],
        "col":                    dc["col"],
        "size_x":                 dc["size_x"],
        "size_y":                 dc["size_y"],
        "dashboard_tab_id":       dc.get("dashboard_tab_id"),
        "visualization_settings": dc.get("visualization_settings", {}),
        "parameter_mappings": [
            {"parameter_id": "param_periodo",  "card_id": cid, "target": ["variable", ["template-tag", "start"]]},
            {"parameter_id": "param_distrito", "card_id": cid, "target": ["variable", ["template-tag", "distrito"]]},
            {"parameter_id": "param_sector",   "card_id": cid, "target": ["variable", ["template-tag", "sector"]]},
        ] if cid else [],
    }
    updated_cards.append(entry)

req("PUT", f"/dashboard/{DASH_ID}/cards", {"cards": updated_cards, "tabs": tabs})
```

---

## 10. Probar una card directamente

```bash
curl -s -X POST \
  "https://tu-metabase.ejemplo.com/api/card/233/query" \
  -H "x-api-key: mb_TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": [
      {"type": "text", "target": ["variable", ["template-tag", "start"]],    "value": "2026-03-07~2026-03-14"},
      {"type": "text", "target": ["variable", ["template-tag", "distrito"]], "value": "ORIENTE"},
      {"type": "text", "target": ["variable", ["template-tag", "sector"]],   "value": "521"}
    ]
  }'
```

O en Python:

```python
r = req("POST", f"/card/{card_id}/query", {"parameters": [
    {"type": "text", "target": ["variable", ["template-tag", "start"]],    "value": "2026-01-01~2026-12-31"},
    {"type": "text", "target": ["variable", ["template-tag", "distrito"]], "value": "ORIENTE"},
]})
print(r["data"]["rows"])
```

---

## 11. URL del dashboard con filtros

```
https://tu-metabase.ejemplo.com/dashboard/17?periodo=2026-03-07~2026-03-14&distrito=ORIENTE&sector=521
```

Los slugs de los parámetros se usan como query params en la URL.

---

## Resumen del flujo completo

```
1. Crear cards con query MongoDB + template tag {{start}} (sin comillas)
   - KPI: $match + $count (o $group + $sum + $project para evitar null)
   - Gráfica: $addFields (_fc/_sc/_ec) + $match + $group + $sort + $project

2. Agregar filtros opcionales de distrito/sector
   - Envolver $match en $and con bloques [[ ,{"campo": {{tag}}} ]]
   - Atención: vista_departamento_estadisticas usa DISTRITO_DE_EVENTO y CUADRANTE

3. Configurar parámetros del dashboard
   - date/range para período
   - string/= con values_query_type:"list" + values_source_type:"static-list" para dropdowns

4. PUT /api/dashboard/:id/cards con tabs (ids negativos) + cards + mappings
   - Siempre incluir "tabs" en el body

5. Verificar con URL ?slug=YYYY-MM-DD~YYYY-MM-DD&distrito=ORIENTE
```
