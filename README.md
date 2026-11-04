# smallest-eval

![eval](https://github.com/anirket/smallest-eval/actions/workflows/eval.yml/badge.svg)

An automated test suite for an LLM app that runs on every pull request and blocks the merge if a prompt or model change makes the answers worse.

It ships with a tiny example app, a customer-support bot that answers only from `app/policy.txt`, and 10 test cases for it. Click **Use this template**, swap in your own app and cases, and you have evals in CI.

```
open a PR ─► GitHub Action ─► promptfoo runs 10 cases from evals/cases.yaml
                                  │  each case: your app (Python) → answer
                                  │             → code checks + LLM judge + cost/latency limits
                                  ▼
                      scripts/report.js → summary on the PR: pass rate, failures with the judge's reason, ₹, p50/p95 latency
                                  ▼
                      any case fails → red check · all pass → green check
```

## Quickstart

Needs Node 22+ and Python 3.12.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                      # then put your ANTHROPIC_API_KEY in it
npx promptfoo@0.125.1 eval -o results.json
node scripts/report.js results.json
```

`npx promptfoo@0.125.1 view` opens the results in the browser.

## How a case is checked

Three kinds of check, cheapest first:

1. **Code checks** (free, exact): `contains`, `icontains-all`, `not-icontains`, or a Python function in `evals/checks.py`.
2. **An LLM judge** (`llm-rubric`), only where code can't decide, e.g. "did it refuse the prompt injection?". Rubrics live in `evals/rubrics/`, one file per failure mode, each with an explicit PASS / FAIL list. The judge is `claude-haiku-5-5`, set in `promptfooconfig.yaml` under `defaultTest.options.provider`.
3. **Cost and latency limits** on every case, in `defaultTest`. Keep only checks that make sense for every case there; put everything else on the case it belongs to.

## Use it for your own app

| File | What to change |
|---|---|
| `app/provider.py` | `call_api(prompt, options, context)` must call your app and return `{output, tokenUsage, cost}` |
| `app/config.py`, `app/policy.txt` | The example app's model, prices and knowledge. Replace with your own |
| `evals/cases.yaml` | Your cases. Write the expected answers yourself, not with the model |
| `evals/rubrics/*.txt` | Judge rubrics: one failure mode per file, binary pass/fail |
| `promptfooconfig.yaml` | Cost and latency thresholds, and the judge model |

Then add your key to the repo: `gh secret set ANTHROPIC_API_KEY`.

## Is the judge any good?

The prompt-injection judge was checked against my own labels: it agreed on **6/6 held-out cases (κ = 1.00, n = 6)** and 14/14 on dev, up from κ = 0.84 before one rubric fix. Padding failing answers to 6–13× their length fooled it 0/4 times. Six cases is small; the method, the caveats and the raw results are in [CALIBRATION.md](CALIBRATION.md).

## Cost

One run of the 10 example cases costs about **₹0.12 for the app plus about ₹0.10 for the judge**: both are Haiku 5.5 ($0.10 / $0.50 per million tokens, ₹100 per USD, prices in `app/config.py`). Each case is capped at ₹0.05 by the `cost` check in `promptfooconfig.yaml`. If you change the model, update the prices in `app/config.py` too, or every ₹ figure will be wrong.

## Known limits

- **Pull requests from forks fail.** GitHub doesn't give secrets to fork PRs, so the eval can't call the API. Run it on a branch in your own copy instead.
- **The judge isn't deterministic.** The same answer can occasionally get a different verdict. Re-run before treating a single judge failure as a regression.
- **Latency depends on the API.** The limit is 15 s per case because a slow API call alone can take 8 s or more.
- **The badge shows runs on `main`.** It turns green once a push to `main` passes.
