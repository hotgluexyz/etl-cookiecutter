# Kind: basic — add source/target/stream notes here as you build the script.

import os

import gluestick as gs
import pandas as pd

ROOT_DIR = os.environ.get("ROOT_DIR", ".")
INPUT_DIR = f"{ROOT_DIR}/sync-output"
OUTPUT_DIR = f"{ROOT_DIR}/etl-output"
SNAPSHOT_DIR = f"{ROOT_DIR}/snapshots"


def transform(df: pd.DataFrame) -> pd.DataFrame:
    return df


reader = gs.Reader(INPUT_DIR)
for stream in reader.input_files:
    df = reader.get(stream, catalog_types=True)
    if df is None or df.empty:
        continue
    df = transform(df)
    keys = reader.get_pk(stream) or []
    gs.to_export(df, stream, OUTPUT_DIR, keys=keys)