from pathlib import Path
def test_seed(): assert "CREATE TABLE customers" in (Path(__file__).parent / "sample/init.sql").read_text()
