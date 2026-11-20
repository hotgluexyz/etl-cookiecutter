# {{ cookiecutter.source_system }} → {{ cookiecutter.target_system }} ({{ cookiecutter.mapping_style }})

import os

import gluestick as gs

ROOT_DIR = os.environ.get("ROOT_DIR", ".")
INPUT_DIR = f"{ROOT_DIR}/sync-output"
OUTPUT_DIR = f"{ROOT_DIR}/etl-output"

reader = gs.Reader(INPUT_DIR)

__COOKIECUTTER_STREAM_CALLS__