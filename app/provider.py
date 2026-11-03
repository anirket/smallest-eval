from dotenv import load_dotenv
from anthropic import Anthropic
import os
from config import MODEL, MAX_TOKENS, MODEL_COST, USD_RATE, SYSTEM

load_dotenv()
api_key = os.environ['ANTHROPIC_API_KEY']


def call_llm(prompt):
    anthropic = Anthropic(api_key=api_key)
    messages = [
        {
            'role': 'user',
            'content': prompt
        }
    ]
    result = anthropic.messages.create(
        model=MODEL,
        system=SYSTEM,
        max_tokens=MAX_TOKENS,
        messages=messages
    )
    response = ''
    usage = result.usage
    for block in result.content:
        if block.type == 'text':
            response += block.text

    return {
        'output': response,
        'tokenUsage': {
            'prompt': usage.input_tokens,
            'completion': usage.output_tokens,
            'total': usage.output_tokens + usage.input_tokens
        },
        'cost': ((usage.output_tokens * MODEL_COST['out'] + usage.input_tokens * MODEL_COST['in']) / 1_000_000) * USD_RATE
    }

def call_api(prompt, options, context):
    return call_llm(prompt)
