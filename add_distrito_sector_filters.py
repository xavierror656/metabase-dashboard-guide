#!/usr/bin/env python3
"""
Agrega filtros opcionales de Distrito y Sector a los dashboards 17, 21 y 23.

Para cada card:
  - Envuelve el $match en {"$and": [<match_original> [[ ,{"distrito": {{distrito}}} ]] [[ ,{"sector": {{sector}}} ]] ]}
  - Agrega los template tags "distrito" y "sector" (required=false, sin default)

Para cada dashboard:
  - Agrega parámetros param_distrito y param_sector (string/=)
  - Mapea los parámetros a todos los dashcards
"""

import json
import os
import uuid
import http.client
import ssl

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    for _line in open(_env_path):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

API_BASE = os.environ["METABASE_API_BASE"]
API_KEY  = os.environ["METABASE_API_KEY"]
HEADERS  = {"Content-Type": "application/json", "x-api-key": API_KEY}

DASHBOARD_IDS = [17, 21, 23]

# ── HTTP ──────────────────────────────────────────────────────────────────────
_SSL_CTX = ssl.create_default_context()

def _conn():
    from urllib.parse import urlparse
    return http.client.HTTPSConnection(urlparse(API_BASE).hostname, context=_SSL_CTX)

def _req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    hdrs = dict(HEADERS)
    if data:
        hdrs["Content-Length"] = str(len(data))
    c = _conn()
    c.request(method, f"/api{path}", body=data, headers=hdrs)
    r = c.getresponse(); raw = r.read(); c.close()
    if r.status >= 400:
        raise RuntimeError(f"HTTP {r.status} {method} {path}: {raw.decode()[:300]}")
    return json.loads(raw) if raw.strip() else {}

# ── QUERY TRANSFORMER ─────────────────────────────────────────────────────────

def find_match_body_bounds(query_str):
    """
    Finds the start and end positions of the {body} of the first $match stage.
    Returns (start, end) where query_str[start:end+1] is the match body including braces.
    Uses bracket counting — works correctly even when {{start}} template tags are present
    because {{ and }} contribute +2 and -2 depth (net zero).
    """
    idx = query_str.find('"$match"')
    if idx == -1:
        return None, None
    # Find the opening { after "$match":
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
    """
    Wraps the $match body in {"$and": [<original_body> [[...distrito...]] [[...sector...]]]}
    so that distrito/sector are optional filters using Metabase's [[...]] syntax.
    """
    start, end = find_match_body_bounds(query_str)
    if start is None:
        return query_str  # no $match found, return as-is

    original_body = query_str[start:end + 1]

    optional = (
        ' [[ ,{"distrito": {{distrito}}} ]]'
        ' [[ ,{"sector": {{sector}}} ]]'
    )
    new_body = f'{{"$and": [{original_body}{optional}]}}'

    return query_str[:start] + new_body + query_str[end + 1:]


def new_ttags_for_card(existing_ttags):
    """Returns the existing template tags + distrito + sector (both optional, no default)."""
    ttags = dict(existing_ttags)
    for field in ("distrito", "sector"):
        if field not in ttags:
            ttags[field] = {
                "id":           str(uuid.uuid4()),
                "name":         field,
                "display-name": field.capitalize(),
                "type":         "text",
                "required":     False,
            }
    return ttags


# ── DASHBOARD PARAMETER HELPERS ───────────────────────────────────────────────

NEW_PARAMS = [
    {
        "id":      "param_distrito",
        "name":    "Distrito",
        "slug":    "distrito",
        "type":    "string/=",
    },
    {
        "id":      "param_sector",
        "name":    "Sector",
        "slug":    "sector",
        "type":    "string/=",
    },
]

def build_parameter_mappings(card_id, existing_mappings):
    """
    Keeps the existing param_periodo mapping and adds distrito + sector.
    Avoids duplicates.
    """
    mappings = list(existing_mappings)
    existing_param_ids = {m["parameter_id"] for m in mappings}
    for p in NEW_PARAMS:
        if p["id"] not in existing_param_ids:
            mappings.append({
                "parameter_id": p["id"],
                "card_id":      card_id,
                "target":       ["variable", ["template-tag", p["slug"]]],
            })
    return mappings


# ── MAIN ──────────────────────────────────────────────────────────────────────

def process_dashboard(dash_id):
    print(f"\n{'='*60}")
    print(f"Dashboard {dash_id}")
    print(f"{'='*60}")

    dash = _req("GET", f"/dashboard/{dash_id}")

    # 1. Collect unique card IDs (skip text dashcards)
    card_ids = list({
        dc["card_id"]
        for dc in dash.get("dashcards", [])
        if dc.get("card_id") is not None
    })
    print(f"  Cards a actualizar: {len(card_ids)}")

    # 2. Update each card
    updated_ok   = []
    updated_fail = []

    for card_id in sorted(card_ids):
        try:
            card = _req("GET", f"/card/{card_id}")
            s0   = card["dataset_query"]["stages"][0]

            original_query = s0.get("native", "")
            new_query      = inject_optional_filters(original_query)
            new_ttags      = new_ttags_for_card(s0.get("template-tags", {}))

            s0["native"]        = new_query
            s0["template-tags"] = new_ttags

            _req("PUT", f"/card/{card_id}", {
                "dataset_query":          card["dataset_query"],
                "name":                   card["name"],
                "display":                card.get("display", "scalar"),
                "visualization_settings": card.get("visualization_settings", {}),
                "collection_id":          card.get("collection_id"),
            })
            updated_ok.append(card_id)
            print(f"  ✅ {card_id:4d} — {card['name']}")
        except Exception as e:
            updated_fail.append(card_id)
            print(f"  ❌ {card_id:4d} — {e}")

    # 3. Add param_distrito and param_sector to dashboard parameters
    existing_params = dash.get("parameters", [])
    existing_ids    = {p["id"] for p in existing_params}
    new_params_list = existing_params + [
        p for p in NEW_PARAMS if p["id"] not in existing_ids
    ]
    _req("PUT", f"/dashboard/{dash_id}", {"parameters": new_params_list})
    print(f"\n  Parámetros del dashboard: {[p['name'] for p in new_params_list]}")

    # 4. Update dashcard parameter mappings
    # Re-fetch dashboard after param update
    dash2   = _req("GET", f"/dashboard/{dash_id}")
    dcs     = dash2.get("dashcards", [])
    tabs    = dash2.get("tabs", [])

    updated_dcs = []
    for dc in dcs:
        cid = dc.get("card_id")
        entry = {
            "id":                  dc["id"],
            "card_id":             cid,
            "row":                 dc["row"],
            "col":                 dc["col"],
            "size_x":              dc["size_x"],
            "size_y":              dc["size_y"],
            "dashboard_tab_id":    dc.get("dashboard_tab_id"),
            "visualization_settings": dc.get("visualization_settings", {}),
            "parameter_mappings":  dc.get("parameter_mappings", []),
        }
        if cid and cid in updated_ok:
            entry["parameter_mappings"] = build_parameter_mappings(
                cid, dc.get("parameter_mappings", [])
            )
        updated_dcs.append(entry)

    _req("PUT", f"/dashboard/{dash_id}/cards", {"cards": updated_dcs, "tabs": tabs})
    print(f"  Mappings actualizados para {len(updated_ok)} cards")

    if updated_fail:
        print(f"  ⚠️  Fallaron: {updated_fail}")


def main():
    for dash_id in DASHBOARD_IDS:
        process_dashboard(dash_id)
    print("\n✅ Listo. Todos los dashboards tienen filtros de Distrito y Sector.")


if __name__ == "__main__":
    main()
