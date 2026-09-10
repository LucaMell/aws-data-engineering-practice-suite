import json
from pathlib import Path
def test_sample():
    assert json.loads((Path(__file__).parent / "sample/event.json").read_text())["event_id"] == "ecs-1"
