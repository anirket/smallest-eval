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

**The part that makes it worth talking about: calibrating the judge.** A judge is a model too, so it can be wrong. You hand-label 30 outputs yourself, run the judge on the same 30, and measure how often it agrees with you (agreement %, Cohen's kappa, TPR/TNR). Then you rewrite the judge's rubric until it tracks you, and test it for two known biases: favouring longer answers, and favouring whichever option is shown first. The end result is a sentence most people can't say: *"my judge agrees with me at κ = 0.7 on 10 held-out cases, here's where it's wrong, and here's the bias I measured."*

**The second part: version the agent, not just the prompt.** The agent config has a `version` field. On every PR, the Action runs the eval against the PR's version and against the previous one (`main`), and prints the delta: pass rate, cases that flipped, ₹ and p95 latency. That turns "evals in CI" into "regression-tested agent versions": a prompt change shows up as a number on the PR before it merges.

**What you end up with:**
- **`smallest-eval`**: a GitHub template repo with a tiny example app. A stranger clicks "Use this template", swaps in their own app and cases, and has evals in CI.
- **The same harness fitted onto** ship #1 (`jd-lens`) and ship #2 (`mini-agent`), so 3 repos carry a green eval badge
- **Version-to-version delta** on every PR: current vs previous agent version, printed in the PR summary
- **`CALIBRATION.md`**: your judge-vs-human number and the bias results

**Done when:**
- [ ] `anirket/smallest-eval` is a template repo, and a stranger can clone it and get a green run by following the README
- [ ] 3 repos show a green eval badge: `smallest-eval`, `jd-lens`, `mini-agent`
- [ ] A PR on `smallest-eval` prints the delta between the current and previous agent version (pass rate, flipped cases, ₹, p95)
- [ ] `CALIBRATION.md` has a judge-vs-you number (agreement + Cohen's kappa + TPR/TNR on a held-out set) and the two bias checks

**5 days, Nov 1 → Nov 5:** Day 1–2 learn (watch + hands-on), Day 3–5 build.
**Nov 6 is the backup day.** It's for spillover only. Nothing is planned onto it.

---

## Scoreboard (fill in as you go)

| | Your guess | Actual |
|---|---|---|
| κ of judge v1 (Haiku) on dev | *write it on Day 2* | |
| κ of the final judge on held-out | | |
| Rubric versions it took | | |
| % of times the pairwise judge picks option A | | |
| Padded fails the judge started passing (out of 5) | | |
| Sneaky rewrites that fooled the final judge (out of 3) | | |
| ₹ per CI run (template) | | |
| ₹ spent on the whole project | | |
| Badges green | | /3 |
| Pass-rate delta on a deliberate regression (previous vs current version) | | |

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
| What gets calibrated | **jd-lens tailored bullets**: "does the rewrite add any fact not in the source bullet?" | Your README already says *"Read the rewrites by hand"*. That's a real, unsolved gap, not a toy |
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
| 4 (Nov 4) | **Judge on trial** | Your judge measured against you, tuned, and stress-tested for bias |
| 5 (Nov 5) | **The 20/20 lie** | jd-lens and mini-agent on green badges, a PR showing the version delta |
| Nov 6 (backup) | **Spillover** | Only what didn't finish Days 1–5, in the order listed under the backup section |

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

### Phase 1: Watch: judges and calibration · ~45 min
1. **Evidently AI, Create an LLM Judge and Align It with Human Labels**: https://www.youtube.com/watch?v=kP_aaFnXLmY (24 min). Watch closely from 10:00: v1 prompt → 64% accuracy, 100% precision but 36% recall → read the misses → v2 prompt → 95%. Copy that loop.
2. **Siddhardhan, LLM as a Judge Explained, Hands-On**: https://www.youtube.com/watch?v=3FcYdRQPMCo&t=1080s, **from 18:00** (~13 min at 1.5×; the first 18 min are setup). Pairwise judge, JSON `{winner, reason}`. That's the setup where position bias shows up.

### Phase 2: Read · ~1 hr
- Hamel, **Using LLM-as-a-Judge: A Complete Guide**: https://hamel.dev/blog/posts/llm-judge/ (critique shadowing)
- oneuptime, **How to Calibrate an LLM-as-a-Judge Against Human Labels with Cohen's Kappa**: https://oneuptime.com/blog/post/2026-08-31-calibrate-llm-judge-cohens-kappa/view (read before writing `calibrate.py`). Read kappa next to the confusion matrix, not on its own.
- Eugene Yan, **Evaluating the Effectiveness of LLM-Evaluators**: https://eugeneyan.com/writing/llm-evaluators/ (only the position and verbosity sections; the bias checks on Day 4 use them)
- Hamel, **Your AI Product Needs Evals**: https://hamel.dev/blog/posts/evals/ (the canonical version of your essay; read it so you don't repeat it)

### Phase 3: Hands-on: the maths you'll present · ~1 hr
Write `calibrate.py` now, on fake data, so Day 4 is just running it:

```python
def cohen_kappa(human, judge):                  # lists of bools, True = pass
    n = len(human)
    p_o = sum(h == j for h, j in zip(human, judge)) / n
    ph, pj = sum(human) / n, sum(judge) / n
    p_e = ph * pj + (1 - ph) * (1 - pj)          # agreement you'd get by chance
    return (p_o - p_e) / (1 - p_e)
```

- Also compute **TPR** (judge passes what you passed) and **TNR** (judge fails what you failed), and print a 2×2 confusion table
- ⚠️ **Why kappa and not just agreement:** if 27 of 30 outputs pass, a judge that always says "pass" gets 90% agreement and **κ = 0**. Test exactly this case on your fake data. It's a good line for the essay.

### Phase 4: Pick the essay evidence · ~30 min
Candidates from your own READMEs:
- **Week 1 (jd-lens):** the eval was wrong, not the model. The substring matcher scored recall at **0.60** when the model was fine (`2–6` vs `2-6`, rewording). Also: bullets-only input gave 3/12 matches vs 9/12 with the full resume, which *looked* like a model problem and was a prompt problem.
- **Week 2 (mini-agent):** 20/20 passed, but **Haiku skipped `calculate`** on easy maths. Output-only checks can't see the path. And Sonnet quietly did steps 3–4 in its head after the step limit, where Haiku said they were missing.

Pick one from each week. Write 3 lines each: what happened, how you found it, what eval would have caught it earlier.

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

## Day 4 (Nov 4): Judge on trial · ~5.5 hrs (the big one)

**Mission:** put your judge in the witness box. Measure it against you, fix it, then attack it until you know exactly where it breaks.

**Done when:** `CALIBRATION.md` shows judge versions v1→vN with κ/TPR/TNR on dev, the final number on a held-out set, and both bias checks.

### Phase 1: 30 outputs · ~1 hr
- Run jd-lens to produce 30 **tailored bullets** (each next to its source bullet)
- The criterion, binary: **"The rewrite adds no fact, number, tool or claim that isn't in the source bullet."**
- ⚠️ You need failures in the set (aim for ~⅓). If Haiku is too clean, produce some with `gpt-oss-20b` or a sloppier prompt. A set of all passes makes κ meaningless (see Day 2, Phase 3).

### Phase 2: Label blind · ~1 hr
- `labels.csv`: `id, source, rewrite, human_pass, why`. **Label before the judge ever sees them.**
- Split **20 dev / 10 held-out**. Tune only on dev. (Hamel's point: with a tiny set, you'll overfit to whatever you iterate on.)
- Take a break after labelling, before you run the judge, so you aren't tempted to "fix" your labels to match it.

### Phase 3: Iterate the rubric · ~2 hrs
- Keep the Evidently tutorial open from 10:00 as the loop to copy: https://www.youtube.com/watch?v=kP_aaFnXLmY&t=600s
- v1: a plain rubric → run on dev → κ, TPR, TNR, confusion table. **Compare with your scoreboard guess.**
- Read **every** disagreement. Fix by adding definitions and 2–3 examples taken from dev (not held-out)
- Log each version in a table: `version | change | agreement | κ | TPR | TNR | ₹`
- Run the final rubric on the 10 held-out → **that's your headline number**
- **Judge leaderboard:** run the final rubric with Haiku, Sonnet and Opus as the judge, then pick one on κ vs ₹. Is the expensive judge worth it?
- Target: κ ≥ 0.6 on held-out. If you don't reach it, report what you got and why. An honest 0.5 with analysis beats a suspicious 1.0.

### Phase 4: The two biases · ~1 hr
- **Verbosity:** take ~5 *failing* rewrites and pad them to ~2× length with neutral wording that adds no facts. Does the judge start passing them? Also compare output length against judge pass rate across the 30.
- **Position:** pairwise judge ("which rewrite is more faithful, A or B?") on 10 pairs, **both orders**. Report the % of times A wins and the number of flipped verdicts.
- Write what you do about it: CI uses the pointwise binary judge; pairwise only with both orders.

### 🔥 Challenge: smuggle a fake fact · ~20 min
Your judge is tuned now. Try to beat it. Write 3 rewrites that sneak in an invented fact the way a real model would: a plausible metric ("cut load time **by 40%**"), a tool that sounds right ("using **Redis**"), a scope inflation ("**led** the migration" when the source says "worked on"). How many get past your final judge? Put the score on the scoreboard and the misses in `CALIBRATION.md` under "Known blind spots". Knowing where your judge is blind is worth more than a high κ.

---

## Day 5 (Nov 5): The 20/20 lie · ~7.5 hrs (heaviest day)

**Mission:** put the judge and the gate on the two real ships, and make CI compare agent versions. Catch your own past self: mini-agent scored 20/20, and today a new test shows what that score was hiding.

**Done when:** `jd-lens` and `mini-agent` both carry green badges (3/3 with `smallest-eval`), a PR on `smallest-eval` prints the delta between the current and previous agent version, and a fresh clone of the template runs green by following its README alone.

**Load warning:** this day is ~7.5 hrs. The stranger test and wrap-up (Phases 4–5) are the parts to move to Nov 6 if the day runs long.

### Phase 1: Retrofit jd-lens · ~1.5 hrs
- Copy the template's `promptfooconfig.yaml`, workflow and `report.py`
- 10 cases from `evals/cases/`. Assertions: schema valid, every quote is really in the resume (your existing `find_fakes`, as a `python` assert), and **the calibrated judge on tailored bullets**
- Secret, badge, green run. **Badge 2/3.**

### Phase 2: Retrofit mini-agent · ~1.5 hrs
- Provider = `run_agent(task)` returning the final answer, plus the tools called, steps and ₹
- 10 of the 20 tasks; reuse the checkers (`number` with tolerance → `python` assert, `contains`)
- Add the check your 20/20 hid: **"used `calculate` for calc tasks"** (a `python` assert on the tool list). **Watch it go red on Haiku.** That's the essay's week-2 evidence turning into a test, live.
- Then decide: fix it (say "always use the calculator" in the system prompt) and watch it go green, or keep the test as a documented known failure. Either is a good story; pick one and say why.
- `cost` and `latency` assertions from your existing thresholds (avg ₹ ≤ 0.50)
- **Badge 3/3.**

### Phase 3: Version the agent · ~3 hrs
- Add a `version` field to `app/agent.yaml` next to the model and prompt. Bump it whenever the prompt or model changes.
- In the Action, run the eval twice: once on the PR's agent config (current) and once on the `main` copy (previous). Use a second `actions/checkout` with `ref: main` into its own folder.
- `report.py --baseline` takes the previous `results.json` and prints a delta table: pass rate, cases that flipped pass→fail or fail→pass, ₹ and p95 latency change.
- ⚠️ The judge isn't deterministic. Run the baseline twice on an unchanged PR to measure the noise floor. A delta smaller than that noise isn't a regression, and the report should say so.
- Test it on purpose: reuse the sabotage change with a version bump and watch the delta show the flipped cases. Then open a PR with no prompt change and check the delta is near zero.
- ⚠️ Fork PRs still get no secrets, so the delta step fails there too. Covered by the README note from Day 3.

### Phase 4: Stranger test · ~1 hr
- `gh repo create test-clone --template anirket/smallest-eval`, clone it into a fresh folder, and follow the README **only**
- Every step where you needed knowledge that isn't in the README → fix the README
- Even better: hand the link to a friend and time them. Their first question is your README's biggest gap.
- Then delete the test repo

### Phase 5: Wrap · ~30 min
- Fill in the **Actual** column of the scoreboard and tick the **Done when** list at the top
- Record the sabotage PR's delta on the scoreboard, with the noise floor next to it
- One `runs.jsonl`-style line per day in the README: what it cost to build the whole thing

---

## Nov 6 (backup): Spillover only · ~0–4 hrs

Nothing is planned here. Use it only if Days 1–5 ran over. Pick up unfinished work in this order:

1. **Stranger test** (Day 5, Phase 4)
2. **Wrap** (Day 5, Phase 5: scoreboard Actual column, Done-when ticks, `runs.jsonl` line)
3. Anything left from Days 3–4 (badge, template settings, judge leaderboard)

If the 3/3 badge slips past Nov 6, say so in the README rather than shipping an unmarked gap.
