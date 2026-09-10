import json
from pathlib import Path
def test_sample(): assert "@" in json.loads((Path(__file__).parent / "sample/event.json").read_text())["email"]
