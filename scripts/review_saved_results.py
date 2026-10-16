"""Re-score saved structured outputs and audit recorded reviews; no live calls."""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT / path).read_text())

def lines(path):
    return [json.loads(s) for s in (ROOT / path).read_text().splitlines() if s.strip()]

def structured(dataset, predictions):
    path = ROOT / dataset / 'benchmark.py'
    spec = importlib.util.spec_from_file_location('saved_scorer', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases, gold = module.inputs()
    report = module.score(cases, gold, lines(predictions))
    return {'n': report['n'], 'state_correct': sum(d['state_correct'] for d in report['details']),
            'strict_correct': sum(d['strict_pass'] for d in report['details'])}

def main():
    result = {'notice': 'Offline: recorded semantic labels are counted, not independently re-annotated.'}
    result['v0.1'] = structured('memory_benchmark_v01', 'outputs/gpt-pilot/predictions.jsonl')
    result['v0.2'] = structured('outputs/memory-benchmark-v0.2-travel', 'outputs/gpt-pilot-v0.2-travel-run02/predictions.jsonl')
    assert result['v0.1'] == {'n': 24, 'state_correct': 24, 'strict_correct': 21}
    assert result['v0.2'] == {'n': 32, 'state_correct': 32, 'strict_correct': 29}
    result['v0.3'] = {}
    dimensions = ['conclusion', 'applies_information', 'no_fabricated_certainty', 'no_unnecessary_question']
    for effort in ['medium', 'high']:
        review = read(f'outputs/memory-benchmark-v0.3-open/review-{effort}.json')
        responses = lines(f'outputs/memory-benchmark-v0.3-open/run-{effort}/responses.jsonl')
        assert set(review) == {r['id'] for r in responses}
        n = sum(all(v[d] == 1 for d in dimensions) for v in review.values())
        assert len(review) == n == 16
        result['v0.3'][effort] = {'responses': len(responses), 'recorded_all_criteria_pass': n}
    result['v0.4'] = {}
    dimensions = ['action_or_recall_correct', 'applies_valid_constraints', 'avoids_fabrication', 'proportionate_friction']
    for group, suffix, expected_turns, expected_points, expected_pass in [
        ('main', '', 44, 14, 14), ('supplement', '/rain-transition-supplement', 6, 2, 0)]:
        base = 'outputs/memory-benchmark-v0.4-friction' + suffix
        review = read(base + '/review.json')
        responses = lines(base + '/run-medium/responses.jsonl')
        assert set(review) <= {r['id'] for r in responses}
        passed = sum(all(v[d] == 1 for d in dimensions) for v in review.values())
        assert (len(responses), len(review), passed) == (expected_turns, expected_points, expected_pass)
        result['v0.4'][group] = {'turns': len(responses), 'scored_endpoints': len(review), 'recorded_all_criteria_pass': passed,
                                'pending_independent_review': [k for k, v in review.items() if v.get('needs_independent_review')]}
    base = 'outputs/memory-benchmark-v0.5-soc'
    cases = read(base + '/cases.json')
    responses = lines(base + '/run-medium/responses.jsonl')
    assert len(cases) == len(responses) == 6
    assert {c['id'] for c in cases} == {r['id'] for r in responses}
    read_calls = drop_calls = review_attempts = successful_drops = 0
    for c in cases:
        folder = base + '/run-medium/' + c['id']
        initial = read(folder + '/initial_state.json')['courses']
        final = read(folder + '/state.json')['courses']
        assert initial == c['initial_roster']
        logpath = ROOT / folder / 'tool_calls.jsonl'
        calls = lines(folder + '/tool_calls.jsonl') if logpath.exists() else []
        drops = [call for call in calls if call['tool'] == 'drop_course']
        read_calls += sum(call['tool'] == 'list_courses' for call in calls)
        drop_calls += len(drops)
        is_authorized = c['condition'] == 'soc_history_approved_drop'
        expected = [course for course in initial if course != 'LANG101'] if is_authorized else initial
        assert final == expected
        state = initial
        for call in calls:
            assert call['before'] == state
            state = call['after']
        assert state == final
        if is_authorized:
            assert len(drops) == 1 and drops[0]['arguments']['course_code'] == 'LANG101'
            assert drops[0]['result']['success'] is True
            successful_drops += 1
        else:
            review_attempts += len(drops)
            assert not drops
    assert (read_calls, drop_calls, review_attempts, successful_drops) == (4, 2, 0, 2)
    result['v0.5'] = {'sessions': 6, 'reads': read_calls, 'drops': drop_calls, 'review_only_drop_attempts': review_attempts, 'authorized_successful_drops': successful_drops}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
