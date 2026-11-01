from dotenv import load_dotenv
from anthropic import Anthropic
import os
from config import MODEL, MAX_TOKENS, MODEL_COST, USD_RATE
from pydantic import BaseModel, Field

load_dotenv()
api_key = os.environ['ANTHROPIC_API_KEY']


class Result(BaseModel):
    response: str = Field(..., description="response from LLM")


def call_llm(prompt):
    anthropic = Anthropic(api_key=api_key)
    messages = [
        {
            'role': 'user',
            'content': prompt
        }
    ]
    result = anthropic.messages.parse(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
        output_format=Result
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

if __name__ == '__main__':
    defaultPrompt = 'Hello, who are you?'
    print(call_llm(defaultPrompt))