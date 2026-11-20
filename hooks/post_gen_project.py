"""Finalize generated ETL repo layout from script_kind, bidirectional, and mapping_style."""

import os
import shutil
import sys
import textwrap

SCRIPT_KIND = "{{ cookiecutter.script_kind }}"
BIDIRECTIONAL = "{{ cookiecutter.bidirectional }}"
MAPPING_STYLE = "{{ cookiecutter.mapping_style }}"
INPUT_STREAMS = "{{ cookiecutter.input_streams }}"
OUTPUT_STREAMS = "{{ cookiecutter.output_streams }}"
WRITE_IN = "{{ cookiecutter.write_input_streams }}"
WRITE_OUT = "{{ cookiecutter.write_output_streams }}"

ETL_VARIANTS = (
    "etl_basic.py",
    "etl_declarative.py",
    "etl_bidirectional.py",
    "etl_unified.py",
)


def _split_tables(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]


def _pair_streams(inputs: str, outputs: str) -> list[tuple[str, str]]:
    ins = _split_tables(inputs)
    outs = _split_tables(outputs)
    if not ins:
        return []
    if not outs:
        outs = ins[:]
    if len(outs) != len(ins):
        print(
            f"Warning: {len(ins)} input stream(s) but {len(outs)} output stream(s); "
            "padding or truncating outputs to match inputs (1st→1st, …).",
            file=sys.stderr,
        )
        if len(outs) < len(ins):
            outs = outs + ins[len(outs) :]
        else:
            outs = outs[: len(ins)]
    return list(zip(ins, outs))


def _remove(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def _write_stream_py(folder: str, stream: str, output_stream: str) -> None:
    validate_block = ""
    extra_utils = "transform_stream"
    if MAPPING_STYLE.startswith("unified_schema_"):
        validate_block = "            df = validate_unified_records(df)\n"
        extra_utils = "transform_stream, validate_unified_records"
    body = textwrap.dedent(
        f'''
        """Transform sync stream: {stream}"""

        import gluestick as gs

        from utils import {extra_utils}

        INPUT_STREAM = "{stream}"
        MAPPING = dict(externalId="id")
        output_stream = "{output_stream}"


        def map_{stream}(reader: gs.Reader, output_dir: str, mapping=None) -> None:
            df = reader.get(INPUT_STREAM, catalog_types=True)
            if df is None or df.empty:
                return
            effective = dict(MAPPING)
            if mapping:
                effective.update(mapping)
            df = transform_stream(df, effective)
{validate_block}            gs.to_export(df, output_stream, output_dir, keys=["id"])
        '''
    ).strip()
    path = os.path.join(folder, f"{stream}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "\n")


def _stream_symbol(stream: str, *, write: bool, write_aliases: set[str]) -> str:
    if write and stream in write_aliases:
        return f"write_{stream}"
    return stream


def _stream_call(stream: str, widget: bool, *, write: bool, write_aliases: set[str]) -> str:
    sym = _stream_symbol(stream, write=write, write_aliases=write_aliases)
    override = f', overrides.get("{stream}")' if widget else ""
    return f"        {sym}.map_{stream}(reader, OUTPUT_DIR{override})"


def _stream_calls_block(
    pairs: list[tuple[str, str]],
    widget: bool,
    *,
    write: bool,
    write_aliases: set[str],
) -> str:
    if not pairs:
        return "        pass"
    return "\n".join(
        _stream_call(stream, widget, write=write, write_aliases=write_aliases)
        for stream, _ in pairs
    )


def _patch_etl(
    project: str,
    read_pairs: list[tuple[str, str]],
    write_pairs: list[tuple[str, str]],
    oneway_pairs: list[tuple[str, str]],
) -> None:
    etl_path = os.path.join(project, "etl.py")
    with open(etl_path, encoding="utf-8") as f:
        content = f.read()

    widget = MAPPING_STYLE == "widget_custom_mapping"
    import_lines: list[str] = []
    if BIDIRECTIONAL == "yes":
        read_names = [s for s, _ in read_pairs]
        write_names = [s for s, _ in write_pairs]
        write_aliases = set(read_names) & set(write_names)
        if read_names:
            import_lines.append(f"from read_streams import {', '.join(read_names)}")
        for stream in write_names:
            if stream in write_aliases:
                import_lines.append(f"from write_streams import {stream} as write_{stream}")
            elif stream not in read_names:
                import_lines.append(f"from write_streams import {stream}")
        content = content.replace(
            "__COOKIECUTTER_READ_STREAM_CALLS__",
            _stream_calls_block(read_pairs, widget, write=False, write_aliases=write_aliases),
        )
        content = content.replace(
            "__COOKIECUTTER_WRITE_STREAM_CALLS__",
            _stream_calls_block(write_pairs, widget, write=True, write_aliases=write_aliases),
        )
    else:
        names = [s for s, _ in oneway_pairs]
        if names:
            import_lines.append(f"from streams import {', '.join(names)}")
        content = content.replace(
            "__COOKIECUTTER_STREAM_CALLS__",
            _stream_calls_block(oneway_pairs, widget, write=False, write_aliases=set()),
        )

    if import_lines:
        anchor = "import gluestick as gs\n"
        content = content.replace(anchor, anchor + "\n".join(import_lines) + "\n", 1)

    with open(etl_path, "w", encoding="utf-8") as f:
        f.write(content)


def _select_etl_variant() -> str:
    if SCRIPT_KIND == "basic":
        return "etl_basic.py"
    if BIDIRECTIONAL == "yes":
        return "etl_bidirectional.py"
    if MAPPING_STYLE.startswith("unified_schema_"):
        return "etl_unified.py"
    return "etl_declarative.py"


def main() -> None:
    project = os.getcwd()
    selected = _select_etl_variant()

    for name in ETL_VARIANTS:
        path = os.path.join(project, name)
        if name == selected:
            shutil.move(path, os.path.join(project, "etl.py"))
        else:
            _remove(path)

    for stale in (
        "mapping.json",
        "mapping.schema.json",
        "docs",
        "reference_data",
        "stream_pairs.json",
        "stream_handlers.py",
    ):
        _remove(os.path.join(project, stale))

    if SCRIPT_KIND == "basic":
        for rel in (
            "utils.py",
            "read_streams",
            "write_streams",
            "streams",
            "tests/test_mappings.py",
            "tests/fixtures",
            "__smoke-tests__",
        ):
            _remove(os.path.join(project, rel))
        return

    _remove(os.path.join(project, "tests", "test_etl.py"))

    if BIDIRECTIONAL == "yes":
        _remove(os.path.join(project, "streams"))
        read_dir = os.path.join(project, "read_streams")
        write_dir = os.path.join(project, "write_streams")
        os.makedirs(read_dir, exist_ok=True)
        os.makedirs(write_dir, exist_ok=True)

        read_pairs = _pair_streams(INPUT_STREAMS, OUTPUT_STREAMS)
        write_pairs = _pair_streams(WRITE_IN, WRITE_OUT)
        for in_stream, out_stream in read_pairs:
            _write_stream_py(read_dir, in_stream, out_stream)
        for in_stream, out_stream in write_pairs:
            _write_stream_py(write_dir, in_stream, out_stream)
        _patch_etl(project, read_pairs, write_pairs, [])
    else:
        _remove(os.path.join(project, "read_streams"))
        _remove(os.path.join(project, "write_streams"))
        streams_dir = os.path.join(project, "streams")
        os.makedirs(streams_dir, exist_ok=True)
        oneway_pairs = _pair_streams(INPUT_STREAMS, OUTPUT_STREAMS)
        for in_stream, out_stream in oneway_pairs:
            _write_stream_py(streams_dir, in_stream, out_stream)
        _patch_etl(project, [], [], oneway_pairs)


if __name__ == "__main__":
    main()