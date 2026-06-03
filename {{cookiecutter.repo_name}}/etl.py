# Source: {{ cookiecutter.source_system }}
# Target: {{ cookiecutter.target_system }}
# Read tables: {{ cookiecutter.input_tables }}
# Transform to tables: {{ cookiecutter.output_tables }}

import os

import gluestick as gs
import pandas as pd

ROOT_DIR = os.environ.get("ROOT_DIR", ".")
INPUT_DIR = f"{ROOT_DIR}/sync-output"
OUTPUT_DIR = f"{ROOT_DIR}/etl-output"
SNAPSHOT_DIR = f"{ROOT_DIR}/snapshots"


def transform(df: pd.DataFrame) -> pd.DataFrame:
    return df


def run() -> None:
    reader = gs.Reader(INPUT_DIR)
    for stream in eval(str(reader)):
        df = reader.get(stream, catalog_types=True)
        if df is None or df.empty:
            continue
        df = transform(df)
        keys = reader.get_pk(stream) or []
        gs.to_export(df, stream, OUTPUT_DIR, keys=keys)


if __name__ == "__main__":
    run()
