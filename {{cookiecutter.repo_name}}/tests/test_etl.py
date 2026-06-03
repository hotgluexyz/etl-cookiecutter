import pandas as pd

from etl import transform


def test_transform_returns_dataframe():
    df = pd.DataFrame({"id": [1], "name": ["alpha"]})
    result = transform(df)
    assert list(result.columns) == ["id", "name"]
    assert len(result) == 1
