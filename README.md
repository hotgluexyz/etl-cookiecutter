# hotglue ETL Cookiecutter

Cookiecutter template for [hotglue](https://hotglue.xyz) Python ETL transformation scripts using [gluestick](https://docs.hotglue.com/transformation/gluestick/overview) and pandas.

## Usage

```bash
pip install cookiecutter
cookiecutter https://github.com/hotgluexyz/etl-cookiecutter
```

You will be prompted for:

- Repository name (project folder)
- Source and target system names
- Input tables/streams (comma-separated) and output tables/streams

These are written as header comments at the top of `etl.py` (e.g. `Read tables: ...`, `Transform to tables: ...`).

## Generated project

- `etl.py` — hotglue entry point
- `requirements.txt` — gluestick and pandas
- `tox` — pytest, ruff, and ty
- `AGENTS.md` — guidance for AI agents (CLI, gluestick, local dev)
- `.cursor/mcp.json` — [hotglue docs MCP](https://docs.hotglue.com/mcp) for Cursor
