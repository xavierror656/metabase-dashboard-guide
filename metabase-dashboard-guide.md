# Guía: Crear y mantener dashboards en Metabase (MongoDB) vía API

## Requisitos

- Metabase v0.59+ con base de datos MongoDB
- API key con permisos de escritura
- `curl` o Python `requests`

```
API_BASE = "https://tu-metabase.ejemplo.com/api"
HEADERS  = {
  "Content-Type": "application/json",
  "x-api-key": "mb_TU_API_KEY"
}
```

---

## 1. Regla crítica: comillas en template tags (MongoDB)

Esta es la diferencia entre una consulta que funciona y una que rompe todo.

| Sintaxis en la query | Lo que Metabase envía a Mongo | Resultado |
|---|---|---|
| `"{{tag}}"` (con comillas) | valor crudo sin comillas → `2026-03-07` | ❌ JSON inválido |
| `{{tag}}` (sin comillas) | valor con comillas → `"2026-03-07"` | ✅ válido |

**Regla:** Nunca pongas comillas alrededor de `{{tag}}` en la query JSON de MongoDB.

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
          { "$gte": ["$fecha_evento_iso", { "$substrCP": [{{start}}, 0, 10] }] },
          { "$lte": ["$fecha_evento_iso", { "$substrCP": [{{start}}, 11, 10] }] }
        ]
      }
    }
  },
  { "$group": { "_id": null, "Total": { "$sum": 1 } } }
]
```

> `$substrCP [{{start}}, 0, 10]` extrae la fecha de inicio (chars 0–9).  
> `$substrCP [{{start}}, 11, 10]` extrae la fecha de fin (chars 11–20).

### 3b. Card de gráfica por día

```json
[
  {
    "$addFields": {
      "_fc": { "$concat": [
        { "$substrCP": ["$fecha_evento_iso", 0, 4] },
        { "$substrCP": ["$fecha_evento_iso", 5, 2] },
        { "$substrCP": ["$fecha_evento_iso", 8, 2] }
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
      "_id": { "f": "$FECHA", "s": "$_fc" },
      "Total": { "$sum": 1 }
    }
  },
  { "$sort": { "_id.s": 1 } },
  { "$project": { "_id": "$_id.f", "Total": 1 } }
]
```

> `_fc`, `_sc`, `_ec` son strings `YYYYMMDD` comparables lexicográficamente.

---

## 4. Template tag (solo uno por card)

```json
{
  "start": {
    "id": "tag-start",
    "name": "start",
    "display-name": "Período",
    "type": "text",
    "required": false,
    "default": "2025-01-01~2025-12-31"
  }
}
```

---

## 5. Crear o actualizar una card

```python
def update_card(card_id, query_str, template_tags, name, display="scalar"):
    card = requests.get(f"{API}/card/{card_id}", headers=HEADERS).json()
    dq = card["dataset_query"]
    dq["stages"][0]["native"] = query_str
    dq["stages"][0]["template-tags"] = template_tags
    payload = {
        "dataset_query": dq,
        "name": name,
        "display": display,
        "visualization_settings": card.get("visualization_settings", {}),
        "collection_id": card.get("collection_id"),
    }
    return requests.put(f"{API}/card/{card_id}", headers=HEADERS, json=payload)
```

Para crear una card nueva usa `POST /api/card` con la misma estructura de `dataset_query`.

---

## 6. Parámetro del dashboard

El dashboard necesita un parámetro `date/range` con `id` único (se usa en los mappings):

```python
requests.put(f"{API}/dashboard/{DASH_ID}", headers=HEADERS, json={
    "parameters": [
        {
            "id": "param_periodo",
            "name": "Período",
            "slug": "periodo",
            "type": "date/range",
            "default": "2025-01-01~2025-12-31"
        }
    ]
})
```

---

## 7. Crear tabs y agregar cards al dashboard

La API `PUT /api/dashboard/:id/cards` crea tabs y dashcards en una sola llamada.  
Usa IDs negativos para tabs y dashcards nuevos; Metabase asigna los IDs reales.

```python
tabs = [
    {"id": -1, "name": "KPIs",     "position": 0},
    {"id": -2, "name": "Gráficas", "position": 1},
]

cards = [
    {
        "id": -1,                    # nuevo dashcard
        "card_id": 233,              # ID de la card
        "row": 0, "col": 0,
        "size_x": 12, "size_y": 6,
        "dashboard_tab_id": -2,      # tab "Gráficas"
        "visualization_settings": {},
        "parameter_mappings": [
            {
                "parameter_id": "param_periodo",
                "card_id": 233,
                "target": ["variable", ["template-tag", "start"]]
            }
        ],
    },
    # ... más cards
]

requests.put(
    f"{API}/dashboard/{DASH_ID}/cards",
    headers=HEADERS,
    json={"cards": cards, "tabs": tabs}
)
```

> **Importante:** Siempre incluye `"tabs"` en el body. Si se omite, la FK de `dashboard_tab_id` falla con error 500.

---

## 8. Actualizar mappings de cards existentes

Si el dashboard ya tiene tabs y dashcards pero los mappings son incorrectos:

```python
r = requests.get(f"{API}/dashboard/{DASH_ID}", headers=HEADERS).json()

updated_cards = []
for dc in r["dashcards"]:
    cid = dc["card_id"]
    updated_cards.append({
        "id": dc["id"],
        "card_id": cid,
        "row": dc["row"], "col": dc["col"],
        "size_x": dc["size_x"], "size_y": dc["size_y"],
        "dashboard_tab_id": dc.get("dashboard_tab_id"),
        "visualization_settings": dc.get("visualization_settings", {}),
        "parameter_mappings": [
            {
                "parameter_id": "param_periodo",
                "card_id": cid,
                "target": ["variable", ["template-tag", "start"]]
            }
        ],
    })

requests.put(
    f"{API}/dashboard/{DASH_ID}/cards",
    headers=HEADERS,
    json={"cards": updated_cards, "tabs": r["tabs"]}  # tabs obligatorio
)
```

---

## 9. Probar una card directamente

```bash
curl -s -X POST \
  "https://tu-metabase.ejemplo.com/api/card/233/query" \
  -H "x-api-key: mb_TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": [
      {
        "type": "text",
        "target": ["variable", ["template-tag", "start"]],
        "value": "2026-03-07~2026-03-14"
      }
    ]
  }'
```

---

## 10. URL del dashboard con filtro de fechas

```
https://tu-metabase.ejemplo.com/dashboard/17?periodo=2026-03-07~2026-03-14
```

El slug del parámetro (`periodo`) se usa como query param en la URL.

---

## Resumen del flujo completo

```
1. Crear cards con query MongoDB + template tag {{start}} (sin comillas)
2. Configurar el parámetro date/range en el dashboard
3. PUT /api/dashboard/:id/cards con tabs (ids negativos) + cards + mappings
4. Verificar con URL ?slug=YYYY-MM-DD~YYYY-MM-DD
```
