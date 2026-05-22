#!/usr/bin/env python3
"""
Agrega tab "Gráficas" al dashboard 21 (DETENCIONES) de Metabase.

Flujo:
  1. Lee la estructura de una card existente para obtener DB_ID y COL_ID.
  2. Crea cards de tipo bar chart (una por métrica).
  3. Convierte el dashboard a dos tabs: KPIs (cards actuales) + Gráficas (nuevas).
"""

import json
import os
import uuid
import http.client
import ssl
from datetime import datetime, timedelta

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
# Lee variables desde .env si no están en el entorno
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    for _line in open(_env_path):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

API_BASE = os.environ["METABASE_API_BASE"]
API_KEY  = os.environ["METABASE_API_KEY"]
DASH_ID  = 21
HEADERS  = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
}

# ── HTTP HELPERS ──────────────────────────────────────────────────────────────

_SSL_CTX = ssl.create_default_context()

def _conn():
    from urllib.parse import urlparse
    host = urlparse(API_BASE).hostname
    return http.client.HTTPSConnection(host, context=_SSL_CTX)

def _request(method, path, body=None):
    hdrs = dict(HEADERS)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Length"] = str(len(data))
    conn = _conn()
    conn.request(method, f"/api{path}", body=data, headers=hdrs)
    resp = conn.getresponse()
    raw  = resp.read()
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"HTTP {resp.status} {method} {path}: {raw.decode()[:300]}")
    return json.loads(raw)

def api_get(path):
    return _request("GET", path)

def api_post(path, body):
    return _request("POST", path, body)

def api_put(path, body):
    try:
        return True, _request("PUT", path, body)
    except RuntimeError as e:
        return False, str(e)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def _last_90_days() -> str:
    today = datetime.now()
    start = today - timedelta(days=90)
    return f"{start.strftime('%Y-%m-%d')}~{today.strftime('%Y-%m-%d')}"

def make_template_tags():
    return {
        "start": {
            "id": str(uuid.uuid4()),
            "name": "start",
            "display-name": "Período",
            "type": "text",
            "required": False,
            "default": _last_90_days(),
        }
    }

def bar_query(date_field, filter_dict=None):
    """
    Pipeline de barras por día usando _fc/_sc/_ec (strings YYYYMMDD comparables).
    {{start}} queda sin comillas en el JSON final (regla crítica MongoDB + Metabase).
    """
    PH = "__PH_START__"

    match_body = {
        "$expr": {
            "$and": [
                {"$gte": ["$_fc", "$_sc"]},
                {"$lte": ["$_fc", "$_ec"]},
            ]
        }
    }
    if filter_dict:
        match_body.update(filter_dict)

    pipeline = [
        {
            "$addFields": {
                "_fc": {"$concat": [
                    {"$substrCP": [f"${date_field}", 0, 4]},
                    {"$substrCP": [f"${date_field}", 5, 2]},
                    {"$substrCP": [f"${date_field}", 8, 2]},
                ]},
                "_sc": {"$concat": [
                    {"$substrCP": [PH, 0, 4]},
                    {"$substrCP": [PH, 5, 2]},
                    {"$substrCP": [PH, 8, 2]},
                ]},
                "_ec": {"$concat": [
                    {"$substrCP": [PH, 11, 4]},
                    {"$substrCP": [PH, 16, 2]},
                    {"$substrCP": [PH, 19, 2]},
                ]},
            }
        },
        {"$match": match_body},
        {
            "$group": {
                "_id": {"f": f"${date_field}", "s": "$_fc"},
                "Total": {"$sum": 1},
            }
        },
        {"$sort": {"_id.s": 1}},
        {"$project": {"_id": "$_id.f", "Total": 1}},
    ]

    q = json.dumps(pipeline, ensure_ascii=False)
    q = q.replace(f'"{PH}"', "{{start}}")
    return q


def create_card(db_id, col_id, name, query_str, ttags, mongo_collection):
    payload = {
        "name": name,
        "display": "bar",
        "dataset_query": {
            "lib/type": "mbql/query",
            "database": db_id,
            "stages": [
                {
                    "lib/type": "mbql.stage/native",
                    "collection": mongo_collection,
                    "template-tags": ttags,
                    "native": query_str,
                }
            ],
        },
        "visualization_settings": {},
        "collection_id": col_id,
    }
    result = api_post("/card", payload)
    return result["id"]


# ── DEFINICIÓN DE CHARTS ──────────────────────────────────────────────────────
# (nombre, colección_mongo, date_field, filter_dict_o_None)

CHARTS = [
    # mv_er_detenidos
    ("Total Detenciones por día",        "mv_er_detenidos",    "fecha_evento", None),
    ("Fuero Común por día",              "mv_er_detenidos",    "fecha_evento", {"fuero": "Estatal"}),
    ("Fuero Federal por día",            "mv_er_detenidos",    "fecha_evento", {"fuero": "Federal"}),
    # mv_er_clasi_hechos
    ("FC - Delitos Contra la Salud por día",          "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "NARCOMENUDEO"}),
    ("FC - Homicidio por día",                        "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "HOMICIDIO"}),
    ("FC - Tentativa de Homicidio por día",           "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": {"$in": ["TENTATIVA DE HOMICIDIO", "TENTATIVA DE FEMINICIDIO"]}}),
    ("FC - Lesiones por día",                         "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "LESIONES"}),
    ("FC - Robo por día",                             "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "ROBO"}),
    ("FC - Delitos Sexuales por día",                 "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": {"$in": [
        "ABUSO SEXUAL", "ACOSO SEXUAL", "HOSTIGAMIENTO SEXUAL",
        "VIOLACIÓN EQUIPARADA", "VIOLACIÓN SIMPLE",
        "OTROS DELITOS QUE ATENTAN CONTRA LA LIBERTAD Y LA SEGURIDAD SEXUAL",
    ]}}),
    ("FC - Violencia Familiar por día",               "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "VIOLENCIA FAMILIAR"}),
    ("FF - Delitos Contra la Salud por día",          "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS"}),
    ("FF - Armas por día",                            "mv_er_clasi_hechos", "fecha_evento", {"nombre_delito": {"$in": [
        "DELITOS EN MATERIA DE ARMAS, EXPLOSIVOS Y OTROS MATERIALES DESTRUCTIVOS",
        "DELITOS EN MATERIA DE ARMAS Y OBJETOS PROHIBIDOS",
    ]}}),
    ("Órdenes de Aprehensión SSPM_dashboard por día",           "mv_er_clasi_hechos", "fecha_evento", {"orden_aprehension": "SI"}),
    # mv_er_faltas_admin
    ("Faltas Administrativas por día",   "mv_er_faltas_admin", "fecha_evento", None),
]


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # 1. Leer DB_ID y COL_ID desde card 339
    print("Leyendo card de referencia (339)…")
    ref   = api_get("/card/339")
    DB_ID = ref["dataset_query"]["database"]
    COL_ID= ref["collection_id"]
    print(f"  database_id={DB_ID}, collection_id={COL_ID}")

    # 2. Crear cards de gráfica
    new_card_ids = []
    for name, mongo_col, date_field, filter_dict in CHARTS:
        print(f"Creando: {name}")
        ttags = make_template_tags()
        q     = bar_query(date_field, filter_dict)
        cid   = create_card(DB_ID, COL_ID, name, q, ttags, mongo_col)
        print(f"  → card_id={cid}")
        new_card_ids.append(cid)

    # 3. Leer estado actual del dashboard
    print(f"\nLeyendo dashboard {DASH_ID}…")
    dash_data        = api_get(f"/dashboard/{DASH_ID}")
    existing_cards   = dash_data.get("dashcards", [])
    existing_tabs    = dash_data.get("tabs", [])

    # 4. Definir tabs
    if existing_tabs:
        tab_kpis_id     = existing_tabs[0]["id"]
        tab_graficas_id = -1
        tabs = existing_tabs + [{"id": -1, "name": "Gráficas", "position": len(existing_tabs)}]
    else:
        tab_kpis_id     = -1
        tab_graficas_id = -2
        tabs = [
            {"id": -1, "name": "KPIs",     "position": 0},
            {"id": -2, "name": "Gráficas", "position": 1},
        ]

    # 5. Mover dashcards existentes al tab KPIs
    updated = []
    for dc in existing_cards:
        cid = dc.get("card_id")
        entry = {
            "id":                  dc["id"],
            "card_id":             cid,
            "row":                 dc["row"],
            "col":                 dc["col"],
            "size_x":              dc["size_x"],
            "size_y":              dc["size_y"],
            "dashboard_tab_id":    tab_kpis_id,
            "visualization_settings": dc.get("visualization_settings", {}),
            "parameter_mappings":  dc.get("parameter_mappings", []),
        }
        if cid:
            entry["parameter_mappings"] = [{
                "parameter_id": "param_periodo",
                "card_id":      cid,
                "target":       ["variable", ["template-tag", "start"]],
            }]
        updated.append(entry)

    # 6. Agregar nuevas cards en tab Gráficas (2 columnas × 8 filas)
    WIDTH, HEIGHT = 12, 8
    for i, card_id in enumerate(new_card_ids):
        updated.append({
            "id":                  -(100 + i),
            "card_id":             card_id,
            "row":                 (i // 2) * HEIGHT,
            "col":                 (i %  2) * WIDTH,
            "size_x":              WIDTH,
            "size_y":              HEIGHT,
            "dashboard_tab_id":    tab_graficas_id,
            "visualization_settings": {},
            "parameter_mappings":  [{
                "parameter_id": "param_periodo",
                "card_id":      card_id,
                "target":       ["variable", ["template-tag", "start"]],
            }],
        })

    # 7. PUT dashboard/cards
    print(f"\nActualizando dashboard {DASH_ID} ({len(tabs)} tabs, {len(updated)} dashcards)…")
    ok, resp = api_put(f"/dashboard/{DASH_ID}/cards", {"cards": updated, "tabs": tabs})
    if ok:
        print("✅ Dashboard actualizado.")
        print(f"   IDs de cards creadas: {new_card_ids}")
    else:
        print(f"❌ Error: {resp}")


if __name__ == "__main__":
    main()
