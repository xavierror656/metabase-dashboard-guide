#!/usr/bin/env python3
"""
SSPM_dashboard — Setup automatizado de dashboards en Metabase vía API.

Aplica el flujo descrito en `dashboardproyect.md` con las correcciones
documentadas en `metabase-dashboard-guide.md`:

  - http.client directo (urllib/requests dan 403 en este servidor)
  - Lectura SOLO de SSPM_dashboard_vistas.mv_*  (nunca ParteInformativa)
  - Template tag único {{start}} con rango "YYYY-MM-DD~YYYY-MM-DD"
  - Filtros opcionales con [[ ,{"campo": {{tag}}} ]]
  - PUT /api/dashboard/:id/cards incluyendo siempre `tabs`
  - Idempotente: busca antes de crear (collections, dashboards, cards)
  - Modo DRY_RUN: muestra qué crearía sin tocar Metabase

Uso:
  DRY_RUN=true  python3 sspm_dashboard_setup.py        # vista previa
  DRY_RUN=false python3 sspm_dashboard_setup.py        # ejecutar de verdad
  python3 sspm_dashboard_setup.py --only "00 Ejecutivo" # solo un dashboard
"""

from __future__ import annotations

import argparse
import http.client
import json
import logging
import os
import ssl
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ───────────────────────────────────────────────────────────────────────────────

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    for _line in open(_env_path):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

API_BASE       = os.environ["METABASE_API_BASE"].rstrip("/")
API_KEY        = os.environ["METABASE_API_KEY"]
MONGO_DB_NAME  = os.environ.get("MONGO_DB_NAME", "Vistas_e")
DRY_RUN        = os.environ.get("DRY_RUN", "true").lower() in ("1", "true", "yes")

COLLECTION_PARENT = "SSPM_dashboard"   # padre de todas las collections del proyecto

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("SSPM_dashboard")

# ───────────────────────────────────────────────────────────────────────────────
# HTTP (http.client directo — patrón validado para este servidor)
# ───────────────────────────────────────────────────────────────────────────────

_SSL_CTX = ssl.create_default_context()
_HEADERS = {"Content-Type": "application/json", "x-api-key": API_KEY}


def _request(method: str, path: str, body: Any = None) -> Any:
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    hdrs = dict(_HEADERS)
    if data:
        hdrs["Content-Length"] = str(len(data))
    host = urlparse(API_BASE).hostname
    conn = http.client.HTTPSConnection(host, context=_SSL_CTX, timeout=60)
    conn.request(method, f"/api{path}", body=data, headers=hdrs)
    resp = conn.getresponse()
    raw  = resp.read()
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"HTTP {resp.status} {method} {path}: {raw.decode()[:400]}")
    return json.loads(raw) if raw.strip() else {}


def api_get(path: str, default_on_404: Any = None) -> Any:
    try:
        return _request("GET", path)
    except RuntimeError as e:
        if default_on_404 is not None and "HTTP 404" in str(e):
            return default_on_404
        raise


def api_post(path: str, body: Any) -> Any:
    if DRY_RUN:
        log.info(f"[DRY_RUN] POST {path}  →  {_short(body)}")
        return {"id": _fake_id(path, body), "_dry_run": True}
    return _request("POST", path, body)


def api_put(path: str, body: Any) -> Any:
    if DRY_RUN:
        log.info(f"[DRY_RUN] PUT  {path}  →  {_short(body)}")
        return {"_dry_run": True}
    return _request("PUT", path, body)


def _short(body: Any, n: int = 140) -> str:
    s = json.dumps(body, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"


_FAKE_ID_COUNTER = [10_000]
def _fake_id(path: str, _body: Any) -> int:
    _FAKE_ID_COUNTER[0] += 1
    return _FAKE_ID_COUNTER[0]


# ───────────────────────────────────────────────────────────────────────────────
# DISCOVERY — buscar antes de crear (idempotencia)
# ───────────────────────────────────────────────────────────────────────────────

def find_database(name: str) -> dict | None:
    dbs = api_get("/database")
    items = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    for db in items:
        if db.get("name") == name:
            return db
    return None


def find_collection(name: str, parent_id: int | None = None) -> dict | None:
    cols = api_get("/collection")
    for c in cols:
        if c.get("name") == name and c.get("parent_id") == parent_id:
            return c
    return None


def get_or_create_collection(name: str, parent_id: int | None = None) -> int:
    existing = find_collection(name, parent_id)
    if existing:
        log.info(f"  collection ya existe:  {name}  (id={existing['id']})")
        return existing["id"]
    payload = {"name": name, "color": "#509EE3"}
    if parent_id is not None:
        payload["parent_id"] = parent_id
    res = api_post("/collection", payload)
    log.info(f"  collection creada:     {name}  (id={res.get('id')})")
    return res["id"]


def find_dashboard(name: str, collection_id: int) -> dict | None:
    res = api_get(f"/collection/{collection_id}/items?models=dashboard", default_on_404={"data": []})
    items = res.get("data", []) if isinstance(res, dict) else res
    for it in items:
        if it.get("name") == name and it.get("model") == "dashboard":
            return it
    return None


def get_or_create_dashboard(name: str, collection_id: int, description: str = "") -> int:
    existing = find_dashboard(name, collection_id)
    if existing:
        log.info(f"  dashboard ya existe:   {name}  (id={existing['id']})")
        return existing["id"]
    res = api_post("/dashboard", {
        "name":          name,
        "description":   description,
        "collection_id": collection_id,
    })
    log.info(f"  dashboard creado:      {name}  (id={res.get('id')})")
    return res["id"]


def find_card(name: str, collection_id: int) -> dict | None:
    res = api_get(f"/collection/{collection_id}/items?models=card", default_on_404={"data": []})
    items = res.get("data", []) if isinstance(res, dict) else res
    for it in items:
        if it.get("name") == name and it.get("model") == "card":
            return it
    return None


# ───────────────────────────────────────────────────────────────────────────────
# QUERY BUILDERS — patrones de metabase-dashboard-guide.md
# ───────────────────────────────────────────────────────────────────────────────

PH = "__PH_START__"   # placeholder reemplazado por {{start}} sin comillas


def _date_range_match(date_field: str = "fecha_evento") -> dict:
    """Filtro $match por rango de fechas extrayendo de {{start}}: 'YYYY-MM-DD~YYYY-MM-DD'."""
    return {
        "$expr": {
            "$and": [
                {"$gte": [f"${date_field}", {"$substrCP": [PH, 0, 10]}]},
                {"$lte": [f"${date_field}", {"$substrCP": [PH, 11, 10]}]},
            ]
        }
    }


def _finalize(pipeline: list) -> str:
    """Serializa el pipeline y reemplaza el placeholder por {{start}} sin comillas."""
    q = json.dumps(pipeline, ensure_ascii=False)
    return q.replace(f'"{PH}"', "{{start}}")


def q_kpi_count(date_field: str = "fecha_evento", extra_match: dict | None = None) -> str:
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    return _finalize([{"$match": match}, {"$count": "total"}])


def q_kpi_sum(field: str, date_field: str = "fecha_evento", extra_match: dict | None = None) -> str:
    """Suma con $project para evitar el null que devuelve scalar cuando _id queda en el resultado."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    return _finalize([
        {"$match": match},
        {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
        {"$project": {"_id": 0, "total": 1}},
    ])


def q_bar_by_day(date_field: str = "fecha_evento", extra_match: dict | None = None) -> str:
    """Eventos por día. Usa _fc/_sc/_ec strings YYYYMMDD para comparación lexicográfica."""
    match_body = {
        "$expr": {"$and": [{"$gte": ["$_fc", "$_sc"]}, {"$lte": ["$_fc", "$_ec"]}]}
    }
    if extra_match:
        match_body = {"$and": [match_body, extra_match]}
    pipeline = [
        {"$addFields": {
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
        }},
        {"$match": match_body},
        {"$group": {"_id": {"f": f"${date_field}", "s": "$_fc"}, "Total": {"$sum": 1}}},
        {"$sort": {"_id.s": 1}},
        {"$project": {"_id": "$_id.f", "Total": 1}},
    ]
    return _finalize(pipeline)


def q_bar_by_category(category_field: str, date_field: str = "fecha_evento",
                       limit: int | None = None, extra_match: dict | None = None) -> str:
    """Conteo por categoría (distrito, turno, motivo, etc.) filtrado por rango de fechas."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    pipeline = [
        {"$match": match},
        {"$group": {"_id": f"${category_field}", "Total": {"$sum": 1}}},
        {"$sort": {"Total": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    pipeline.append({"$project": {"_id": 0, category_field: "$_id", "Total": 1}})
    return _finalize(pipeline)


def q_top_by_sum(category_field: str, sum_field: str, date_field: str = "fecha_evento",
                  limit: int | None = None, extra_match: dict | None = None) -> str:
    """Top categorías ordenadas por suma de un campo numérico (no por conteo)."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    pipeline = [
        {"$match": match},
        {"$group": {"_id": f"${category_field}", "Total": {"$sum": f"${sum_field}"}}},
        {"$sort": {"Total": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    pipeline.append({"$project": {"_id": 0, category_field: "$_id", "Total": 1}})
    return _finalize(pipeline)


def q_table(fields: list[str], date_field: str | None = "fecha_evento",
            extra_match: dict | None = None, limit: int = 1000) -> str:
    project = {f: 1 for f in fields}
    project["_id"] = 0
    pipeline: list = []
    if date_field:
        match = _date_range_match(date_field)
        if extra_match:
            match = {"$and": [match, extra_match]}
        pipeline.append({"$match": match})
    elif extra_match:
        pipeline.append({"$match": extra_match})
    pipeline.extend([{"$project": project}, {"$limit": limit}])
    return _finalize(pipeline)


def q_map(date_field: str = "fecha_evento", flag_field: str | None = None) -> str:
    """
    Eventos georreferenciados desde mv_ubicacion.
    Si flag_field se pasa (ej. 'cantidad_detenidos'), filtra a > 0.
    """
    extra = {flag_field: {"$gt": 0}} if flag_field else None
    match = _date_range_match(date_field)
    if extra:
        match = {"$and": [match, extra]}
    match = {"$and": [match, {"latitud": {"$ne": None}}, {"longitud": {"$ne": None}}]}
    return _finalize([
        {"$match": match},
        {"$project": {
            "_id": 0, "latitud": 1, "longitud": 1, "folio": 1,
            "fecha_evento": 1, "distrito": 1, "colonia": 1, "motivo_intervencion": 1,
        }},
        {"$limit": 5000},
    ])


def q_map_via_lookup(target_collection: str, date_field: str = "fecha_evento") -> str:
    """
    Mapa para colecciones cuyas coords están sparse: parte de mv_ubicacion y
    cruza por folio con la colección entidad. Útil para Víctimas, Armas, etc.
    """
    match = {"$and": [
        _date_range_match(date_field),
        {"latitud":  {"$ne": None}},
        {"longitud": {"$ne": None}},
    ]}
    return _finalize([
        {"$match": match},
        {"$lookup": {"from": target_collection,
                     "localField": "folio", "foreignField": "folio", "as": "_e"}},
        {"$match": {"_e.0": {"$exists": True}}},
        {"$project": {
            "_id": 0, "latitud": 1, "longitud": 1, "folio": 1,
            "fecha_evento": 1, "distrito": 1, "colonia": 1,
        }},
        {"$limit": 3000},
    ])


def q_kpi_count_nodate(extra_match: dict | None = None) -> str:
    """Conteo sin filtro de fecha — para vistas con fechas corruptas o pre-agregadas."""
    pipeline: list = []
    if extra_match:
        pipeline.append({"$match": extra_match})
    pipeline.append({"$count": "total"})
    return _finalize(pipeline)


def q_kpi_sum_nodate(field: str, extra_match: dict | None = None) -> str:
    """Suma sin filtro de fecha."""
    pipeline: list = []
    if extra_match:
        pipeline.append({"$match": extra_match})
    pipeline += [
        {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
        {"$project": {"_id": 0, "total": 1}},
    ]
    return _finalize(pipeline)


def q_bar_by_category_nodate(category_field: str, limit: int | None = None,
                              extra_match: dict | None = None) -> str:
    """Conteo por categoría sin filtro de fecha."""
    pipeline: list = []
    if extra_match:
        pipeline.append({"$match": extra_match})
    pipeline += [
        {"$group": {"_id": f"${category_field}", "Total": {"$sum": 1}}},
        {"$sort": {"Total": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    pipeline.append({"$project": {"_id": 0, category_field: "$_id", "Total": 1}})
    return _finalize(pipeline)


def q_top_by_sum_nodate(category_field: str, sum_field: str,
                        limit: int | None = None, extra_match: dict | None = None) -> str:
    """Top categorías por suma de campo numérico, sin filtro de fecha."""
    pipeline: list = []
    if extra_match:
        pipeline.append({"$match": extra_match})
    pipeline += [
        {"$group": {"_id": f"${category_field}", "Total": {"$sum": f"${sum_field}"}}},
        {"$sort": {"Total": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    pipeline.append({"$project": {"_id": 0, category_field: "$_id", "Total": 1}})
    return _finalize(pipeline)


def _edad_int_expr(edad_field: str = "edad") -> dict:
    """`$convert` defensivo: edad string → int. Strings inválidos/vacíos/null → -1."""
    return {"$convert": {"input": f"${edad_field}", "to": "int",
                         "onError": -1, "onNull": -1}}


def edad_between(lo: int, hi: int, edad_field: str = "edad") -> dict:
    """Devuelve un $expr que matchea edad ∈ [lo, hi). Excluye edades inválidas (-1)."""
    e = _edad_int_expr(edad_field)
    return {"$expr": {"$and": [{"$gte": [e, lo]}, {"$lt": [e, hi]}]}}


def q_age_range(date_field: str = "fecha_evento", edad_field: str = "edad",
                extra_match: dict | None = None) -> str:
    """
    Conteo por rango de edad. Convierte string→int defensivamente y descarta
    edades inválidas (vacías, no-numéricas, fuera de 0..120).
    Recomendación: mover esta lógica al ETL de materialización.
    """
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    e = _edad_int_expr(edad_field)
    return _finalize([
        {"$match": match},
        {"$addFields": {"_edad_n": e}},
        {"$match": {"_edad_n": {"$gte": 0, "$lte": 120}}},
        {"$addFields": {
            "rango_edad": {"$switch": {
                "branches": [
                    {"case": {"$lt": ["$_edad_n", 18]}, "then": "1. 0-17 Menor"},
                    {"case": {"$lt": ["$_edad_n", 30]}, "then": "2. 18-29 Joven"},
                    {"case": {"$lt": ["$_edad_n", 45]}, "then": "3. 30-44 Adulto"},
                    {"case": {"$lt": ["$_edad_n", 60]}, "then": "4. 45-59 Adulto maduro"},
                ],
                "default": "5. 60+ Adulto mayor",
            }}
        }},
        {"$group": {"_id": "$rango_edad", "Total": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "rango_edad": "$_id", "Total": 1}},
    ])


def q_avg(field: str, date_field: str = "fecha_evento",
          extra_match: dict | None = None, cast: str | None = None) -> str:
    """
    Promedio de un campo. cast='int' lo convierte string→int defensivamente
    (necesario para `edad` que MongoDB guarda como string en estas vistas).
    """
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    pipeline: list = [{"$match": match}]
    if cast == "int":
        e = {"$convert": {"input": f"${field}", "to": "int", "onError": -1, "onNull": -1}}
        pipeline.append({"$addFields": {"_n": e}})
        pipeline.append({"$match": {"_n": {"$gte": 0, "$lte": 120}}})
        avg_target = "$_n"
    else:
        avg_target = f"${field}"
    pipeline += [
        {"$group": {"_id": None, "promedio": {"$avg": avg_target}}},
        {"$project": {"_id": 0, "promedio": {"$round": ["$promedio", 1]}}},
    ]
    return _finalize(pipeline)


def q_distinct_count(field: str, date_field: str = "fecha_evento", extra_match: dict | None = None) -> str:
    """Cardinalidad de un campo (ej. agentes únicos)."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    return _finalize([
        {"$match": match},
        {"$group": {"_id": f"${field}"}},
        {"$count": "total"},
    ])


def q_heatmap_distrito_turno(date_field: str = "fecha_evento", extra_match: dict | None = None) -> str:
    """Pivot distrito × turno para mostrar como heatmap o tabla pivotada."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    return _finalize([
        {"$match": match},
        {"$group": {"_id": {"d": "$distrito", "t": "$turno"}, "Total": {"$sum": 1}}},
        {"$sort": {"_id.d": 1, "_id.t": 1}},
        {"$project": {"_id": 0, "distrito": "$_id.d", "turno": "$_id.t", "Total": 1}},
    ])


def q_stacked_by_month(category_field: str, date_field: str = "fecha_evento",
                        extra_match: dict | None = None) -> str:
    """Serie mensual segmentada por categoría (para gráficas de área apilada)."""
    match = _date_range_match(date_field)
    if extra_match:
        match = {"$and": [match, extra_match]}
    return _finalize([
        {"$match": match},
        {"$addFields": {"_mes": {"$substrCP": [f"${date_field}", 0, 7]}}},
        {"$group": {"_id": {"m": "$_mes", "c": f"${category_field}"}, "Total": {"$sum": 1}}},
        {"$sort": {"_id.m": 1}},
        {"$project": {"_id": 0, "mes": "$_id.m", category_field: "$_id.c", "Total": 1}},
    ])


# ───────────────────────────────────────────────────────────────────────────────
# CARDS — fábrica
# ───────────────────────────────────────────────────────────────────────────────

OPTIONAL_FILTER_FIELDS = ("distrito", "sector")  # filtros globales opcionales por defecto


def _wrap_match_with_optional_filters(query_str: str, fields: tuple[str, ...]) -> str:
    """Envuelve el primer $match en $and y agrega bloques [[ ,{"campo": {{tag}}} ]] opcionales."""
    idx = query_str.find('"$match"')
    if idx == -1:
        return query_str
    brace_start = query_str.index('{', idx + len('"$match"'))
    depth = 0
    end = -1
    for i in range(brace_start, len(query_str)):
        if query_str[i] == '{':
            depth += 1
        elif query_str[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return query_str
    original_body = query_str[brace_start:end + 1]
    optional = "".join(f' [[ ,{{"{f}": {{{{{f}}}}}}} ]]' for f in fields)
    new_body = f'{{"$and": [{original_body}{optional}]}}'
    return query_str[:brace_start] + new_body + query_str[end + 1:]


def make_template_tags(extra_fields: tuple[str, ...] = ()) -> dict:
    ttags = {
        "start": {
            "id":           str(uuid.uuid4()),
            "name":         "start",
            "display-name": "Período",
            "type":         "text",
            "required":     False,
            "default":      "2025-01-01~2025-12-31",
        }
    }
    for f in extra_fields:
        ttags[f] = {
            "id":           str(uuid.uuid4()),
            "name":         f,
            "display-name": f.capitalize(),
            "type":         "text",
            "required":     False,
        }
    return ttags


def create_card(*, db_id: int, collection_id: int, name: str, mongo_collection: str,
                query_str: str, display: str = "scalar",
                viz: dict | None = None,
                optional_filters: tuple[str, ...] = OPTIONAL_FILTER_FIELDS) -> int:
    existing = find_card(name, collection_id)
    if existing:
        log.info(f"    card ya existe:    [{display:>5}] {name}  (id={existing['id']})")
        return existing["id"]

    if optional_filters:
        query_str = _wrap_match_with_optional_filters(query_str, optional_filters)

    ttags = make_template_tags(optional_filters)
    payload = {
        "name":    name,
        "display": display,
        "dataset_query": {
            "lib/type": "mbql/query",
            "database": db_id,
            "stages": [{
                "lib/type":      "mbql.stage/native",
                "collection":    mongo_collection,
                "template-tags": ttags,
                "native":        query_str,
            }],
        },
        "visualization_settings": viz or {},
        "collection_id": collection_id,
    }
    res = api_post("/card", payload)
    log.info(f"    card creada:       [{display:>5}] {name}  (id={res.get('id')})")
    return res["id"]


# ───────────────────────────────────────────────────────────────────────────────
# DASHBOARDS — parámetros, tabs, layouts
# ───────────────────────────────────────────────────────────────────────────────

DISTRITOS = ["CENTRO", "ORIENTE", "PONIENTE", "RIVERAS", "SUR", "UNIVERSIDAD", "VALLE"]


def _last_90_days() -> str:
    """Calcula rango últimos 90 días en formato 'YYYY-MM-DD~YYYY-MM-DD'."""
    today = datetime.now()
    start = today - timedelta(days=90)
    return f"{start.strftime('%Y-%m-%d')}~{today.strftime('%Y-%m-%d')}"


def standard_parameters() -> list[dict]:
    """Parámetros globales del dashboard. Coincide con metabase-dashboard-guide §7."""
    return [
        {
            "id":      "param_periodo",
            "name":    "Período",
            "slug":    "periodo",
            "type":    "date/range",
            "default": _last_90_days(),
        },
        {
            "id":      "param_distrito",
            "name":    "Distrito",
            "slug":    "distrito",
            "type":    "string/=",
            "values_query_type":  "list",
            "values_source_type": "static-list",
            "values_source_config": {"values": DISTRITOS},
        },
        {
            "id":   "param_sector",
            "name": "Sector",
            "slug": "sector",
            "type": "string/=",
        },
    ]


def _mappings_for_card(card_id: int, fields: tuple[str, ...] = OPTIONAL_FILTER_FIELDS) -> list[dict]:
    m = [{
        "parameter_id": "param_periodo",
        "card_id":      card_id,
        "target":       ["variable", ["template-tag", "start"]],
    }]
    for f in fields:
        m.append({
            "parameter_id": f"param_{f}",
            "card_id":      card_id,
            "target":       ["variable", ["template-tag", f]],
        })
    return m


def push_dashboard_layout(dash_id: int, *, kpi_card_ids: list[int],
                          chart_card_ids: list[int],
                          table_card_ids: list[int] | None = None,
                          map_card_ids: list[int] | None = None) -> None:
    """
    Layout de un solo tab (sin pestañas):
      - KPIs arriba (4 por fila, ancho 6, alto 4)   → fila 0..k
      - Gráficas (2 por fila, ancho 12, alto 8)
      - Mapas (full width, alto 14)
      - Tablas (full width, alto 12)
    """
    api_put(f"/dashboard/{dash_id}", {"parameters": standard_parameters()})

    cards: list[dict] = []
    next_dc_id = -1
    row_cursor = 0

    KPI_W, KPI_H, KPI_PER_ROW = 6, 4, 4
    if kpi_card_ids:
        for i, cid in enumerate(kpi_card_ids):
            cards.append({
                "id": next_dc_id, "card_id": cid,
                "row": row_cursor + (i // KPI_PER_ROW) * KPI_H,
                "col": (i % KPI_PER_ROW) * KPI_W,
                "size_x": KPI_W, "size_y": KPI_H,
                "dashboard_tab_id": None,
                "visualization_settings": {},
                "parameter_mappings": _mappings_for_card(cid),
            })
            next_dc_id -= 1
        rows_used = ((len(kpi_card_ids) + KPI_PER_ROW - 1) // KPI_PER_ROW) * KPI_H
        row_cursor += rows_used

    CH_W, CH_H, CH_PER_ROW = 12, 8, 2
    if chart_card_ids:
        for i, cid in enumerate(chart_card_ids):
            cards.append({
                "id": next_dc_id, "card_id": cid,
                "row": row_cursor + (i // CH_PER_ROW) * CH_H,
                "col": (i % CH_PER_ROW) * CH_W,
                "size_x": CH_W, "size_y": CH_H,
                "dashboard_tab_id": None,
                "visualization_settings": {},
                "parameter_mappings": _mappings_for_card(cid),
            })
            next_dc_id -= 1
        rows_used = ((len(chart_card_ids) + CH_PER_ROW - 1) // CH_PER_ROW) * CH_H
        row_cursor += rows_used

    if map_card_ids:
        for cid in map_card_ids:
            cards.append({
                "id": next_dc_id, "card_id": cid,
                "row": row_cursor, "col": 0, "size_x": 24, "size_y": 14,
                "dashboard_tab_id": None,
                "visualization_settings": {
                    "map.type": "pin",
                    "map.latitude_column": "latitud",
                    "map.longitude_column": "longitud",
                },
                "parameter_mappings": _mappings_for_card(cid),
            })
            next_dc_id -= 1
            row_cursor += 14

    if table_card_ids:
        for cid in table_card_ids:
            cards.append({
                "id": next_dc_id, "card_id": cid,
                "row": row_cursor, "col": 0, "size_x": 24, "size_y": 12,
                "dashboard_tab_id": None,
                "visualization_settings": {},
                "parameter_mappings": _mappings_for_card(cid),
            })
            next_dc_id -= 1
            row_cursor += 12

    api_put(f"/dashboard/{dash_id}/cards", {"cards": cards, "tabs": []})


# ───────────────────────────────────────────────────────────────────────────────
# DEFINICIÓN DECLARATIVA DE LOS 13 DASHBOARDS
# ───────────────────────────────────────────────────────────────────────────────
#
# Cada dashboard:
#   collection: subcollection bajo "SSPM_dashboard"
#   description: descripción visible en Metabase
#   kpis:    [{name, mongo, query_fn, args}]   → cards display=scalar
#   charts:  [{name, mongo, query_fn, args, display, viz?}]
#   table:   {name, mongo, fields}             → opcional
#   map:     {name, mongo}                     → opcional
#
# query_fn nombres válidos:  "count", "sum", "bar_day", "bar_cat", "table", "map"
#
# Las definiciones siguen el catálogo de dashboardproyect.md §1-13.

DASHBOARDS: list[dict] = [
    # 1. EJECUTIVO ─────────────────────────────────────────────────────────────
    {
        "collection": "00 Ejecutivo",
        "name":       "Dashboard Ejecutivo General",
        "description": "Visión global de Partes Informativas, detenidos, víctimas y aseguramientos.",
        "kpis": [
            {"name": "Total Partes Informativas",   "mongo": "mv_resumen_pi",   "fn": "count"},
            {"name": "Total Detenidos",             "mongo": "mv_er_detenidos", "fn": "count"},
            {"name": "Total Víctimas",              "mongo": "mv_er_victimas",  "fn": "count"},
            {"name": "Total Armas Aseguradas",      "mongo": "mv_er_armas",     "fn": "count"},
            {"name": "Total Vehículos Involucrados","mongo": "mv_er_vehiculos", "fn": "count"},
            {"name": "Total Sustancias",            "mongo": "mv_er_sustancias","fn": "count"},
            {"name": "Total Objetos",               "mongo": "mv_er_objetos",   "fn": "count"},
            {"name": "Eventos con Coordenadas",     "mongo": "mv_ubicacion",    "fn": "count"},
            {"name": "Eventos únicos",              "mongo": "mv_resumen_pi",   "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con eventos",       "mongo": "mv_resumen_pi",   "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Eventos por día",             "mongo": "mv_resumen_pi", "fn": "bar_day",  "display": "line"},
            {"name": "Eventos por distrito",        "mongo": "mv_resumen_pi", "fn": "bar_cat",  "args": {"category_field": "distrito"},            "display": "bar"},
            {"name": "Eventos por turno",           "mongo": "mv_resumen_pi", "fn": "bar_cat",  "args": {"category_field": "turno"},               "display": "pie"},
            {"name": "Motivos de intervención",     "mongo": "mv_resumen_pi", "fn": "bar_cat",  "args": {"category_field": "motivo_intervencion"}, "display": "bar"},
            {"name": "Top 10 colonias",             "mongo": "mv_resumen_pi", "fn": "bar_cat",  "args": {"category_field": "colonia", "limit": 10}, "display": "bar"},
            {"name": "Heatmap distrito × turno",    "mongo": "mv_resumen_pi", "fn": "heatmap_dist_turno", "display": "table"},
            {"name": "Eventos por mes y distrito",  "mongo": "mv_resumen_pi", "fn": "stacked_month", "args": {"category_field": "distrito"}, "display": "area"},
        ],
        "map": {"name": "Mapa de eventos", "mongo": "mv_ubicacion"},
        "tables": [
            {"name": "Detalle de partes informativos", "mongo": "mv_resumen_pi",
             "fields": ["folio", "fecha_evento", "hora_evento", "distrito", "colonia", "turno", "motivo_intervencion", "cantidad_detenidos", "cantidad_armas", "cantidad_sustancias", "cantidad_vehiculos", "cantidad_objetos"]},
        ],
    },

    # 2. OPERATIVO ─────────────────────────────────────────────────────────────
    # mv_operativa NO tiene fecha_evento (es un rollup pre-agregado), por lo que
    # los KPIs/charts con filtro de período devuelven vacío. Usamos solo
    # mv_er_agentes (que sí tiene fecha_evento) + counts cruzados de otras vistas.
    # Anonimizado: agrupamos por numero_empleado, no por nombre.
    {
        "collection": "01 Operativo",
        "name":       "Dashboard Operativo",
        "description": "Carga operativa, agentes y participaciones (anonimizadas por número de empleado).",
        "kpis": [
            {"name": "Total Participaciones",         "mongo": "mv_er_agentes",  "fn": "count"},
            {"name": "Agentes únicos",                "mongo": "mv_er_agentes",  "fn": "distinct_count", "args": {"field": "numero_empleado"}},
            {"name": "Eventos atendidos",             "mongo": "mv_er_agentes",  "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con participación",   "mongo": "mv_er_agentes",  "fn": "distinct_count", "args": {"field": "distrito"}},
            {"name": "Total Detenidos",               "mongo": "mv_er_detenidos","fn": "count"},
            {"name": "Total Víctimas",                "mongo": "mv_er_victimas", "fn": "count"},
            {"name": "Total Armas",                   "mongo": "mv_er_armas",    "fn": "count"},
        ],
        "charts": [
            {"name": "Participaciones por distrito",  "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Participaciones por turno",     "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "turno"}, "display": "pie"},
            {"name": "Participaciones por puesto",    "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "puesto"}},
            {"name": "Top 20 agentes (núm empleado)", "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "numero_empleado", "limit": 20}, "display": "row"},
            {"name": "Heatmap distrito × turno",      "mongo": "mv_er_agentes", "fn": "heatmap_dist_turno", "display": "table"},
            {"name": "Participaciones por mes y puesto","mongo": "mv_er_agentes", "fn": "stacked_month", "args": {"category_field": "puesto"}, "display": "area"},
            {"name": "Participaciones por día",       "mongo": "mv_er_agentes", "fn": "bar_day"},
        ],
        "tables": [
            {"name": "Detalle de participaciones", "mongo": "mv_er_agentes",
             "fields": ["folio", "fecha_evento", "distrito", "distrito_agente", "turno", "puesto", "numero_empleado"]},
        ],
        "maps": [
            {"name": "Mapa de participaciones", "mongo": "mv_ubicacion", "fn": "map_lookup", "args": {"target_collection": "mv_er_agentes"}},
        ],
    },

    # 3. DELITOS ───────────────────────────────────────────────────────────────
    # mv_er_clasi_hechos NO tiene 'orden_aprehension'. KPI removido.
    {
        "collection": "02 Delitos",
        "name":       "Dashboard Delitos",
        "description": "Clasificación, modalidad y distribución geográfica de delitos.",
        "kpis": [
            {"name": "Total Delitos",              "mongo": "mv_er_clasi_hechos", "fn": "count"},
            {"name": "Delitos con violencia",      "mongo": "mv_er_clasi_hechos", "fn": "count", "extra": {"hubo_violencia": "SI"}},
            {"name": "Eventos únicos",             "mongo": "mv_er_clasi_hechos", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con delitos",      "mongo": "mv_er_clasi_hechos", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Top delitos por nombre",     "mongo": "mv_er_clasi_hechos", "fn": "bar_cat", "args": {"category_field": "nombre_delito", "limit": 15}, "display": "row"},
            {"name": "Top subdelitos",             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat", "args": {"category_field": "nombre_subdelito", "limit": 15}, "display": "row"},
            {"name": "Delitos por clasificación",  "mongo": "mv_er_clasi_hechos", "fn": "bar_cat", "args": {"category_field": "clasificacion_delito"},      "display": "bar"},
            {"name": "Delitos por distrito",       "mongo": "mv_er_clasi_hechos", "fn": "bar_cat", "args": {"category_field": "distrito"},                  "display": "bar"},
            {"name": "Delitos por modalidad",      "mongo": "mv_er_clasi_hechos", "fn": "bar_cat", "args": {"category_field": "modalidad"},                 "display": "bar"},
            {"name": "Delitos por día",            "mongo": "mv_er_clasi_hechos", "fn": "bar_day"},
            {"name": "Delitos por mes y clasificación", "mongo": "mv_er_clasi_hechos", "fn": "stacked_month", "args": {"category_field": "clasificacion_delito"}, "display": "area"},
        ],
        "tables": [
            {"name":   "Tabla de delitos",
             "mongo":  "mv_er_clasi_hechos",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "nombre_delito",
                        "nombre_subdelito", "clasificacion_delito", "modalidad", "hubo_violencia"]},
        ],
        "map": {"name": "Mapa de delitos", "mongo": "mv_ubicacion"},
    },

    # 4. FALTAS ADMINISTRATIVAS ───────────────────────────────────────────────
    # mv_er_faltas_admin NO tiene 'turno'. Chart removido.
    {
        "collection": "03 Faltas Administrativas",
        "name":       "Dashboard Faltas Administrativas",
        "description": "Faltas administrativas: clasificación, fracción, distritos.",
        "kpis": [
            {"name": "Total Faltas",              "mongo": "mv_er_faltas_admin",         "fn": "count"},
            {"name": "Detenidos por Faltas",      "mongo": "mv_reporte_detenidos_faltas","fn": "count"},
            {"name": "Eventos únicos",            "mongo": "mv_er_faltas_admin", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con faltas",      "mongo": "mv_er_faltas_admin", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Faltas por distrito",       "mongo": "mv_er_faltas_admin", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Faltas por clasificación",  "mongo": "mv_er_faltas_admin", "fn": "bar_cat", "args": {"category_field": "clasificacion"}},
            {"name": "Faltas por fracción",       "mongo": "mv_er_faltas_admin", "fn": "bar_cat", "args": {"category_field": "fraccion", "limit": 20}, "display": "row"},
            {"name": "Faltas por colonia",        "mongo": "mv_er_faltas_admin", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Faltas por día",            "mongo": "mv_er_faltas_admin", "fn": "bar_day"},
            {"name": "Faltas por mes y clasificación", "mongo": "mv_er_faltas_admin", "fn": "stacked_month", "args": {"category_field": "clasificacion"}, "display": "area"},
        ],
        "tables": [
            {"name": "Detalle de faltas", "mongo": "mv_er_faltas_admin",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "clasificacion", "fraccion", "descripcion"]},
        ],
        "maps": [
            {"name": "Mapa de faltas", "mongo": "mv_ubicacion", "fn": "map_lookup", "args": {"target_collection": "mv_er_faltas_admin"}},
        ],
    },

    # 5. DETENIDOS ────────────────────────────────────────────────────────────
    # Campos verificados en mv_er_detenidos: nombre, edad, fecha_nacimiento, genero,
    # distrito, sector, colonia, domicilio, latitud, longitud, fecha_evento.
    # NO existen: fuero, presentado_ante, estado_origen, rango_edad (se calcula con $switch).
    {
        "collection": "04 Detenidos",
        "name":       "Dashboard Detenidos",
        "description": "Demografía y perfil de detenidos. KPIs, gráficas y mapa en una sola vista.",
        "kpis": [
            {"name": "Total Detenidos",           "mongo": "mv_er_detenidos", "fn": "count"},
            {"name": "Detenidos Hombres",         "mongo": "mv_er_detenidos", "fn": "count", "extra": {"genero": "MASCULINO"}},
            {"name": "Detenidos Mujeres",         "mongo": "mv_er_detenidos", "fn": "count", "extra": {"genero": "FEMENINO"}},
            {"name": "Edad Promedio",             "mongo": "mv_er_detenidos", "fn": "avg",   "args": {"field": "edad", "cast": "int"}},
            {"name": "Detenidos Menores",         "mongo": "mv_er_detenidos", "fn": "count", "extra": edad_between(0, 18)},
            {"name": "Detenidos Adultos Mayores", "mongo": "mv_er_detenidos", "fn": "count", "extra": edad_between(60, 121)},
        ],
        "charts": [
            {"name": "Detenidos por distrito",    "mongo": "mv_er_detenidos", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Detenidos por género",      "mongo": "mv_er_detenidos", "fn": "bar_cat", "args": {"category_field": "genero"},  "display": "pie"},
            {"name": "Detenidos por rango de edad","mongo":"mv_er_detenidos", "fn": "age_range"},
            {"name": "Top 15 colonias con más detenciones",
                                                  "mongo": "mv_er_detenidos", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Detenidos por día",         "mongo": "mv_er_detenidos", "fn": "bar_day", "display": "line"},
            {"name": "Detenidos por mes y género","mongo": "mv_er_detenidos", "fn": "stacked_month", "args": {"category_field": "genero"}, "display": "area"},
            {"name": "Pivote distrito × turno (mv_resumen_pi)",
                                                  "mongo": "mv_resumen_pi",   "fn": "heatmap_dist_turno", "display": "table",
              "viz": {"table.pivot": True, "table.pivot_column": "turno", "table.cell_column": "Total"}},
        ],
        "maps": [
            {"name": "Mapa de eventos con detenidos",
              "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_detenidos"}},
        ],
    },

    # 6. VÍCTIMAS ─────────────────────────────────────────────────────────────
    # Campos verificados en mv_er_victimas: nombre, edad, genero, distrito, colonia,
    # pais_origen, estado_origen, ciudad_origen, etnia, canalizacion,
    # atencion_legal, atencion_psicologica, atencion_medica.
    # NO existe: delito (no hay relación directa nombre_delito en esta vista).
    {
        "collection": "05 Víctimas",
        "name":       "Dashboard Víctimas",
        "description": "Perfil de víctimas, atención brindada y distribución geográfica.",
        "kpis": [
            {"name": "Total Víctimas",                "mongo": "mv_er_victimas", "fn": "count"},
            {"name": "Víctimas Hombres",              "mongo": "mv_er_victimas", "fn": "count", "extra": {"genero": "MASCULINO"}},
            {"name": "Víctimas Mujeres",              "mongo": "mv_er_victimas", "fn": "count", "extra": {"genero": "FEMENINO"}},
            {"name": "Víctimas Canalizadas",          "mongo": "mv_er_victimas", "fn": "count", "extra": {"canalizacion": "SI"}},
            {"name": "Víctimas con atención médica",  "mongo": "mv_er_victimas", "fn": "count", "extra": {"atencion_medica": {"$nin": [None, ""]}}},
            {"name": "Víctimas con atención legal",   "mongo": "mv_er_victimas", "fn": "count", "extra": {"atencion_legal":  {"$nin": [None, ""]}}},
            {"name": "Edad Promedio",                 "mongo": "mv_er_victimas", "fn": "avg",   "args": {"field": "edad", "cast": "int"}},
            {"name": "Víctimas Menores",              "mongo": "mv_er_victimas", "fn": "count", "extra": edad_between(0, 18)},
        ],
        "charts": [
            {"name": "Víctimas por distrito",         "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Víctimas por género",           "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "genero"}, "display": "pie"},
            {"name": "Víctimas por rango de edad",    "mongo": "mv_er_victimas", "fn": "age_range"},
            {"name": "Víctimas por canalización",     "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "canalizacion"}, "display": "pie"},
            {"name": "Top 15 colonias con víctimas",  "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Top 10 estados de origen",      "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "estado_origen", "limit": 10}, "display": "row"},
            {"name": "Top 10 hospitales / atención médica",
                                                      "mongo": "mv_er_victimas", "fn": "bar_cat", "args": {"category_field": "atencion_medica", "limit": 10}, "display": "row"},
            {"name": "Víctimas por día",              "mongo": "mv_er_victimas", "fn": "bar_day", "display": "line"},
            {"name": "Víctimas por mes y género",     "mongo": "mv_er_victimas", "fn": "stacked_month", "args": {"category_field": "genero"}, "display": "area"},
        ],
        "maps": [
            {"name": "Mapa de eventos con víctimas",
              "mongo": "mv_ubicacion", "fn": "map_lookup", "args": {"target_collection": "mv_er_victimas"}},
        ],
    },

    # 7. VEHÍCULOS ────────────────────────────────────────────────────────────
    {
        "collection": "06 Vehículos",
        "name":       "Dashboard Vehículos",
        "description": "Vehículos asegurados: marca, tipo, motivo de aseguramiento.",
        "kpis": [
            {"name": "Total Vehículos",           "mongo": "mv_er_vehiculos", "fn": "count"},
            {"name": "Eventos únicos",            "mongo": "mv_er_vehiculos", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con registros",   "mongo": "mv_er_vehiculos", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Vehículos por distrito",    "mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Vehículos por marca",       "mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "marca", "limit": 15}, "display": "row"},
            {"name": "Vehículos por tipo",        "mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "tipo"}},
            {"name": "Vehículos por color",       "mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "color"}, "display": "pie"},
            {"name": "Vehículos por motivo",      "mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "motivo_aseguramiento"}},
            {"name": "Vehículos por año (modelo)","mongo": "mv_er_vehiculos", "fn": "bar_cat", "args": {"category_field": "modelo", "limit": 20}},
            {"name": "Vehículos por día",         "mongo": "mv_er_vehiculos", "fn": "bar_day"},
            {"name": "Vehículos por mes y tipo",  "mongo": "mv_er_vehiculos", "fn": "stacked_month", "args": {"category_field": "tipo"}, "display": "area"},
        ],
        "map": {"name": "Mapa de vehículos", "mongo": "mv_ubicacion"},
        "tables": [
            {"name": "Detalle de vehículos", "mongo": "mv_er_vehiculos",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo", "marca", "modelo", "color", "placas", "motivo_aseguramiento"]},
        ],
    },

    # 8. ARMAS ────────────────────────────────────────────────────────────────
    {
        "collection": "07 Armas",
        "name":       "Dashboard Armas",
        "description": "Armas aseguradas: tipo, calibre, clasificación.",
        "kpis": [
            {"name": "Total Armas",               "mongo": "mv_er_armas", "fn": "count"},
            {"name": "Piezas totales",            "mongo": "mv_er_armas", "fn": "sum", "args": {"field": "cantidad_arma"}},
            {"name": "Eventos únicos",            "mongo": "mv_er_armas", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con registros",   "mongo": "mv_er_armas", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Armas por distrito",        "mongo": "mv_er_armas", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Armas por tipo_arma",       "mongo": "mv_er_armas", "fn": "bar_cat", "args": {"category_field": "tipo_arma"}},
            {"name": "Armas por nombre_arma",     "mongo": "mv_er_armas", "fn": "bar_cat", "args": {"category_field": "nombre_arma", "limit": 15}, "display": "row"},
            {"name": "Armas por calibre",         "mongo": "mv_er_armas", "fn": "bar_cat", "args": {"category_field": "calibre_arma", "limit": 15}, "display": "row"},
            {"name": "Armas por clasificación",   "mongo": "mv_er_armas", "fn": "bar_cat", "args": {"category_field": "clasificacion_arma"}, "display": "pie"},
            {"name": "Armas por día",             "mongo": "mv_er_armas", "fn": "bar_day"},
            {"name": "Armas por mes y clasificación", "mongo": "mv_er_armas", "fn": "stacked_month", "args": {"category_field": "clasificacion_arma"}, "display": "area"},
        ],
        "tables": [
            {"name": "Detalle de armas", "mongo": "mv_er_armas",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "clasificacion_arma", "tipo_arma", "nombre_arma", "calibre_arma", "cantidad_arma"]},
        ],
        "maps": [
            {"name": "Mapa de armas", "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_armas"}},
        ],
    },

    # 9. SUSTANCIAS ───────────────────────────────────────────────────────────
    {
        "collection": "08 Sustancias",
        "name":       "Dashboard Sustancias",
        "description": "Sustancias aseguradas y pesos.",
        "kpis": [
            {"name": "Registros de Sustancias",   "mongo": "mv_er_sustancias", "fn": "count"},
            {"name": "Cantidad Total",            "mongo": "mv_er_sustancias", "fn": "sum", "args": {"field": "cantidad_sustancia"}},
            {"name": "Gramos totales",            "mongo": "mv_er_sustancias", "fn": "sum", "args": {"field": "cantidad_gramos"}},
            {"name": "Kilogramos totales",        "mongo": "mv_er_sustancias", "fn": "sum", "args": {"field": "cantidad_kg"}},
            {"name": "Eventos únicos",            "mongo": "mv_er_sustancias", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con registros",   "mongo": "mv_er_sustancias", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Sustancias por distrito",   "mongo": "mv_er_sustancias", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Sustancias por tipo",       "mongo": "mv_er_sustancias", "fn": "bar_cat", "args": {"category_field": "tipo_sustancia"}},
            {"name": "Top tipos por gramos",      "mongo": "mv_er_sustancias", "fn": "top_by_sum",
             "args": {"category_field": "tipo_sustancia", "sum_field": "cantidad_gramos", "limit": 15}, "display": "row"},
            {"name": "Sustancias por unidad",     "mongo": "mv_er_sustancias", "fn": "bar_cat", "args": {"category_field": "unidad_medida"}, "display": "pie"},
            {"name": "Sustancias por día",        "mongo": "mv_er_sustancias", "fn": "bar_day"},
            {"name": "Sustancias por mes y tipo", "mongo": "mv_er_sustancias", "fn": "stacked_month", "args": {"category_field": "tipo_sustancia"}, "display": "area"},
        ],
        "tables": [
            {"name": "Detalle de sustancias", "mongo": "mv_er_sustancias",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo_sustancia", "unidad_medida", "cantidad_sustancia", "peso_en", "cantidad_gramos", "cantidad_kg"]},
        ],
        "maps": [
            {"name": "Mapa de sustancias", "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_sustancias"}},
        ],
    },

    # 10. OBJETOS ─────────────────────────────────────────────────────────────
    {
        "collection": "09 Objetos",
        "name":       "Dashboard Objetos",
        "description": "Objetos asegurados.",
        "kpis": [
            {"name": "Total Objetos",             "mongo": "mv_er_objetos", "fn": "count"},
            {"name": "Piezas totales",            "mongo": "mv_er_objetos", "fn": "sum", "args": {"field": "cantidad_objeto"}},
            {"name": "Eventos únicos",            "mongo": "mv_er_objetos", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con registros",   "mongo": "mv_er_objetos", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Objetos por tipo_objeto",   "mongo": "mv_er_objetos", "fn": "bar_cat", "args": {"category_field": "tipo_objeto"}},
            {"name": "Objetos por distrito",      "mongo": "mv_er_objetos", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Objetos por colonia",       "mongo": "mv_er_objetos", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Objetos por unidad_medida", "mongo": "mv_er_objetos", "fn": "bar_cat", "args": {"category_field": "unidad_medida"}, "display": "pie"},
            {"name": "Objetos por día",           "mongo": "mv_er_objetos", "fn": "bar_day"},
            {"name": "Objetos por mes y tipo",    "mongo": "mv_er_objetos", "fn": "stacked_month", "args": {"category_field": "tipo_objeto"}, "display": "area"},
        ],
        "tables": [
            {"name": "Detalle de objetos", "mongo": "mv_er_objetos",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo_objeto", "especifique_objeto", "cantidad_objeto", "unidad_medida"]},
        ],
        "maps": [
            {"name": "Mapa de objetos", "mongo": "mv_ubicacion", "fn": "map_lookup", "args": {"target_collection": "mv_er_objetos"}},
        ],
    },

    # 11. AGENTES ─────────────────────────────────────────────────────────────
    # Campos verificados en mv_er_agentes: nombre, apellido_paterno, apellido_materno,
    # numero_empleado, distrito, distrito_agente, turno, puesto, fecha_evento.
    # NO existen: nombre_agente (compuesto), unidad.
    # Anonimización: el "Top agentes" agrupa por numero_empleado (identificador interno),
    # NO por nombre, para no exponer PII en la vista pública.
    {
        "collection": "10 Agentes",
        "name":       "Dashboard Agentes",
        "description": "Participaciones de agentes (anonimizadas por número de empleado).",
        "kpis": [
            {"name": "Total Participaciones",         "mongo": "mv_er_agentes", "fn": "count"},
            {"name": "Agentes únicos",                "mongo": "mv_er_agentes", "fn": "distinct_count", "args": {"field": "numero_empleado"}},
            {"name": "Distritos con participación",   "mongo": "mv_er_agentes", "fn": "distinct_count", "args": {"field": "distrito"}},
            {"name": "Eventos atendidos",             "mongo": "mv_er_agentes", "fn": "distinct_count", "args": {"field": "folio"}},
        ],
        "charts": [
            {"name": "Participaciones por puesto",    "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "puesto"}, "display": "pie"},
            {"name": "Participaciones por distrito",  "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Participaciones por turno",     "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "turno"},   "display": "pie"},
            {"name": "Distrito de adscripción del agente",
                                                      "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "distrito_agente"}},
            {"name": "Top 20 agentes (por número de empleado)",
                                                      "mongo": "mv_er_agentes", "fn": "bar_cat", "args": {"category_field": "numero_empleado", "limit": 20}, "display": "row"},
            {"name": "Participaciones por día",       "mongo": "mv_er_agentes", "fn": "bar_day", "display": "line"},
            {"name": "Participaciones por mes y turno",
                                                      "mongo": "mv_er_agentes", "fn": "stacked_month", "args": {"category_field": "turno"}, "display": "area"},
            {"name": "Pivote distrito × turno",       "mongo": "mv_er_agentes", "fn": "heatmap_dist_turno", "display": "table",
              "viz": {"table.pivot": True, "table.pivot_column": "turno", "table.cell_column": "Total"}},
        ],
    },

    # 12. EMERGENCIAS ─────────────────────────────────────────────────────────
    {
        "collection": "11 Emergencias",
        "name":       "Dashboard Emergencias",
        "description": "Emergencias: tipo, clasificación, distribución.",
        # mv_er_emergencias NO tiene 'turno'. Chart removido.
        "kpis": [
            {"name": "Total Emergencias",         "mongo": "mv_er_emergencias", "fn": "count"},
            {"name": "Eventos únicos",            "mongo": "mv_er_emergencias", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con emergencias", "mongo": "mv_er_emergencias", "fn": "distinct_count", "args": {"field": "distrito"}},
        ],
        "charts": [
            {"name": "Emergencias por tipo",      "mongo": "mv_er_emergencias", "fn": "bar_cat", "args": {"category_field": "tipo"}},
            {"name": "Emergencias por clasif.",   "mongo": "mv_er_emergencias", "fn": "bar_cat", "args": {"category_field": "clasificacion"}},
            {"name": "Emergencias por distrito",  "mongo": "mv_er_emergencias", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Emergencias por colonia",   "mongo": "mv_er_emergencias", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Emergencias por día",       "mongo": "mv_er_emergencias", "fn": "bar_day"},
            {"name": "Emergencias por mes y tipo","mongo": "mv_er_emergencias", "fn": "stacked_month", "args": {"category_field": "tipo"}, "display": "area"},
        ],
        "tables": [
            {"name": "Detalle de emergencias", "mongo": "mv_er_emergencias",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo", "clasificacion", "especifique_subtipo", "descripcion"]},
        ],
        "maps": [
            {"name": "Mapa de emergencias", "mongo": "mv_ubicacion", "fn": "map_lookup", "args": {"target_collection": "mv_er_emergencias"}},
        ],
    },

    # 13. GEOESPACIAL ─────────────────────────────────────────────────────────
    {
        "collection": "12 Geoespacial",
        "name":       "Dashboard Geoespacial",
        "description": "Mapas y concentración geográfica de eventos.",
        "kpis": [
            {"name": "Eventos georreferenciados", "mongo": "mv_ubicacion", "fn": "count"},
            {"name": "Eventos únicos",            "mongo": "mv_ubicacion", "fn": "distinct_count", "args": {"field": "folio"}},
            {"name": "Distritos con eventos",     "mongo": "mv_ubicacion", "fn": "distinct_count", "args": {"field": "distrito"}},
            {"name": "Colonias con eventos",      "mongo": "mv_ubicacion", "fn": "distinct_count", "args": {"field": "colonia"}},
        ],
        "charts": [
            {"name": "Concentración por distrito","mongo": "mv_ubicacion", "fn": "bar_cat", "args": {"category_field": "distrito"}},
            {"name": "Concentración por colonia", "mongo": "mv_ubicacion", "fn": "bar_cat", "args": {"category_field": "colonia", "limit": 15}, "display": "row"},
            {"name": "Concentración por turno",   "mongo": "mv_ubicacion", "fn": "bar_cat", "args": {"category_field": "turno"}, "display": "pie"},
            {"name": "Top motivos de intervención","mongo": "mv_ubicacion", "fn": "bar_cat", "args": {"category_field": "motivo_intervencion", "limit": 15}, "display": "bar"},
            {"name": "Heatmap distrito × turno",  "mongo": "mv_ubicacion", "fn": "heatmap_dist_turno", "display": "table"},
            {"name": "Eventos por mes y motivo",  "mongo": "mv_ubicacion", "fn": "stacked_month", "args": {"category_field": "motivo_intervencion"}, "display": "area"},
        ],
        "maps": [
            {"name": "Mapa general de eventos",   "mongo": "mv_ubicacion", "fn": "map"},
            {"name": "Mapa de detenidos",         "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_detenidos"}},
            {"name": "Mapa de armas",             "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_armas"}},
            {"name": "Mapa de sustancias",        "mongo": "mv_ubicacion", "fn": "map", "args": {"flag_field": "cantidad_sustancias"}},
        ],
    },

    # 14. HOMICIDIO ───────────────────────────────────────────────────────────
    # Fuente: mv_er_clasi_hechos filtrado por nombre_delito ~ HOMICIDIO.
    # mv_er_clasi_hechos sí tiene fecha_evento — el filtro de período funciona normalmente.
    # turno no verificado en esta vista; si no existe el heatmap devolverá resultados
    # sin segmentar — es seguro dejarlo, Metabase muestra la columna vacía.
    {
        "collection": "14 Homicidio",
        "name":       "Dashboard Homicidio",
        "description": "Análisis de homicidios: clasificación, modalidad, distribución geográfica y temporal.",
        "kpis": [
            {"name": "Total Homicidios",
             "mongo": "mv_er_clasi_hechos", "fn": "count",
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}}},
            {"name": "Homicidios con Violencia",
             "mongo": "mv_er_clasi_hechos", "fn": "count",
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}, "hubo_violencia": "SI"}},
            {"name": "Homicidios sin Violencia",
             "mongo": "mv_er_clasi_hechos", "fn": "count",
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}, "hubo_violencia": "NO"}},
            {"name": "Eventos Únicos con Homicidio",
             "mongo": "mv_er_clasi_hechos", "fn": "distinct_count",
             "args": {"field": "folio"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}}},
            {"name": "Distritos con Homicidios",
             "mongo": "mv_er_clasi_hechos", "fn": "distinct_count",
             "args": {"field": "distrito"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}}},
            {"name": "Colonias con Homicidios",
             "mongo": "mv_er_clasi_hechos", "fn": "distinct_count",
             "args": {"field": "colonia"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}}},
        ],
        "charts": [
            {"name": "Homicidios por distrito",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat",
             "args": {"category_field": "distrito"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "bar"},
            {"name": "Homicidios por subdelito",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat",
             "args": {"category_field": "nombre_subdelito", "limit": 15},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "row"},
            {"name": "Homicidios por modalidad",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat",
             "args": {"category_field": "modalidad"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "pie"},
            {"name": "Homicidios con/sin violencia",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat",
             "args": {"category_field": "hubo_violencia"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "pie"},
            {"name": "Top 10 colonias con homicidios",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_cat",
             "args": {"category_field": "colonia", "limit": 10},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "row"},
            {"name": "Homicidios por día",
             "mongo": "mv_er_clasi_hechos", "fn": "bar_day",
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "line"},
            {"name": "Homicidios por mes y clasificación",
             "mongo": "mv_er_clasi_hechos", "fn": "stacked_month",
             "args": {"category_field": "clasificacion_delito"},
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "area"},
            {"name": "Heatmap homicidios distrito × turno",
             "mongo": "mv_er_clasi_hechos", "fn": "heatmap_dist_turno",
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}},
             "display": "table",
             "viz": {"table.pivot": True, "table.pivot_column": "turno", "table.cell_column": "Total"}},
        ],
        "tables": [
            {"name":   "Tabla detalle Homicidios",
             "mongo":  "mv_er_clasi_hechos",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "nombre_delito",
                        "nombre_subdelito", "clasificacion_delito", "modalidad", "hubo_violencia"],
             "extra": {"nombre_delito": {"$regex": "HOMICIDIO", "$options": "i"}}},
        ],
        "maps": [
            {"name": "Mapa de Homicidios",
             "mongo": "mv_ubicacion", "fn": "map_lookup",
             "args": {"target_collection": "mv_er_clasi_hechos"}},
        ],
    },

    # 15. ÓRDENES DE APREHENSIÓN ──────────────────────────────────────────────
    # mv_puestas_ordenes_vehiculos: pre-agregado por día/distrito, fechas corruptas → _nodate.
    # mv_armasyordenesreporte: registros individuales con fechas corruptas → _nodate.
    {
        "collection": "15 Órdenes de Aprehensión",
        "name":       "Dashboard Órdenes de Aprehensión",
        "description": "Puestas a disposición, órdenes de aprehensión y vehículos asociados.",
        "kpis": [
            {"name": "Total Órdenes de Aprehensión",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "sum_nodate",
             "args": {"field": "ordenes"}},
            {"name": "Total Puestas a Disposición",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "sum_nodate",
             "args": {"field": "puestas"}},
            {"name": "Total Vehículos en Órdenes",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "sum_nodate",
             "args": {"field": "vehiculos"}},
            {"name": "Registros de Armas y Órdenes",
             "mongo": "mv_armasyordenesreporte", "fn": "count_nodate"},
            {"name": "Registros de Puestas y Órdenes",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "count_nodate"},
        ],
        "charts": [
            {"name": "Órdenes por distrito",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "top_by_sum_nodate",
             "args": {"category_field": "distrito", "sum_field": "ordenes"},
             "display": "bar"},
            {"name": "Puestas a disposición por distrito",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "top_by_sum_nodate",
             "args": {"category_field": "distrito", "sum_field": "puestas"},
             "display": "bar"},
            {"name": "Vehículos en órdenes por distrito",
             "mongo": "mv_puestas_ordenes_vehiculos", "fn": "top_by_sum_nodate",
             "args": {"category_field": "distrito", "sum_field": "vehiculos"},
             "display": "bar"},
            {"name": "Armas y Órdenes por distrito",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "distrito"},
             "display": "bar"},
            {"name": "Armas y Órdenes por tipo de arma",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "TIPO_ARMA1", "limit": 15},
             "display": "row"},
            {"name": "Armas y Órdenes por clasificación",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "CLASIFICACION_ARMA1"},
             "display": "bar"},
            {"name": "Armas y Órdenes por turno",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "turno"},
             "display": "pie"},
            {"name": "Top 15 nombres de arma en órdenes",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "NOMBRE_ARMA1", "limit": 15},
             "display": "row"},
            {"name": "Armas y Órdenes por colonia",
             "mongo": "mv_armasyordenesreporte", "fn": "bar_cat_nodate",
             "args": {"category_field": "colonia", "limit": 15},
             "display": "row"},
        ],
        "tables": [
            {"name": "Puestas, Órdenes y Vehículos por día",
             "mongo": "mv_puestas_ordenes_vehiculos",
             "fields": ["distrito", "fecha", "ano", "mes", "dia", "puestas", "ordenes", "vehiculos"],
             "date_field": None},
            {"name": "Detalle Armas y Órdenes",
             "mongo": "mv_armasyordenesreporte",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "turno",
                        "TIPO_ARMA1", "CLASIFICACION_ARMA1", "NOMBRE_ARMA1", "CALIBRE_ARMA1", "CANTIDAD_ARMA1"],
             "date_field": None},
        ],
    },

    # 16. MENORES INFRACTORES ─────────────────────────────────────────────────
    # Fuente: mv_menores_delitos. date_field = "fecha_detencion" (no "fecha_evento").
    # edad es string — se usa cast="int" igual que en detenidos/víctimas.
    {
        "collection": "16 Menores",
        "name":       "Dashboard Menores Infractores",
        "description": "Menores detenidos: perfil demográfico, delitos, situación jurídica y distribución.",
        "kpis": [
            {"name": "Total Menores Detenidos",
             "mongo": "mv_menores_delitos", "fn": "count",
             "args": {"date_field": "fecha_detencion"}},
            {"name": "Menores Hombres",
             "mongo": "mv_menores_delitos", "fn": "count",
             "args": {"date_field": "fecha_detencion"}, "extra": {"sexo": "MASCULINO"}},
            {"name": "Menores Mujeres",
             "mongo": "mv_menores_delitos", "fn": "count",
             "args": {"date_field": "fecha_detencion"}, "extra": {"sexo": "FEMENINO"}},
            {"name": "Edad Promedio",
             "mongo": "mv_menores_delitos", "fn": "avg",
             "args": {"field": "edad", "cast": "int", "date_field": "fecha_detencion"}},
            {"name": "Eventos Únicos",
             "mongo": "mv_menores_delitos", "fn": "distinct_count",
             "args": {"field": "folio", "date_field": "fecha_detencion"}},
            {"name": "Distritos con Menores Detenidos",
             "mongo": "mv_menores_delitos", "fn": "distinct_count",
             "args": {"field": "distrito", "date_field": "fecha_detencion"}},
        ],
        "charts": [
            {"name": "Menores por distrito",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "distrito", "date_field": "fecha_detencion"},
             "display": "bar"},
            {"name": "Menores por sexo",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "sexo", "date_field": "fecha_detencion"},
             "display": "pie"},
            {"name": "Menores por falta o delito",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "falta_delito", "date_field": "fecha_detencion"},
             "display": "pie"},
            {"name": "Menores por clasificación de delito",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "clasificacion_delito", "date_field": "fecha_detencion"},
             "display": "bar"},
            {"name": "Menores por situación jurídica",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "situacion_juridica", "date_field": "fecha_detencion"},
             "display": "bar"},
            {"name": "Menores por presentado ante",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "presentado_ante", "date_field": "fecha_detencion"},
             "display": "bar"},
            {"name": "Top 15 colonias con menores detenidos",
             "mongo": "mv_menores_delitos", "fn": "bar_cat",
             "args": {"category_field": "colonia", "limit": 15, "date_field": "fecha_detencion"},
             "display": "row"},
            {"name": "Menores por rango de edad",
             "mongo": "mv_menores_delitos", "fn": "age_range",
             "args": {"date_field": "fecha_detencion", "edad_field": "edad"}},
            {"name": "Menores por día",
             "mongo": "mv_menores_delitos", "fn": "bar_day",
             "args": {"date_field": "fecha_detencion"},
             "display": "line"},
            {"name": "Menores por mes y clasificación de delito",
             "mongo": "mv_menores_delitos", "fn": "stacked_month",
             "args": {"category_field": "clasificacion_delito", "date_field": "fecha_detencion"},
             "display": "area"},
            {"name": "Menores por mes y sexo",
             "mongo": "mv_menores_delitos", "fn": "stacked_month",
             "args": {"category_field": "sexo", "date_field": "fecha_detencion"},
             "display": "area"},
        ],
        "tables": [
            {"name": "Tabla Menores Detenidos",
             "mongo": "mv_menores_delitos",
             "fields": ["folio", "fecha_detencion", "distrito", "colonia", "edad", "sexo",
                        "falta_delito", "clasificacion_delito", "situacion_juridica", "presentado_ante"],
             "date_field": "fecha_detencion"},
        ],
        "maps": [
            {"name": "Mapa de Menores Detenidos",
             "mongo": "mv_ubicacion", "fn": "map_lookup",
             "args": {"target_collection": "mv_menores_delitos"}},
        ],
    },

    # 17. REPORTES OFICIALES ──────────────────────────────────────────────────
    # Campos verificados por sampleo (2026-04). Varias vistas tienen fechas
    # corruptas (años 0002/1976/0202) o columnas pre-aggregadas — para esas
    # ponemos date_field=None para saltar el filtro de período.
    {
        "collection": "13 Reportes Oficiales",
        "name":       "Dashboard Reportes Oficiales",
        "description": "Tablas oficiales para exportación CSV/XLSX.",
        "kpis": [],
        "charts": [],
        "tables": [
            {"name": "Reporte Detenidos + Faltas", "mongo": "mv_reporte_detenidos_faltas",
             "fields": ["folio", "fecha_evento", "distrito", "barandilla", "colonia", "turno",
                        "motivo_intervencion", "nombre_responsable", "cantidad_detenidos", "cantidad_faltas", "estatus"]},
            {"name": "Excel Faltas Informativas", "mongo": "mv_excel_faltas_informativas",
             "fields": ["FOLIO", "folio_pi", "FECHA", "BARANDILLA", "DISTRITO", "TIPO_DE_FALTA_ADMIN",
                        "COLONIA", "NOMBRE_DEL_DETENIDO", "SEXO", "EDAD", "NACIONALIDAD"],
             "date_field": None},
            {"name": "Puestas, Órdenes y Vehículos", "mongo": "mv_puestas_ordenes_vehiculos",
             "fields": ["distrito", "fecha", "ano", "mes", "dia", "puestas", "ordenes", "vehiculos"],
             "date_field": None},
            {"name": "Departamento de Estadísticas", "mongo": "vista_departamento_estadisticas",
             "fields": ["NO_REMISION", "FECHA", "HORA", "DISTRITO_DE_EVENTO", "CUADRANTE",
                        "DELITO_PRIMARIO", "DELITO_SECUNDARIO", "ARMA_CORTA", "ARMA_LARGA",
                        "COCAINA", "CRISTAL", "MARIHUANA_ENV", "FGE_DETENIDOS"],
             "date_field": None},
            {"name": "Armas y Órdenes", "mongo": "mv_armasyordenesreporte",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "turno",
                        "TIPO_ARMA1", "CLASIFICACION_ARMA1", "NOMBRE_ARMA1", "CALIBRE_ARMA1", "CANTIDAD_ARMA1"],
             "date_field": None},
            {"name": "Vehículos General", "mongo": "mv_reporte_vehiculos_general",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo_vehiculo", "marca",
                        "submarca", "modelo", "placas", "color", "motivo_aseguramiento"],
             "date_field": None},
            {"name": "Bitácora de Armas", "mongo": "mv_bitacora_armas",
             "fields": ["folio", "fecha_evento", "distrito", "colonia", "tipo_arma", "clasificacion_arma",
                        "nombre_arma", "calibre_arma", "cantidad_arma", "posesion_portacion"],
             "date_field": None},
            {"name": "Menores Delitos", "mongo": "mv_menores_delitos",
             "fields": ["folio", "fecha_detencion", "distrito", "colonia", "edad", "sexo",
                        "falta_delito", "clasificacion_delito", "situacion_juridica", "presentado_ante"],
             "date_field": "fecha_detencion"},
        ],
    },
]


# ───────────────────────────────────────────────────────────────────────────────
# DISPATCH de query_fn
# ───────────────────────────────────────────────────────────────────────────────

def build_query(spec: dict) -> str:
    fn    = spec["fn"]
    args  = dict(spec.get("args", {}))   # copia para no mutar el config global
    extra = spec.get("extra")
    # date_field puede venir en args para vistas con campo de fecha no estándar
    date_field = args.pop("date_field", "fecha_evento")

    if fn == "count":
        return q_kpi_count(date_field=date_field, extra_match=extra)
    if fn == "sum":
        return q_kpi_sum(date_field=date_field, extra_match=extra, **args)
    if fn == "avg":
        return q_avg(date_field=date_field, extra_match=extra, **args)
    if fn == "distinct_count":
        return q_distinct_count(date_field=date_field, extra_match=extra, **args)
    if fn == "bar_day":
        return q_bar_by_day(date_field=date_field, extra_match=extra)
    if fn == "bar_cat":
        return q_bar_by_category(date_field=date_field, extra_match=extra, **args)
    if fn == "top_by_sum":
        return q_top_by_sum(date_field=date_field, extra_match=extra, **args)
    if fn == "age_range":
        return q_age_range(date_field=date_field, extra_match=extra, **args)
    if fn == "heatmap_dist_turno":
        return q_heatmap_distrito_turno(date_field=date_field, extra_match=extra)
    if fn == "stacked_month":
        return q_stacked_by_month(date_field=date_field, extra_match=extra, **args)
    if fn == "table":
        return q_table(date_field=date_field, **args)
    if fn == "map":
        return q_map(**args)
    if fn == "map_lookup":
        return q_map_via_lookup(**args)
    # fns sin filtro de fecha (vistas con fechas corruptas o pre-agregadas)
    if fn == "count_nodate":
        return q_kpi_count_nodate(extra_match=extra)
    if fn == "sum_nodate":
        return q_kpi_sum_nodate(extra_match=extra, **args)
    if fn == "bar_cat_nodate":
        return q_bar_by_category_nodate(extra_match=extra, **args)
    if fn == "top_by_sum_nodate":
        return q_top_by_sum_nodate(extra_match=extra, **args)
    raise ValueError(f"query_fn desconocido: {fn}")


# ───────────────────────────────────────────────────────────────────────────────
# ORQUESTACIÓN
# ───────────────────────────────────────────────────────────────────────────────

def setup_database() -> int:
    log.info(f"[1/4] Buscando database: {MONGO_DB_NAME}")
    db = find_database(MONGO_DB_NAME)
    if not db:
        raise RuntimeError(
            f"No se encontró la database '{MONGO_DB_NAME}'. "
            f"Crearla manualmente desde Admin → Databases o agregar credenciales aquí."
        )
    log.info(f"  database id={db['id']}, engine={db.get('engine')}")
    return db["id"]


def archive_collection_contents(collection_id: int) -> None:
    """Archiva todos los dashboards y cards activos en una collection.
    Es reversible (los items quedan en /admin/archive)."""
    res = api_get(f"/collection/{collection_id}/items?models=dashboard&models=card",
                  default_on_404={"data": []})
    items = res.get("data", []) if isinstance(res, dict) else res
    for it in items:
        model = it.get("model")
        iid   = it.get("id")
        if not iid or model not in ("dashboard", "card"):
            continue
        try:
            api_put(f"/{model}/{iid}", {"archived": True})
            log.info(f"  archivado:  {model:9s} id={iid}  {it.get('name')!r}")
        except Exception as e:
            log.warning(f"  no se pudo archivar {model} {iid}: {e}")


def setup_collections(dash_list: list[dict]) -> dict[str, int]:
    log.info(f"[2/4] Collections (parent: {COLLECTION_PARENT})")
    parent_id = get_or_create_collection(COLLECTION_PARENT, parent_id=None)
    sub_ids: dict[str, int] = {}
    for d in dash_list:
        sub_ids[d["collection"]] = get_or_create_collection(d["collection"], parent_id=parent_id)
    return sub_ids


def build_dashboard(db_id: int, dash_def: dict, collection_id: int) -> int:
    log.info(f"\n[3/4] Dashboard: {dash_def['name']}  (collection: {dash_def['collection']})")

    dash_id = get_or_create_dashboard(
        dash_def["name"], collection_id, dash_def.get("description", "")
    )

    kpi_ids: list[int]   = []
    chart_ids: list[int] = []
    table_ids: list[int] = []
    map_ids: list[int]   = []

    for spec in dash_def.get("kpis", []):
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=spec["name"], mongo_collection=spec["mongo"],
            query_str=build_query(spec), display="scalar",
        )
        kpi_ids.append(cid)

    for spec in dash_def.get("charts", []):
        display = spec.get("display", "bar")
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=spec["name"], mongo_collection=spec["mongo"],
            query_str=build_query(spec), display=display,
            viz=spec.get("viz", {}),
        )
        chart_ids.append(cid)

    if "table" in dash_def:
        t = dash_def["table"]
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=t["name"], mongo_collection=t["mongo"],
            query_str=q_table(t["fields"], date_field=t.get("date_field", "fecha_evento")), display="table",
        )
        table_ids.append(cid)

    for t in dash_def.get("tables", []):
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=t["name"], mongo_collection=t["mongo"],
            query_str=q_table(t["fields"],
                              date_field=t.get("date_field", "fecha_evento"),
                              extra_match=t.get("extra")),
            display="table",
        )
        table_ids.append(cid)

    for m in dash_def.get("maps", []):
        viz = {"map.type": "pin", "map.latitude_column": "latitud", "map.longitude_column": "longitud"}
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=m["name"], mongo_collection=m["mongo"],
            query_str=build_query(m), display="map", viz=viz,
        )
        map_ids.append(cid)

    if "map" in dash_def:
        m = dash_def["map"]
        viz = {"map.type": "pin", "map.latitude_column": "latitud", "map.longitude_column": "longitud"}
        cid = create_card(
            db_id=db_id, collection_id=collection_id,
            name=m["name"], mongo_collection=m["mongo"],
            query_str=q_map(), display="map", viz=viz,
        )
        map_ids.append(cid)

    push_dashboard_layout(
        dash_id,
        kpi_card_ids=kpi_ids,
        chart_card_ids=chart_ids,
        table_card_ids=table_ids,
        map_card_ids=map_ids,
    )
    return dash_id


def main():
    parser = argparse.ArgumentParser(description="Setup Metabase dashboards SSPM_dashboard")
    parser.add_argument("--only", action="append", default=[],
                        help="Procesar solo dashboards cuya collection contenga este texto. Puede repetirse.")
    parser.add_argument("--rebuild", action="store_true",
                        help="Archivar dashboards/cards previos en las collections seleccionadas antes de recrear.")
    args = parser.parse_args()

    log.info("=" * 70)
    log.info(f"SSPM_dashboard setup     DRY_RUN={DRY_RUN}     base={API_BASE}")
    log.info("=" * 70)

    db_id = setup_database()

    selected = DASHBOARDS
    if args.only:
        terms = [t.lower() for t in args.only]
        selected = [d for d in DASHBOARDS
                    if any(t in d["collection"].lower() for t in terms)]
        if not selected:
            log.error(f"--only {args.only} no coincide con ninguna collection")
            sys.exit(1)
        log.info(f"Filtro --only: {[d['collection'] for d in selected]}")

    col_ids = setup_collections(selected)

    if args.rebuild:
        log.info("\n[2.5] --rebuild activo: archivando contenidos previos de las collections")
        for d in selected:
            cid = col_ids[d["collection"]]
            log.info(f"  collection: {d['collection']} (id={cid})")
            archive_collection_contents(cid)

    summary: list[tuple[str, int]] = []
    for d in selected:
        try:
            dash_id = build_dashboard(db_id, d, col_ids[d["collection"]])
            summary.append((d["name"], dash_id))
        except Exception as e:
            log.error(f"  ❌ Falló {d['name']}: {e}")
            summary.append((d["name"], -1))

    log.info("\n[4/4] Resumen:")
    for name, did in summary:
        mark = "✅" if did > 0 else "❌"
        log.info(f"  {mark} {name:55s} dashboard_id={did}")

    if DRY_RUN:
        log.info("\n⚠️  DRY_RUN=true — nada se escribió en Metabase. "
                 "Para ejecutar de verdad: DRY_RUN=false python3 sspm_dashboard_setup.py")


if __name__ == "__main__":
    main()
