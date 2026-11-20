# {{ cookiecutter.source_system }} → {{ cookiecutter.target_system }} ({{ cookiecutter.mapping_style }})

import os

import gluestick as gs

{% if cookiecutter.mapping_style == "widget_custom_mapping" %}
from utils import tenant_mapping_overrides
{% endif %}

ROOT_DIR = os.environ.get("ROOT_DIR", ".")
INPUT_DIR = f"{ROOT_DIR}/sync-output"
OUTPUT_DIR = f"{ROOT_DIR}/etl-output"
FLOW_ID = os.environ.get("FLOW", "")

{% if cookiecutter.mapping_style == "widget_custom_mapping" %}
overrides = tenant_mapping_overrides(FLOW_ID)
{% else %}
overrides = dict()
{% endif %}
reader = gs.Reader(INPUT_DIR)

__COOKIECUTTER_STREAM_CALLS__