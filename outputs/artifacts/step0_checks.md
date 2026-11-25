# Step 0 checks (UC1)

Date: 2026-11-26. Branch `work/data-discovery`. Python 3.12.4 in `.venv` (anthropic 1.17.0, jsonschema 4.26.0, pytest 9.2.0).

## Model backend
- Gateway variables (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`): all unset. Intentional: no gateway credentials were provided.
- The pipeline uses the opt-in Claude Code backend, selected in `.env`:
  `DISCOVERY_BACKEND=claude-code`, `DISCOVERY_MODEL=claude-sonnet-5-5`, `DISCOVERY_EFFORT=high`.
- Claude Code CLI 2.1.316. In the trace, the model appears as `claude-code:claude-sonnet-5-5`.

## Offline tests (`python -m pytest tests/ -q`): 52 collected, 32 passed, 20 failed
| File | Passed | Failed |
|---|---|---|
| `tests/test_tools_offline.py` | 24 | 0 |
| `tests/test_agent_loop.py` | 7 | 0 |
| `tests/test_learner_gaps.py` | 1 | 20 |

The 20 failures are the expected open learner gaps, not implemented here:
- G1 (`extract_licence`): 9 tests
- G3 (`jsonstat_summary`): 2 tests
- G4 (three rules in `risk_rules.py`): 7 tests
- G5 (verdict calibration in `prompts/risk_assessor.md`): 1 test
- G6 (`ec.europa.eu` not on the allowlist): 1 test

## Tool smoke tests (no LLM)
- `search_internal_catalog {"query": "hourly air pollutants"}`: JSON, 3 hits (`traffic.hourly_counts`, `airq.station_readings`, `counter_replacement_2024`).
- `inspect_dataset_link {"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}`: JSON, HTTP 200, `link.uci_360` (`uci_dataset_page`), 2 files; licence is null because `extract_licence` is the G1 TODO.
- `list_external_register {}`: JSON, 4 UC1 sources (`policy.open_data_links`, `api.open_meteo_archive`, `api.nager_public_holidays`, `vendor.atmosdata_pro`).
