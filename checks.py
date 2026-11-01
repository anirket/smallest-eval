def answer_contains(output, context):
    print(context)
    expected = context['vars']['expected']
    passed = expected.lower() in output.lower()
    return {'pass': passed, 'score': int(passed), 'reason': f'Looking for "{expected}" in: {output}'}
