"""Helpers for transformation ETL scripts."""

from __future__ import annotations

import json
import os
from typing import Dict

import gluestick as gs
import pandas as pd

ROOT_DIR = os.environ.get("ROOT_DIR", ".")
OUTPUT_DIR = os.path.join(ROOT_DIR, "etl-output")
EMPTY_MAP: dict = dict()


{% if cookiecutter.mapping_style == "widget_custom_mapping" %}
def load_tenant_config() -> dict:
    path = os.path.join(ROOT_DIR, "snapshots", "tenant-config.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return dict()


def tenant_mapping_overrides(flow_id: str) -> Dict[str, dict]:
    tenant_config = load_tenant_config()
    hg_mapping = tenant_config.get("hotglue_mapping")
    if not isinstance(hg_mapping, dict):
        hg_mapping = EMPTY_MAP
    raw = hg_mapping.get("mapping")
    if not raw:
        return dict()
    fields_map, _ = gs.read_tenant_custom_mapping(tenant_config, flow_id=flow_id)
    if not fields_map:
        return dict()
    return {stream: mapping for stream, mapping in fields_map.items() if isinstance(mapping, dict)}
{% endif %}


def transform_stream(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    if not mapping:
        return df
    mapped = gs.map_fields_df(df, mapping, EMPTY_MAP)
    present = [c for c in mapping if c in mapped.columns]
    if present:
        mapped = mapped[present]
    return mapped


{% if cookiecutter.mapping_style == "unified_schema_accounting" %}
def validate_unified_records(df: pd.DataFrame) -> pd.DataFrame:
    from hotglue_models_accounting.accounting import Account

    validate_cfg = dict()
    validate_cfg["timezone"] = "UTC"
    records = gs.validate_model(
        df.to_dict(orient="records"), Account, validate_cfg, raise_error=False
    )
    return pd.DataFrame([r.model_dump() for r in records]) if records else df
{% elif cookiecutter.mapping_style == "unified_schema_crm" %}
def validate_unified_records(df: pd.DataFrame) -> pd.DataFrame:
    from hotglue_models_crm.crm import Contact

    validate_cfg = dict()
    validate_cfg["timezone"] = "UTC"
    records = gs.validate_model(
        df.to_dict(orient="records"), Contact, validate_cfg, raise_error=False
    )
    return pd.DataFrame([r.model_dump() for r in records]) if records else df
{% elif cookiecutter.mapping_style == "unified_schema_ecommerce" %}
def validate_unified_records(df: pd.DataFrame) -> pd.DataFrame:
    from hotglue_models_ecommerce.ecommerce import Order

    validate_cfg = dict()
    validate_cfg["timezone"] = "UTC"
    records = gs.validate_model(
        df.to_dict(orient="records"), Order, validate_cfg, raise_error=False
    )
    return pd.DataFrame([r.model_dump() for r in records]) if records else df
{% endif %}