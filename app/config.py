from pathlib import Path

MODEL = 'claude-haiku-5-5'
MAX_TOKENS = 2048
USD_RATE = 100
MODEL_COST = {
    'in': 2,
    'out': 10
}

def getPolicy():
    return (Path(__file__).parent / 'policy.txt').read_text()

SYSTEM= f"""You are a helpful customer support assistant. You answer user queries
    Always answer from the the following:
    
    {getPolicy()}

    For any other unrelated queries or outside the above knowledge base, never assume, simply
    say you dont know about it and an employee will shortly connect with you.
"""