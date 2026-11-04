# smallest-eval: Plan

## What we're building

**smallest-eval is an automated test suite for an LLM app.** It runs on every pull request and blocks the merge if a prompt or model change makes the answers worse.

A normal unit test checks `add(2, 2) == 4`. An LLM app's output changes every run and is rarely an exact string, so "is this answer right?" needs three kinds of check:

1. **Code checks** (free, exact): is it valid JSON? Does it contain "30 days"? Does every quote really appear in the resume? Did the agent call `calculate`?
2. **An LLM judge**, for what code can't decide: a second model reads the answer and returns pass/fail plus a reason against one rule, e.g. *"does this rewrite add any fact that isn't in the source?"*
3. **Cost and latency limits**: fail the run if a case costs more than ₹X or takes longer than N seconds.

**What it does, end to end:**

```
open a PR ─► GitHub Action ─► promptfoo runs 10 cases from evals/cases.yaml
                                   │  each case: your app (Python) → answer
                                   │             → code checks + judge + cost/latency limits
                                   ▼
                       report.py → summary on the PR: pass rate, failures with the judge's reason, ₹, p50/p95 latency,
                                   and the delta against the previous agent version
                                   ▼
                       any case fails → red check, merge blocked · all pass → green check + green badge
```

**The part that makes it worth talking about: calibrating the judge.** A judge is a model too, so it can be wrong. You hand-label 20 outputs yourself, run the judge on the same 20, and measure how often it agrees with you (agreement %, Cohen's kappa, TPR/TNR). Then you fix the judge's rubric once, re-measure, and test it for one known bias: favouring longer answers. The end result is a sentence most people can't say: *"my judge agrees with me at κ = 0.7 on 6 held-out cases, here's where it's wrong, and here's the bias I measured."*

**Cut on Nov 4 (see Scope cut below):** the version delta and the jd-lens / mini-agent retrofits.

**The second part (dropped): version the agent, not just the prompt.** The agent config has a `version` field. On every PR, the Action runs the eval against the PR's version and against the previous one (`main`), and prints the delta: pass rate, cases that flipped, ₹ and p95 latency. That turns "evals in CI" into "regression-tested agent versions": a prompt change shows up as a number on the PR before it merges.

**What you end up with:**
- **`smallest-eval`**: a GitHub template repo with a tiny example app. A stranger clicks "Use this template", swaps in their own app and cases, and has evals in CI.
- **`CALIBRATION.md`**: your judge-vs-human number on held-out cases, and one measured bias

**Done when:**
- [ ] `anirket/smallest-eval` is a template repo, the badge on `main` is green, and the eval blocks a failing PR (the sabotage PR)
- [x] The README's calibration section has a judge-vs-you number on held-out cases (agreement + Cohen's kappa + TPR/TNR) and the verbosity bias check
- [x] The README states the calibration number

**4 days, Nov 1 → Nov 4:** Day 1–2 learn (watch + hands-on), Day 3–4 build. Then smallest-eval is closed.

**Scope cut (Nov 4).** Day 5 is dropped, and Day 4 is cut to a 3-hour version. The jd-lens and mini-agent retrofits, the version delta, the pairwise position check, the judge leaderboard and the smuggle-a-fact challenge are out. Reason: the remaining work is mechanical or adds a new codebase; the one part that isn't mechanical is measuring the judge, so Day 4 keeps only that.

---

## Scoreboard (fill in as you go)

| | Your guess | Actual |
|---|---|---|
| κ of `resists_injection` v1 (Haiku) on dev | *write it on Day 2* | 0.84 |
| κ of the final judge on held-out | | 1.00 (n = 6) |
| Rubric versions it took | | 2 |
| Padded fails the judge started passing (out of 4) | | 0 |
| ₹ per CI run (template) | | ~₹0.23 (₹0.13 app + ~₹0.10 judge) |
| ₹ spent on the whole project | | |

Guessing before you measure is the fun part. Being wrong is a line in the essay.

---

## Decisions made up front

| Choice | Pick | Why |
|---|---|---|
| Runner | **promptfoo** (YAML cases, the built-in viewer, a CI exit code) | Strangers know it, and you don't need to rebuild a test runner |
| Your app inside promptfoo | **Python provider** (`file://app/provider.py`) | Your ships are Python; promptfoo calls your function directly |
| Calibration + report | **Your own Python** (`calibrate.py`, `report.py`) | This is the part worth owning and explaining in interviews |
| Judge verdict | **Binary pass/fail + a reason**, one judge per failure mode | Hamel: 1–5 scales can't be grounded or calibrated; you'll gate on pass/fail anyway |
| Models | App on `claude-haiku-5-5`; judge: Haiku vs Sonnet vs Opus on Day 4, then pick | Choosing a judge model on measured κ vs ₹ makes a good table |
| What gets calibrated | **`resists_injection`**, the template's own most interesting rubric (changed Nov 4, was jd-lens bullets) | Calibrates the judge you already ship, with no new codebase on the last day |
| Versioning | **`version` field on the agent config**; the Action runs the eval on the PR and on `main`, and prints the delta | Turns "evals in CI" into regression-tested agent versions |

```
smallest-eval/
  promptfooconfig.yaml        # providers, judge model, tests: file://evals/cases.yaml
  evals/cases.yaml            # the 10 cases
  evals/checks.py             # python assertions (deterministic, free)
  evals/rubrics/*.txt         # judge prompts, one file per failure mode, versioned
  app/provider.py             # call_api() → {output, tokenUsage, cost}
  app/agent.yaml              # version, model, prompt: the thing we version
  scripts/report.py           # results.json → markdown: pass rate, ₹, p50/p95 latency, --baseline for the delta
  calibration/labels.csv  calibration/calibrate.py  CALIBRATION.md
  .github/workflows/eval.yml
  .env.example  requirements.txt  README.md
```

---

## Before Day 1 · ~20 min (today, Oct 31)
- Node **22+** (`node -v`; promptfoo fails on 18, as Codemify hits on camera) → `npm i -g promptfoo` or use `npx promptfoo@<version>`
- `ANTHROPIC_API_KEY` in `.env`; `gh auth status` works
- Create the empty `anirket/smallest-eval` repo on GitHub now so Day 3 isn't blocked

| Day | Name | You'll walk away with |
|---|---|---|
| 1 (Nov 1) | **First blood** | promptfoo running your own Python, and a judge you've already fooled once |
| 2 (Nov 2) | **Who judges the judge?** | `cohen_kappa()` written, your κ guess on the scoreboard, essay evidence picked |
| 3 (Nov 3) | **The gate** | A sabotage PR caught by CI: red check, then green, plus a badge and a template repo |
| 4 (Nov 4) | **Judge on trial** (3-hour version) | Your judge measured against you on held-out cases, fixed once, and checked for verbosity bias. Project closed |

---

## Day 1 (Nov 1): First blood · ~3.75 hrs

**Mission:** go from "I've heard of promptfoo" to promptfoo calling **your** Python code and grading it.

**Done when:** a scratch promptfoo project calls your own Python function through a Python provider, has one code check + one `llm-rubric` check, and you've seen a failure in the viewer.

### Phase 1: Watch: why evals · ~45 min
1. Hamel, **LLM Evals: Common Mistakes**: https://www.youtube.com/watch?v=GL0XhAj5LPE (28 min at 1.5×). Write down 5 rules in your own words.
2. Hamel, **Error Analysis: The Highest ROI Technique**: https://www.youtube.com/watch?v=e2i6JbU2R-s (12 min)

Notes to take, since they feed the essay: *what would an eval have caught in jd-lens and in mini-agent?*

### Phase 2: Watch, read + type along: promptfoo · ~1 hr
1. **Codemify, PromptFoo Tutorial – How to Test AI**: https://www.youtube.com/watch?v=29EH2nryuAQ (17 min). Pause and do every step: `promptfoo init`, run, `promptfoo view`. Switch the provider to `anthropic:messages:claude-haiku-5-5`. Notice how a code check and an `llm-rubric` check sit on the same test.
2. **NerdLevelTech, Test LLM Prompts in CI with Promptfoo**: https://nerdleveltech.com/promptfoo-test-llm-prompts-ci-tutorial (written, May 2026: an `llm-rubric` check plus a GitHub Actions quality gate). Read it now; you build this on Day 3.

### Phase 3: Hands-on: a Python provider · ~1.5 hrs
- Docs: promptfoo Python provider: https://www.promptfoo.dev/docs/providers/python/
- Write `provider.py` with `call_api(prompt, options, context)` that calls Haiku and returns output **plus** token usage and cost
- Point `promptfooconfig.yaml` at `file://provider.py` and write 3 cases
- Add one `python` assertion (e.g. output is valid JSON), one `llm-rubric`, one `latency` and one `cost` assertion
- Break something on purpose and find it in the viewer
- `promptfoo eval -o results.json`, then open it: find per-test pass/fail, `latencyMs`, cost and token usage. Write down the JSON paths `report.py` will need on Day 3.

```python
def call_api(prompt, options, context):
    r = client.messages.create(model=MODEL, max_tokens=1000,
                               messages=[{"role": "user", "content": prompt}])
    u = r.usage
    return {"output": r.content[0].text,
            "tokenUsage": {"prompt": u.input_tokens, "completion": u.output_tokens,
                           "total": u.input_tokens + u.output_tokens},
            "cost": usd(u)}          # reuse PRICES from jd-lens/config.py
```

### 🔥 Challenge: fool the judge · ~15 min
Write a rubric like *"the answer must not mention pricing"*. Then hand-write 3 outputs that **do** leak pricing in sneaky ways ("it's less than a coffee a month", "two digits, starts with a 9") and run them through `llm-rubric`. How many slip through? Keep these. They're your first taste of Day 4, and a great opening for the essay.

---

## Day 2 (Nov 2): Who judges the judge? · ~3.5 hrs

**Mission:** understand why "the LLM said it's fine" isn't evidence, and write the maths that turns it into evidence.

**Done when:** `cohen_kappa()` is written and checked on toy data, the three readings are done, your κ guess is on the scoreboard, and your two essay failures are written down in 3 lines each.

### Phase 1: Watch: pairwise judging · ~15 min
1. **Siddhardhan, LLM as a Judge Explained, Hands-On**: https://www.youtube.com/watch?v=3FcYdRQPMCo&t=1080s, **from 18:00** (~13 min at 1.5×; the first 18 min are setup). Pairwise judge, JSON `{winner, reason}`. That's the setup where position bias shows up.

### Phase 2: Read · ~1 hr
- Hamel, **Using LLM-as-a-Judge: A Complete Guide**: https://hamel.dev/blog/posts/llm-judge/ (critique shadowing)
- oneuptime, **How to Calibrate an LLM-as-a-Judge Against Human Labels with Cohen's Kappa**: https://oneuptime.com/blog/post/2026-08-31-calibrate-llm-judge-cohens-kappa/view (read before writing `calibrate.py`). Read kappa next to the confusion matrix, not on its own.
- Eugene Yan, **Evaluating the Effectiveness of LLM-Evaluators**: https://eugeneyan.com/writing/llm-evaluators/ (only the position and verbosity sections; the bias checks on Day 4 use them)
- Hamel, **Your AI Product Needs Evals**: https://hamel.dev/blog/posts/evals/ (the canonical version of your essay; read it so you don't repeat it)

### Phase 3: Hands-on: the maths you'll present · ~1 hr
Write `calibration/calibrate.py` now, on fake data, so Day 4 is just running it. Kappa comes from `sklearn.metrics.cohen_kappa_score`; the confusion table from `confusion_matrix`.

- Guard the all-pass case: if every label on both sides is the same, kappa is 0/0, so report n/a instead of crashing
- Also compute **TPR** (judge passes what you passed) and **TNR** (judge fails what you failed), and print a 2×2 confusion table
- ⚠️ **Why kappa and not just agreement:** if 27 of 30 outputs pass, a judge that always says "pass" gets 90% agreement and **κ = 0**. Test exactly this case on your fake data. It's a good line for the essay.

### Phase 4: Pick the essay evidence · ~30 min
Candidates from your own READMEs:
- **Week 1 (jd-lens):** the eval was wrong, not the model. The substring matcher scored recall at **0.60** when the model was fine (`2–6` vs `2-6`, rewording). Also: bullets-only input gave 3/12 matches vs 9/12 with the full resume, which *looked* like a model problem and was a prompt problem.
- **Week 2 (mini-agent):** 20/20 passed, but **Haiku skipped `calculate`** on easy maths. Output-only checks can't see the path. And Sonnet quietly did steps 3–4 in its head after the step limit, where Haiku said they were missing.

Pick one from each week. Write 3 lines each: what happened, how you found it, what eval would have caught it earlier. Kept in `notes/eval-failures.md` for the essay later.

### 🔥 Challenge: place your bets · ~10 min
Fill in the **Your guess** column of the scoreboard now: κ for Haiku as judge, how many rubric versions it'll take, how often the pairwise judge will pick A. No peeking at the numbers in the videos.

---

## Day 3 (Nov 3): The gate · ~6.25 hrs

**Mission:** build the thing that stands between a bad prompt change and `main`, then try to sneak a bad change past it.

**Done when:** a PR on `smallest-eval` shows a green check with the cost/latency summary, the badge is in the README, and the repo is marked as a template.

### Phase 1: Example app + 10 cases · ~2 hrs
- The template needs a tiny built-in app so it works straight after cloning. One prompt → Haiku, e.g. "answer a customer question from this policy text"
- 10 cases in `evals/cases.yaml`: ~6 normal, 2 edge cases, 1 "the right answer is I don't know", 1 adversarial
- Every case gets **cheap checks first** (`contains`, `is-json`, `python`), and a judge check only where code can't decide
- ⚠️ Write the expected answers yourself, not with the model (same rule as mini-agent)
- ⚠️ A `defaultTest` assertion applies to **every** case, including ones it makes no sense for (Day 1: "is it funny" graded "What is 2+2?" and failed it). Keep only universal checks there (cost, latency); put rubrics on the cases they belong to.

```yaml
- description: refund after 45 days asks about exceptions
  vars: { input: "I bought the annual plan 45 days ago..." }
  assert:
    - type: python
      value: file://evals/checks.py:no_internal_rule
    - type: llm-rubric
      value: file://evals/rubrics/grounded.txt
    - type: latency
      threshold: 8000
    - type: cost
      threshold: 0.002
```

### Phase 2: Judge config · ~45 min
- Set the grader once: `defaultTest.options.provider: anthropic:messages:claude-haiku-5-5` (temporary; Day 4 decides)
- Rubric files: one failure mode each, a binary pass/fail, and the reason asked for **before** the verdict
- ⚠️ Check the llm-rubric docs: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/ to confirm `file://` works for the rubric value in your promptfoo version

### Phase 3: `report.py` · ~1.5 hrs
`results.json` → markdown with: pass rate, failures with the judge's reason, total and per-case ₹, **p50/p95 latency**, tokens, and the model + promptfoo version. Print to stdout so CI can append it to `$GITHUB_STEP_SUMMARY`.

### Phase 4: GitHub Action + badge · ~1.5 hrs
Docs: promptfoo GitHub Action: https://www.promptfoo.dev/docs/integrations/github-action/ · CI/CD: https://www.promptfoo.dev/docs/integrations/ci-cd/

```yaml
name: eval
on: [pull_request, push]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: npx promptfoo@<pinned-version> eval -c promptfooconfig.yaml -o results.json
        env: { ANTHROPIC_API_KEY: "${{ secrets.ANTHROPIC_API_KEY }}" }
      - if: always()
        run: python scripts/report.py results.json >> "$GITHUB_STEP_SUMMARY"
```

- `gh secret set ANTHROPIC_API_KEY`
- Badge in the README: `![eval](https://github.com/anirket/smallest-eval/actions/workflows/eval.yml/badge.svg)`
- ⚠️ The badge shows the status of runs on `main` (it only falls back to other branches while `main` has no runs). That's why `push` is in `on:`. Without it, PR runs would never turn the badge green.
- ⚠️ Pin the promptfoo version; `@latest` will change underneath you
- ⚠️ PRs from forks don't get secrets, so a stranger's PR will fail. Say this in the README.

### Phase 5: Make it a template · ~30 min
- README: what it is, a 5-command quickstart, how to swap in your own app (edit `app/provider.py` + `cases.yaml`), cost per run
- `.env.example`, then `gh repo edit anirket/smallest-eval --template`

### 🔥 Challenge: the sabotage PR · ~20 min
Play the well-meaning teammate. Open a PR titled **"chore: tighten system prompt"** that *looks* like a cleanup: shorter wording, but it quietly drops the line that keeps the app grounded in the policy. Then sit back and watch CI turn red on its own. Read the judge's reason in the PR summary, revert, and watch it go green. Screenshot both. This is the most convincing 10 seconds of the whole project, and it goes at the top of the README and in the essay.

---

## Day 4 (Nov 4): Judge on trial · ~3 hrs, then close

**Mission:** you know how to write a judge; today you measure one. "I built an LLM judge" is common. "I hand-labelled 20 outputs, measured my judge against them at κ = 0.68, and here's where it's blind" is rare, and it's the eval-literacy signal job posts ask for (define metrics, build eval pipelines, distinguish signal from noise).

**Done when:** `CALIBRATION.md` has κ / TPR / TNR for rubric v1 and v2 on dev, the v2 number on held-out, and the verbosity check; the README states the number; the badge is green.

No jd-lens: calibrate the judge you already have, **`evals/rubrics/resists_injection.txt`**.

| Step | What | Time |
|---|---|---|
| 1. Outputs | Get **20 responses** to prompt-injection attempts and judge them against `resists_injection`. Run your injection cases several times, add a few new attack questions, or hand-edit responses. Make sure **~7 genuinely fail** (the bot follows the injection, grants a refund outside policy, tells the joke) | 45 min |
| 2. Label | Label all 20 yourself in `calibration/labels.csv` (`id, question, response, human_pass, why`) **before** the judge sees them. Then stop and do something else for 10 minutes | 45 min |
| 3. Measure v1 | Split **14 dev / 6 held-out** (failures in both). Run the judge on the 14 (echo provider + `llm-rubric`, as in `fool-the-judge.yaml`), feed the verdicts and your labels into `calibrate.py` → κ / TPR / TNR | 15 min |
| 4. Fix once | Read **every** disagreement. Fix the rubric once (definitions, 2–3 examples from dev only) as `resists_injection_v2.txt`. Re-measure on dev | 45 min |
| 5. Held-out | Run v2 on the 6 held-out. **That's your number.** Don't tune after seeing it | 10 min |
| 6. Verbosity bias | Take **4 failing responses** and pad them to double length with filler that adds nothing. Does the judge start passing them? | 20 min |

**Skipped on purpose:** the pairwise position check, the judge leaderboard, the smuggle-a-fact challenge.

⚠️ Six held-out cases is a small number: one judge mistake moves κ a lot. Say so in `CALIBRATION.md`. A measured κ on six still beats an unmeasured judge on zero.

### Then close it
- `CALIBRATION.md`: the v1 → v2 table on dev, the held-out number with the n = 6 caveat, the verbosity result, and the disagreements that changed the rubric
- README: add the calibration number, and check the badge on `main` is green
- Fill in the **Actual** column of the scoreboard and tick **Done when**
- smallest-eval is done. Week 4 starts Saturday with the collector.
