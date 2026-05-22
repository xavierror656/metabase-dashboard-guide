#!/usr/bin/env python3
"""Sample one document per view to verify available fields."""
from sspm_dashboard_setup import _request

VIEWS = [
    "mv_resumen_pi",
    "mv_operativa",
    "mv_er_agentes",
    "mv_er_clasi_hechos",
    "mv_er_faltas_admin",
    "mv_er_emergencias",
    "mv_reporte_detenidos_faltas",
    "mv_excel_faltas_informativas",
    "mv_puestas_ordenes_vehiculos",
    "vista_departamento_estadisticas",
    "mv_armasyordenesreporte",
    "mv_reporte_vehiculos_general",
    "mv_bitacora_armas",
    "mv_menores_delitos",
]
DB_ID = 3

for view in VIEWS:
    print(f"\n=== {view} ===")
    body = {
        "type": "native",
        "native": {"collection": view, "query": '[{"$limit": 1}]'},
        "database": DB_ID,
    }
    try:
        r = _request("POST", "/dataset", body)
        cols = [c["name"] for c in r.get("data", {}).get("cols", [])]
        rows = r.get("data", {}).get("rows", [])
        print(f"  campos ({len(cols)}): {cols}")
        if rows:
            sample = dict(zip(cols, rows[0]))
            for k, v in sample.items():
                vs = str(v)[:70]
                print(f"    {k:32s} = {vs}")
    except Exception as e:
        print(f"  ERROR: {str(e)[:200]}")
