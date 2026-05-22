# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Python tooling that manages **Metabase** dashboards via the REST API for the **SSPM_dashboard** police-information project. The data layer is **MongoDB** (`Vistas_e` database, ~25 materialized views named `mv_*`). The repo is **not** the ETL — it consumes views materialized elsewhere from `SSPM_dashboard.ParteInformativa`.

```
Laravel/Mongo → ETL (external) → Vistas_e.mv_*  ←  these scripts ← Metabase
```

Reference docs (read these before changing query/dashboard code):
- `metabase-dashboard-guide.md` — battle-tested patterns, gotchas, and the rationale behind them
- `dashboardproyect.md` — original project spec; **outdated** in places (lists fields that don't exist in the views — always verify schema first)
- `informe_dashboard17.md` / `informe_dashboard21.md` — dashboard-specific notes

## Common commands

The orchestrator is `sspm_dashboard_setup.py`. **It defaults to `DRY_RUN=true`** (set in `.env`) and only mutates Metabase when explicitly overridden.

```bash
# preview everything (no writes)
DRY_RUN=true python3 sspm_dashboard_setup.py

# preview a subset (matches collection name substring)
DRY_RUN=true python3 sspm_dashboard_setup.py --only "Detenidos" --only "Víctimas"

# execute against Metabase
DRY_RUN=false python3 sspm_dashboard_setup.py --only "Detenidos"

# nuke-and-rebuild: archives existing dashboards/cards in the target collections, then recreates fresh
DRY_RUN=false python3 sspm_dashboard_setup.py --only "Detenidos" --rebuild

# patch one or more cards in place (no archive, surgical PUT to /api/card/{id})
DRY_RUN=false python3 fix_age_cards.py
```

Single-script utilities (one-shot operations against specific dashboards):
- `add_distrito_sector_filters.py` — adds optional `distrito`/`sector` filters to dashboards 17, 21, 23
- `add_graficas_tab_d21.py`, `add_graficas_tab_d23.py` — adds a "Gráficas" tab to dashboards 21, 23

There is no test suite. Validate Python with `python3 -c "import ast; ast.parse(open('FILE.py').read())"`. Validate logic by running queries directly against Metabase via the patterns at the bottom of `metabase-dashboard-guide.md` §10 (POST `/api/card/{id}/query`).

## Architecture

`sspm_dashboard_setup.py` is a single-file framework with these layers:

1. **HTTP** (`_request`, `api_get`, `api_post`, `api_put`) — uses `http.client` directly (see gotchas below). All mutating calls respect `DRY_RUN`.
2. **Discovery** (`find_database`, `find_collection`, `find_dashboard`, `find_card`) — idempotency by name+parent. Treats 404 as "not found" (default empty), which is what makes DRY_RUN's fake IDs work.
3. **Query builders** (`q_kpi_count`, `q_avg`, `q_age_range`, `q_bar_by_*`, `q_map`, `q_map_via_lookup`, `q_heatmap_*`, `q_stacked_month`, …) — produce MongoDB aggregation pipelines as JSON strings using the `__PH_START__` placeholder trick described in §1 of the guide.
4. **Card factory** (`create_card`) — wraps the first `$match` body with `$and` and injects optional-filter blocks `[[ ,{"campo": {{tag}}} ]]`. Idempotent per (name, collection_id).
5. **Layout** (`push_dashboard_layout`) — single-tab grid: KPIs (4 per row, 6×4) → charts (2 per row, 12×8) → maps (24×14) → tables (24×12). Always passes `tabs: []` to `PUT /api/dashboard/:id/cards`.
6. **Declarative config** (`DASHBOARDS = [...]`) — all 14 dashboards as data, dispatched via `build_query()` to the right query builder. Adding a chart usually means adding one dict.

Companion scripts (`fix_age_cards.py`, etc.) `import` from `sspm_dashboard_setup` to reuse the query builders rather than reimplementing them.

## Gotchas that took real debugging — read before editing

These are recorded in `metabase-dashboard-guide.md` but are easy to miss:

- **Use `http.client` directly.** This server returns HTTP 403 to `urllib` (and most likely `requests`). Don't replace.
- **Never quote `{{tag}}` in MongoDB queries.** `"{{tag}}"` becomes raw `2026-03-07` (invalid JSON); `{{tag}}` becomes `"2026-03-07"` (valid). Build queries with the `PH = "__PH_START__"` placeholder, then `q.replace(f'"{PH}"', "{{start}}")`.
- **One template tag per card with date range.** Metabase's `date/range` parameter only sends the value to one tag. Use `{{start}}` receiving `"YYYY-MM-DD~YYYY-MM-DD"` and extract both ends with `$substrCP`.
- **Date comparison uses `_fc/_sc/_ec` strings (`YYYYMMDD`).** Mongo's `$dateFromString` doesn't play well with these views' string-typed dates. Compare lexicographically.
- **Always pass `tabs` to `PUT /api/dashboard/:id/cards`.** Empty array is fine; omitting causes a FK 500.
- **`PUT /api/dashboard/:id/cards` (≥0.47) is the unified endpoint.** Don't use the old per-card endpoints.
- **Database name is `Vistas_e` (id=3), not "SSPM_dashboard Vistas MongoDB"** despite what the spec says. The `engine` is `mongo`.
- **Many fields in `dashboardproyect.md` don't exist in the views.** Verified missing: `fuero`, `presentado_ante`, `estado_origen`, `situacion_juridica`, `nombre_agente`, `unidad`, `delito` (in víctimas), `rango_edad`. **Always sample one document before writing a query that depends on a field.**
- **`edad` is stored as string in `mv_er_detenidos` and `mv_er_victimas`.** Use `_edad_int_expr()` / `edad_between()` helpers — they `$convert` defensively with `onError: -1` and filter to `0..120`. Numeric comparisons (`$lt 18`, `$gte 60`) directly against the field silently misbehave.
- **lat/lon coverage is sparse on entity views** (28% on detenidos, 16% on víctimas). For maps, prefer `mv_ubicacion` (filter with a flag like `cantidad_detenidos > 0`) or `q_map_via_lookup` for entities without a flag column.
- **PII lives in `mv_er_detenidos.nombre`/`domicilio` and `mv_er_victimas.nombre`.** Cards don't expose them today, but the underlying view is queryable from Metabase's SQL editor. Anonymization is a known open item — see the bottom of `metabase-dashboard-guide.md`-related conversation history for the recommended split (`_publica` / `_restringida` views).

## Conventions for extending

- Keep dashboards declarative: add to `DASHBOARDS` config rather than writing imperative code.
- New visualization → add a `q_*` builder, register it in `build_query()`'s dispatch, then reference by `"fn": "..."` in `DASHBOARDS`.
- For one-off in-place fixes (e.g., updating a few cards without rebuild churn), follow the `fix_age_cards.py` pattern: import builders, list `(card_id, lambda)` pairs, PUT.
- Standard global parameters (`param_periodo`, `param_distrito`, `param_sector`) are wired automatically by `push_dashboard_layout` + `_mappings_for_card`. Any new template tag added to a query needs both a parameter in `standard_parameters()` and a target in `_mappings_for_card`.
- `ParteInformativa` is forbidden as a BI source. Always read `mv_*` views.
