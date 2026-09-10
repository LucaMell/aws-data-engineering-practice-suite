import pathlib
def test_model(): assert "sum(amount)" in (pathlib.Path(__file__).parent / "models/customer_revenue.sql").read_text()
