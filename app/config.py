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

    
"""