# Revision Task: Calibrate the INFORMS Jury Prompt Against Past Winners

> Feed this to the agent that already researched past INFORMS Undergraduate OR Prize winners. The agent's job is to revise `INFORMS_JURY_REVIEW_PROMPT.md` so the judge it produces evaluates papers against the actual bar set by past winners, not against generic OR/MS criteria.

---

You previously researched past winners and honorable mentions of the INFORMS Undergraduate Operations Research Prize. Use that knowledge to revise the judge prompt below so that the judge it produces evaluates papers against the actual bar set by past winners, not against generic OR/MS criteria.

## What to add to the judge prompt

The current prompt tells the judge to score on Significance, OR methodology, and Measurable value. That's correct but uncalibrated. From your prior research, add the following calibration layers:

1. **Winning-paper anatomy** — A short section describing what past winners typically have: depth of deployment (pilot vs. production), magnitude of quantified impact (typical ranges), methodology novelty markers, paper-craft signals (notation discipline, computational evidence tables, generalizability framing). Name specific past winners and their projects as benchmarks where useful.

2. **Honorable mention vs. winner distinction** — What separates the tier-1 (winning) papers from tier-2 (honorable mention) papers in past years? This is the most useful calibration — most submissions look "good" but only the top one wins. The judge should be able to identify which tier a paper falls into.

3. **Common loss patterns** — Recurring weaknesses you saw in non-winning papers from past cohorts. Things like: overstated novelty, missing canonical citations, simulated rather than deployed pilots, vague impact claims, methodology that any competent undergraduate could replicate with off-the-shelf solvers.

4. **Domain calibration** — If past winners cluster in certain domains (healthcare scheduling, transportation, energy, manufacturing, etc.), note that. Production planning at a small manufacturer is a competitive but not unusual domain; how have past production-planning papers fared?

5. **Stretch markers** — Things that pushed papers from "winning candidate" to "actual winner." Examples might include: a published companion paper, a system still in use at the sponsor years later, a methodology that became a citation in the literature, broad media coverage, etc.

## How to revise

- Preserve the existing structure (persona, criteria, scrutiny checklist, deliverable format, tone)
- Add calibration as new sections — do not delete what's there unless it directly conflicts with what past winners actually look like
- Be concrete with examples from your research. "Past winners typically reported impact in the X–Y range" is more useful than "winners report large impact"
- If your research contradicts something in the existing prompt, flag the conflict and propose a resolution rather than silently overwriting
- Keep the anti-sycophancy clause at the end

## Existing judge prompt to revise

The full prompt is in `C:\Users\badir\Documents\TCOTZ\INFORMS_JURY_REVIEW_PROMPT.md`. Read that file in full before revising. Do not work from memory or summary.

## Output

Return the revised judge prompt, complete and ready to copy-paste into a new agent session. Write the revised version to `INFORMS_JURY_REVIEW_PROMPT.md` (overwriting the current file). In the same response, also produce a short change log indicating with markers (e.g., "ADDED:" or "REVISED:") which sections are new or changed, so the user can review your edits.

Do not paraphrase your past research findings into the body of the prompt — instead, encode them as concrete checklist items the judge should apply when reviewing the BobaCo paper. The judge does not need to know your sources; it needs to know what to look for.
