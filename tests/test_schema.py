import json
def test_generated_schema():
    with open('data/generated_events.json','r',encoding='utf-8') as f:
        data = json.load(f)
    assert 'events' in data
    for e in data['events']:
        assert 'title' in e and isinstance(e['title'], str)
        assert 'summary' in e and isinstance(e['summary'], str)
        assert 'date' in e
        assert 'relevance' in e
