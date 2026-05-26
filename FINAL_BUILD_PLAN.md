# Final Build Plan — INFORMS 2026 Submission

Produce an INFORMS Undergraduate OR Prize 2026 submission-ready PDF from the BobaCo capstone repository. The literature review, methodology framing, citation strategy, and bibliography work are already complete (commits 13bcb9b, 061b9e3, 93a4c7e). This plan covers the remaining formatting, structural, and verification work. **Deadline: June 30, 2026 at 11:59 pm ET.**

---

## Context and Authoritative Guides

Read these first — they contain the strategy and constraints to follow:

1. `INFORMS_submission_brief.md` — full project briefing, formatting rules, structural change guidance, submission checklist
2. `LITREVIEW_PLAN.md` — citation strategy (already executed in commits) and Section 7 action list
3. `memory/MEMORY.md` — user profile, citation quality standards, project state

**Key files:**
- `TCOTZ_21/report.tex` — source LaTeX (currently uses `buIE47x` class — must convert)
- `TCOTZ_21/report.bib` — bibliography (already cleaned, 12 new top-tier citations added)
- `TCOTZ_21/figures/` — keep 5 figures, drop 6 appendix UI figures

---

## Hard Constraints (Non-Negotiable)

- Page limit: **≤25 pages** total (title, abstract, body, refs, appendix — everything)
- **Double-spaced** throughout
- **11pt** minimum font
- **1-inch margins** on all four sides
- **US Letter** paper size (NOT A4)
- ≤35 lines of text per page (except reference pages)
- Standalone abstract **≤100 words**, attached to paper
- At least one student listed as first author
- No phrase "course project" anywhere in the paper

---

## Phase 1 — Format Compliance (mechanical, do first)

### 1.1 Replace document class in `report.tex`

- Current: `\documentclass[fleqn]{buIE47x}`
- Target: `\documentclass[11pt]{article}`
- Add packages: `geometry` (margin=1in), `setspace` (`\doublespacing`), `graphicx`, `amsmath`, `amssymb`, `booktabs`, `hyperref`, `natbib`, `caption`
- Rebuild `\maketitle` block with all 7 author names from team list, both advisors. Project name becomes the paper title.
- Remove all `buIE47x`-specific commands (`\projectname`, `\company`, `\teamno`, `\projectshortcode`, `\teammembers`, `\IA`, `\AA`, `\bibfilename`)
- Use `\bibliographystyle{plainnat}` and `\bibliography{report}`
- Paper size: `\usepackage[letterpaper, margin=1in]{geometry}`

### 1.2 Drop 6 appendix UI figures

Drop any `\section{Appendix}` containing only UI figures. Keep these 5 figures:

- `figures/FCNew.png` (production workflow)
- `figures/Hierarchical_models.png`
- `figures/fig5.jpg` (heuristic vs exact comparison)
- `figures/prodem.png` (production vs demand)
- `figures/Ui_and_Wschedule.png` (combined UI + weekly schedule)

### 1.3 Compile and verify

Run `pdflatex` + `bibtex` + `pdflatex` + `pdflatex`. Verify:
- No undefined citation warnings (all 24+ cite keys resolve)
- No undefined reference warnings
- Page count is measurable

**Stop and report findings before continuing to Phase 2.**

---

## Phase 2 — Content Polish (writing)

### 2.1 Rewrite the abstract

Current abstract is generic and does not mention OR methods or quantified results. Target **≤100 words**, mentioning ALL of:
- Two-stage stochastic programming
- Hierarchical decomposition
- Rolling horizon
- 42% cost reduction
- Average overtime reduction (28.2 → 0.3 days)
- VSS dominance in 100/100 iterations
- Deployed at industrial scale

### 2.2 Unify the notation table

Sets $K_1$, $K_2$, $T$, $S$ are defined redundantly in each sub-model section. Consolidate into one "Sets, Parameters, and Decision Variables" table at the top of Section 4. Each sub-model then says "Using the notation from Table X..." Saves ~1 page.

### 2.3 Add computational evidence table

Convert the prose justification for the heuristic into a compact table with columns: **Scenario | Exact solver runtime (s) | Heuristic runtime (s) | Objective deviation (%) | Critical backlog deviation**.

Source data may be in `TCOTZ_21/` — check for CSV outputs, model run logs, or run scripts to regenerate if needed. **If no data exists, report the gap rather than fabricating numbers.**

### 2.4 Add generalizability sentence to conclusion

Suggested text:
> "The hierarchical stochastic rolling-horizon approach developed here is directly applicable to any SME facing seasonal demand with long-horizon procurement lead times and recently expanded storage capacity, particularly in food and beverage manufacturing where multi-level BOM dependencies and synchronized line constraints are common."

### 2.5 Remove "course project" language

Search and remove every occurrence of: `course project`, `capstone`, `Bilkent IE 47x`, `buIE47x` in body text. This is an industry engagement paper, not a course deliverable.

### 2.6 Compress Section 1 (Company Information)

Current version is ~2 pages of company history. Compress to **≤0.5 pages** focused on what matters for the OR contribution: B2B model, 4 products, 2 lines, new facility with storage capacity. **Drop the TeaCo paragraph entirely** — it's irrelevant.

---

## Phase 3 — Page Budget Enforcement

### 3.1 Compile and measure

Target ≤22 pages to leave a 3-page safety buffer.

### 3.2 If over 25 pages, trim in this order:

1. Section 1 (Company Information) — compress further
2. Constraint explanation prose where constraints are explained twice (long-term and short-term sections)
3. Verification sub-sections — keep tables, trim prose
4. Detailed scenario-by-scenario narration

**DO NOT trim:**
- Literature review (already lean at 11 paragraphs)
- Mathematical model formulations
- VSS analysis table
- Benchmarking results table
- Pilot study description

### 3.3 Iterate

Recompile and re-measure. Iterate until within budget.

---

## Phase 4 — Submission Verification

### 4.1 Submission checklist

Run through the submission checklist in `INFORMS_submission_brief.md` Section 10. Report each item as ✅ Pass / ❌ Fail / ⚠️ Manual check.

### 4.2 Visual verification

Open the compiled PDF and verify:
- Title block is clean (no buIE47x artifacts)
- All 7 authors listed, first author is a student
- Abstract is on the first page, ≤100 words
- No figure overflow, no broken references
- Bibliography renders with proper formatting
- Line count per page ≤35 (except references)

### 4.3 Final delivery summary

Report: page count, citation count by journal tier, hard-constraint compliance status, any remaining manual TODOs for the human team.

---

## Authorizations

**You ARE authorized to:**
- Edit `report.tex` and `report.bib` freely (these are tracked in git)
- Compile LaTeX repeatedly until it builds cleanly
- Run Python scripts in `TCOTZ_21/` to regenerate result tables if data is missing (check for existing solver outputs first; only re-run if necessary, document what you ran)
- Commit changes incrementally with clear messages
- Drop figures, sections, and prose to meet page budget
- Use scite MCP if available to verify any new citation you might add

**You are NOT authorized to:**
- Add new citations beyond those already in `report.bib` without scite-verification (user explicitly rejected weak journals)
- Change the architectural novelty claim or problem classification — settled in three independent deep research runs
- Push to remote or open PRs without explicit human approval
- Fabricate computational results — if data is missing, flag it
- Skip pre-commit hooks or amend published commits

---

## Deliverable

A compiled PDF at `TCOTZ_21/report.pdf` that satisfies every item in the INFORMS submission checklist, plus a written summary of:
- Final page count
- Compile-clean status
- Checklist pass/fail per item
- Any manual decisions left for the human team

---

## Writing Style

- Academic but not stilted. INFORMS judges are OR faculty, not English professors. Clarity > formality.
- Lead with impact, not process. Open sections with the result or decision, then explain how.
- Be specific. "42% cost reduction" not "significant savings". "100/100 iterations" not "consistently". "2,200 seconds" not "intractable".
- Use first person plural ("we") consistently.
- No marketing language about the company. This is an OR paper.

---

## Execution Protocol

1. Begin by reading the three context files (`INFORMS_submission_brief.md`, `LITREVIEW_PLAN.md`, `memory/MEMORY.md`)
2. Propose your Phase 1 approach before executing
3. **Stop after each phase to report progress** before proceeding to the next
