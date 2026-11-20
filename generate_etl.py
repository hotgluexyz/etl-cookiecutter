#!/usr/bin/env python3
"""Interactive ETL scaffold — asks only the questions that apply, then runs cookiecutter --no-input."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import click
except ImportError:
    print("Install click: pip install click", file=sys.stderr)
    sys.exit(1)

TEMPLATE = Path(__file__).resolve().parent
MAPPING_CHOICES = [
    "fixed_mapping",
    "widget_custom_mapping",
    "unified_schema_accounting",
    "unified_schema_crm",
    "unified_schema_ecommerce",
]


def _flow_pair(label: str) -> tuple[str, str, str, str]:
    click.echo(f"--- {label} ---")
    source_system = click.prompt("source_system", default="")
    target_system = click.prompt("target_system", default="")
    input_streams = click.prompt("input_streams", default="")
    output_streams = click.prompt("output_streams", default=input_streams)
    return source_system, target_system, input_streams, output_streams


@click.command()
@click.option("--output-dir", type=click.Path(), default=".")
def main(output_dir: str) -> None:
    repo_name = click.prompt("repo_name", default="my-etl-script")
    script_kind = click.prompt(
        "script_kind",
        type=click.Choice(["basic", "transformation"]),
        default="basic",
    )

    ctx: dict[str, str] = {
        "repo_name": repo_name,
        "script_kind": script_kind,
        "bidirectional": "no",
        "mapping_style": "fixed_mapping",
        "source_system": "",
        "target_system": "",
        "input_streams": "",
        "output_streams": "",
        "write_source_system": "",
        "write_target_system": "",
        "write_input_streams": "",
        "write_output_streams": "",
    }

    if script_kind == "transformation":
        ctx["bidirectional"] = click.prompt(
            "bidirectional",
            type=click.Choice(["no", "yes"]),
            default="no",
        )
        ctx["mapping_style"] = click.prompt(
            "mapping_style",
            type=click.Choice(MAPPING_CHOICES),
            default="fixed_mapping",
        )

        if ctx["bidirectional"] == "yes":
            s, t, i, o = _flow_pair("READ job")
            ctx["source_system"], ctx["target_system"] = s, t
            ctx["input_streams"], ctx["output_streams"] = i, o
            ws, wt, wi, wo = _flow_pair("WRITE job")
            ctx["write_source_system"], ctx["write_target_system"] = ws, wt
            ctx["write_input_streams"], ctx["write_output_streams"] = wi, wo
        else:
            s, t, i, o = _flow_pair("One-way transformation")
            ctx["source_system"], ctx["target_system"] = s, t
            ctx["input_streams"], ctx["output_streams"] = i, o

    args = ["cookiecutter", str(TEMPLATE), "--no-input", "-o", output_dir]
    for key, value in ctx.items():
        args.append(f"{key}={value}")

    click.echo("Running: " + " ".join(args))
    subprocess.run(args, check=True)


if __name__ == "__main__":
    main()