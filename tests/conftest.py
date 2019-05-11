import pytest
import json


@pytest.fixture
def github_push_payload():
    return json.loads(open('tests/shards/push.json').read())
