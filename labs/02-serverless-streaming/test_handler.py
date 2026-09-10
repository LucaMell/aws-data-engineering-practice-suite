import base64, json


def test_fixture_shape():
    value={"event_id":"e","email":"a@b.com"}
    assert json.loads(base64.b64decode(base64.b64encode(json.dumps(value).encode()))) == value

