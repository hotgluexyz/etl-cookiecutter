import json
from pathlib import Path

import gluestick as gs

FIXTURES = Path(__file__).parent / "fixtures"


def test_map_fields_fixture():
    row = json.loads((FIXTURES / "sample_row.json").read_text())
    mapping = json.loads((FIXTURES / "sample_mapping.json").read_text())
    result = gs.map_fields(row, mapping)
    assert result["externalId"] == "99"
    assert result["status"] == "active"


def test_lookup_operator():
    row = {"active": False}
    mapping = {
        "status": {
            "lookup": {
                "src": "active",
                "map": {"True": "active", "False": "inactive"},
            }
        }
    }
    assert gs.map_fields(row, mapping)["status"] == "inactive"