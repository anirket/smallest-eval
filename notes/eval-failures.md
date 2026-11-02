# Eval failures from past ships

Raw material for the essay, written later. 3 lines each: what happened, how I found it, what eval would have caught it earlier.

## Week 1, jd-lens: the eval was wrong, not the model
- **What happened:** the first must-haves matcher scored recall at 0.60 while the model's extractions were fine. Substring matching missed `2–6` vs `2-6` and reworded sentences.
- **How I found it:** the number looked too low, so I checked one case by hand and the "misses" were real matches.
- **What would have caught it earlier:** testing the checker itself on a few hand-labelled pairs (known match / known miss) before trusting its score. Same idea as calibrating a judge: measure the grader before you measure the model.

## Week 2, mini-agent: 20/20 hid the path
- **What happened:** the eval passed 20/20, but Haiku skipped `calculate` on easy maths (calc_03 and 3 of 4 multi tasks did the maths in its head). Answers were right; "uses the tool" wasn't.
- **How I found it:** reading the "tools called" column of the results table, not the pass count.
- **What would have caught it earlier:** a check on the trajectory, not just the final answer: "calc tasks must call `calculate`". This becomes a real `python` assert on Day 5, Phase 2.

## Backup candidates
- **jd-lens:** bullets-only input gave 3/12 matches vs 9/12 with the full resume. Looked like a model problem, was a prompt problem.
- **mini-agent:** Sonnet's one "failure" on adv_02 was a correct refusal (`stop_reason: refusal`, empty answer). The checker was too strict, so 19/20 was really 20/20.
