# hotglue ETL Cookiecutter

## Recommended: `generate_etl.py`

Asks only relevant questions (no duplicate read/one-way fields when bidirectional):

```bash
pip install click
python generate_etl.py
```

Uses **`source_system` / `target_system`** for the one-way job or the **READ** job; **WRITE** job uses the same labels in the wizard with values stored as `write_source_system` / `write_target_system` in the template (cookiecutter needs distinct keys).

## Raw `cookiecutter` prompt order

| Step | Field | Notes |
|------|--------|--------|
| 1 | `script_kind` | **basic** stops here logically (still answer later prompts with defaults or blanks) |
| 2 | `bidirectional` | **transformation** only — separate read/write jobs |
| 3 | `mapping_style` | `fixed_mapping` \| `widget_custom_mapping` \| `unified_schema_{accounting,crm,ecommerce}` |
| 4 | `source_system`, `target_system`, `input_streams`, `output_streams` | One-way **or READ job** when bidirectional |
| 5 | `write_source_system`, … | **WRITE job only** (skip if not bidirectional) |

**basic:** minimal `etl.py`; use `--no-input` or skip meaning in remaining prompts.

```bash
cookiecutter /path/to/etl-cookiecutter --no-input \
  repo_name=my-script script_kind=basic
```

## Mapping styles

- **fixed_mapping** — `streams/<name>.py` with `mapping = {}`
- **widget_custom_mapping** — tenant-config from UI; repo file for dev
- **unified_schema_*** — + Pydantic models (vertical is in the choice name)

Reference data works with all transformation styles (`reference_data/`).

## Export

Singer by default via `gs.to_export`; set `DEFAULT_EXPORT_FORMAT` to `csv` or `parquet`.

## Agents

Generated `AGENTS.md` points to [hotglue-skills](https://github.com/hotgluexyz/hotglue-skills) → **creating-hotglue-etl-scripts** (scaffold, archetypes, patterns).