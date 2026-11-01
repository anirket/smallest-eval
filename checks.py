import json


def answer_contains(output, context):
    print(context)
    expected = context['vars']['expected']
    answer = json.loads(output)['response']
    passed = expected.lower() in answer.lower()
    return {'pass': passed, 'score': int(passed), 'reason': f'Looking for "{expected}" in: {answer}'}
