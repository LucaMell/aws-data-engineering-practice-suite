import importlib.util
from pathlib import Path
import pandas as pd

spec = importlib.util.spec_from_file_location("batch_app", Path(__file__).with_name("app.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
transform = module.transform


def test_transform():
    result = transform(pd.DataFrame([{"order_id":"1","email":" A@B.COM ","order_date":"2026-01-01","amount":"2"}]))
    assert result.iloc[0]["email"] == "a@b.com"
