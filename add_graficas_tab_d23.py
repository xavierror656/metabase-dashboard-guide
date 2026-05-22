#!/usr/bin/env python3
"""
Dashboard 23 — RESULTADOS
  1. Reescribe las 15 cards KPI: elimina el patrón {{start}}/{{end}} + $switch
     y lo reemplaza por el patrón simplificado de un solo tag {{start}}.
  2. Agrega tab "Gráficas" con una card de barras por cada KPI.
  3. Convierte el dashboard a dos tabs: KPIs + Gráficas.
"""

import json
import os
import uuid
import http.client
import ssl
from datetime import datetime, timedelta

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
DASH_ID  = 23
HEADERS  = {"Content-Type": "application/json", "x-api-key": API_KEY}

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

# ── BUILDERS ──────────────────────────────────────────────────────────────────

def _last_90_days() -> str:
    today = datetime.now()
    start = today - timedelta(days=90)
    return f"{start.strftime('%Y-%m-%d')}~{today.strftime('%Y-%m-%d')}"

def make_ttags():
    return {
        "start": {
            "id":           str(uuid.uuid4()),
            "name":         "start",
            "display-name": "Período",
            "type":         "text",
            "required":     False,
            "default":      _last_90_days(),
        }
    }

PH = "__PH_START__"

def _date_filter(date_field):
    return {
        "$expr": {
            "$and": [
                {"$gte": [f"${date_field}", {"$substrCP": [PH, 0,  10]}]},
                {"$lte": [f"${date_field}", {"$substrCP": [PH, 11, 10]}]},
            ]
        }
    }

def scalar_query(date_field, filter_dict=None, sum_expr=None):
    """
    Pipeline para card KPI (scalar).
    sum_expr: si None → $count; si dict → $group + $sum con ese expr.
    """
    match_body = _date_filter(date_field)
    if filter_dict:
        match_body.update(filter_dict)

    if sum_expr is None:
        pipeline = [{"$match": match_body}, {"$count": "total"}]
    else:
        pipeline = [
            {"$match": match_body},
            {"$group": {"_id": None, "total": sum_expr}},
        ]

    q = json.dumps(pipeline, ensure_ascii=False)
    q = q.replace(f'"{PH}"', "{{start}}")
    return q

def bar_query(date_field, filter_dict=None, sum_expr=None):
    """
    Pipeline para card de barras por día.
    sum_expr: si None → {$sum: 1}; si dict → se usa tal cual.
    """
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

    group_sum = sum_expr if sum_expr else {"$sum": 1}

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
                "Total": group_sum,
            }
        },
        {"$sort": {"_id.s": 1}},
        {"$project": {"_id": "$_id.f", "Total": 1}},
    ]

    q = json.dumps(pipeline, ensure_ascii=False)
    q = q.replace(f'"{PH}"', "{{start}}")
    return q

# ── DEFINICIÓN DE CARDS ────────────────────────────────────────────────────────
#
# (card_id, mongo_collection, date_field, filter_dict, sum_expr_scalar, sum_expr_bar)
#
# sum_expr_scalar: None = $count / dict = $group con esa expresión
# sum_expr_bar:    None = {$sum:1}     / dict = se usa tal cual

DOSIS_SUM = {"$sum": {"$convert": {
    "input": "$cantidad_sustancia", "to": "int", "onError": 0, "onNull": 0
}}}

CARDS = [
    # id   collection                   date_field      filter_dict                                                       sum_scalar  sum_bar
    (379, "mv_er_armas",                "fecha_evento", {"tipo_arma": "CARTUCHOS"},                                       None,       None),
    (380, "mv_er_detenidos",            "fecha_evento", {"fuero": "Federal"},                                             None,       None),
    (381, "mv_er_detenidos",            "fecha_evento", {"fuero": "Estatal"},                                             None,       None),
    (382, "mv_er_sustancias",           "fecha_evento", None,                                                             {"$sum": "$cantidad_kg"}, {"$sum": "$cantidad_kg"}),
    (383, "mv_er_armas",                "fecha_evento", {"clasificacion_arma": "FUEGO", "tipo_arma": "ARMA LARGA"},       None,       None),
    (384, "mv_er_armas",                "fecha_evento", {"clasificacion_arma": "FUEGO", "tipo_arma": "ARMA CORTA"},       None,       None),
    (385, "mv_er_clasi_hechos",         "fecha_evento", {"nombre_delito": "ORDEN DE APREHENSION VIGENTE"},                None,       None),
    (386, "mv_er_armas",                "fecha_evento", {"clasificacion_arma": "FUEGO"},                                  None,       None),
    (387, "mv_reporte_vehiculos_general","fecha_evento", {"motivo_aseguramiento": "VEHICULO RECUPERDO CON REPORTE DE ROBO"}, None,    None),
    (388, "mv_reporte_vehiculos_general","fecha_evento", {"motivo_aseguramiento": "INVOLUCRADO EN DELITOS"},              None,       None),
    (389, "mv_er_clasi_hechos",         "fecha_evento", {"nombre_delito": {"$in": ["NARCOMENUDEO", "DELITOS FEDERALES RELACIONADOS CON NARCOTICOS"]}}, None, None),
    (390, "mv_er_sustancias",           "fecha_evento", None,                                                             DOSIS_SUM,  DOSIS_SUM),
    (391, "mv_er_faltas_admin",         "fecha_evento", None,                                                             None,       None),
    (392, "mv_reporte_vehiculos_general","fecha_evento", None,                                                            None,       None),
    (393, "mv_reporte_vehiculos_general","fecha_evento", {"tipo_reporte": "POR FALTA"},                                   None,       None),
]

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # 1. Leer DB_ID y COL_ID desde la primera card
    ref   = _req("GET", f"/card/{CARDS[0][0]}")
    DB_ID = ref["dataset_query"]["database"]
    COL_ID= ref["collection_id"]
    print(f"database_id={DB_ID}, collection_id={COL_ID}\n")

    # 2. Reescribir cards KPI existentes con el patrón nuevo
    print("── Reescribiendo KPIs ──")
    for card_id, mongo_col, date_field, filt, sum_sc, _ in CARDS:
        card = _req("GET", f"/card/{card_id}")
        name = card["name"]
        ttags = make_ttags()
        q     = scalar_query(date_field, filt, sum_sc)
        dq    = card["dataset_query"]
        dq["stages"][0]["native"]        = q
        dq["stages"][0]["template-tags"] = ttags
        dq["stages"][0]["collection"]    = mongo_col
        payload = {
            "dataset_query":          dq,
            "name":                   name,
            "display":                card.get("display", "scalar"),
            "visualization_settings": card.get("visualization_settings", {}),
            "collection_id":          card.get("collection_id"),
        }
        _req("PUT", f"/card/{card_id}", payload)
        print(f"  ✅ {card_id} — {name}")

    # 3. Crear cards de gráfica
    print("\n── Creando Gráficas ──")
    new_card_ids = []
    for card_id, mongo_col, date_field, filt, _, sum_bar in CARDS:
        card  = _req("GET", f"/card/{card_id}")
        name  = card["name"] + " por día"
        ttags = make_ttags()
        q     = bar_query(date_field, filt, sum_bar)
        payload = {
            "name":    name,
            "display": "bar",
            "dataset_query": {
                "lib/type": "mbql/query",
                "database":  DB_ID,
                "stages": [{
                    "lib/type":      "mbql.stage/native",
                    "collection":    mongo_col,
                    "template-tags": ttags,
                    "native":        q,
                }],
            },
            "visualization_settings": {},
            "collection_id": COL_ID,
        }
        result = _req("POST", "/card", payload)
        cid    = result["id"]
        print(f"  ✅ {cid} — {name}")
        new_card_ids.append(cid)

    # 4. Leer dashboard
    print(f"\n── Actualizando dashboard {DASH_ID} ──")
    dash          = _req("GET", f"/dashboard/{DASH_ID}")
    existing_dcs  = dash.get("dashcards", [])
    existing_tabs = dash.get("tabs", [])

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

    # 5. Mover dashcards existentes a tab KPIs
    updated = []
    for dc in existing_dcs:
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

    # 6. Agregar cards de gráfica en tab Gráficas (2 col × 8 filas)
    WIDTH, HEIGHT = 12, 8
    for i, cid in enumerate(new_card_ids):
        updated.append({
            "id":                  -(100 + i),
            "card_id":             cid,
            "row":                 (i // 2) * HEIGHT,
            "col":                 (i %  2) * WIDTH,
            "size_x":              WIDTH,
            "size_y":              HEIGHT,
            "dashboard_tab_id":    tab_graficas_id,
            "visualization_settings": {},
            "parameter_mappings":  [{
                "parameter_id": "param_periodo",
                "card_id":      cid,
                "target":       ["variable", ["template-tag", "start"]],
            }],
        })

    ok, resp = True, _req("PUT", f"/dashboard/{DASH_ID}/cards", {"cards": updated, "tabs": tabs})
    print(f"✅ Dashboard {DASH_ID} actualizado: {len(tabs)} tabs, {len(updated)} dashcards")
    print(f"   Cards de gráfica: {new_card_ids}")


if __name__ == "__main__":
    main()
