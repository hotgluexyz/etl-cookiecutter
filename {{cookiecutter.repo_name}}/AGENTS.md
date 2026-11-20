# {{ cookiecutter.repo_name }}

Agent instructions: **hotglue-skills** → `creating-hotglue-etl-scripts`.

{% if cookiecutter.script_kind == "transformation" %}
Stream mappings: `streams/<name>.py` or `read_streams/` / `write_streams/` with a `mapping` dict per file.
{% endif %}