# Parity validation notes

Validated against cookiecutter generation (`declarative_json` with `contacts` stream) and reference scripts.

## airbase (rillet-scripts) — declarative target

| Concern | airbase | cookiecutter `declarative_json` |
|---------|---------|----------------------------------|
| Mapping file | `mapping.json` read/write sections | Same; bidirectional uses `read_streams/` / `write_streams/` |
| Transform | `gs.map_fields` per row / stream | `gs.map_fields_df` in loop |
| Tenant mapping | `read_mapping()` file | `utils.load_mapping()` prefers tenant-config, falls back to file |
| Custom utils | Heavy (`get_id_from_snapshot`, etc.) | `reference_heavy` archetype + escape hatch docs |

**Remaining custom-only in airbase:** subsidiary currency defaults, line-item explosions, attachment transforms — implement in `utils.py` or custom handlers.

## mailchimp-scripts — simple + widget mapping

| Concern | mailchimp | cookiecutter `basic` |
|---------|-----------|----------------------|
| Structure | `transform()`-style stream logic | Passthrough `transform()` |
| Widget fields | `read_tenant_custom_mapping` + rename | Available via upgrade to declarative |
| Merge fields / nesting | Custom Python | Escape hatch — not generated |

**Agent path:** start `basic`, add `utils.py` for merge-field nesting, or migrate to declarative for column renames only.

## Gluestick version

Mapping ops (`lookup`, dot paths, `const`, `env`, `config`) require **gluestick ≥ 3.0.23**.