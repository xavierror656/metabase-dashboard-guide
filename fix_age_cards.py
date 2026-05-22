#!/usr/bin/env python3
"""
Patch puntual: corrige las 7 cards de Detenidos/Víctimas que fallan porque
`edad` está guardada como string en MongoDB (no como int).

  - 484  Detenidos · Edad Promedio        →  q_avg(field='edad', cast='int')
  - 485  Detenidos · Detenidos Menores    →  edad_between(0, 18)
  - 486  Detenidos · Adultos Mayores      →  edad_between(60, 121)
  - 489  Detenidos · Por rango de edad    →  q_age_range
  - 501  Víctimas  · Edad Promedio        →  q_avg(field='edad', cast='int')
  - 502  Víctimas  · Víctimas Menores     →  edad_between(0, 18)
  - 505  Víctimas  · Por rango de edad    →  q_age_range

Hace PUT /api/card/{id} con la query nueva. No archiva, no recrea, no toca otras cards.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sspm_dashboard_setup import (
    api_get, api_put,
    q_age_range, q_avg, q_kpi_count,
    edad_between,
    _wrap_match_with_optional_filters, OPTIONAL_FILTER_FIELDS,
)

PATCHES = [
    (484, lambda: q_avg(field="edad", cast="int")),
    (485, lambda: q_kpi_count(extra_match=edad_between(0, 18))),
    (486, lambda: q_kpi_count(extra_match=edad_between(60, 121))),
    (489, lambda: q_age_range()),
    (501, lambda: q_avg(field="edad", cast="int")),
    (502, lambda: q_kpi_count(extra_match=edad_between(0, 18))),
    (505, lambda: q_age_range()),
]


def patch_card(card_id: int, new_query_str: str) -> None:
    card = api_get(f"/card/{card_id}")
    s0   = card["dataset_query"]["stages"][0]
    s0["native"] = _wrap_match_with_optional_filters(new_query_str, OPTIONAL_FILTER_FIELDS)
    api_put(f"/card/{card_id}", {
        "dataset_query":          card["dataset_query"],
        "name":                   card["name"],
        "display":                card.get("display", "scalar"),
        "visualization_settings": card.get("visualization_settings", {}),
        "collection_id":          card.get("collection_id"),
    })
    print(f"  ✅ {card_id}  {card['name']}")


def main():
    print("Aplicando patches a 7 cards (edad string → int)…")
    for cid, fn in PATCHES:
        try:
            patch_card(cid, fn())
        except Exception as e:
            print(f"  ❌ {cid}: {e}")
    print("Listo.")


if __name__ == "__main__":
    main()
