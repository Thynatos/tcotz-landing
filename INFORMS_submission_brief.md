# INFORMS Undergraduate OR Prize 2026 — Submission Briefing
**Bilkent IE Team 21 · Nesco Gıda İçecek (BobaCo)**  
*Prepared for handoff to Claude Code — May 2026*

---

## 1. What We Are Doing

We are reformatting and strengthening a Bilkent IE senior capstone report to submit to the **INFORMS Undergraduate Operations Research Prize 2026**. The deadline is **June 30, 2026 at 11:59 pm Eastern time**.

This is an **applied industry project** (not a theoretical research paper). The INFORMS prize explicitly covers applied projects as a first-class track. Judging criteria for applied projects are:
1. Is the work significant?
2. Did it require clever OR methodology?
3. Did it create substantial, measurable value for the project sponsor?

Our project scores well on all three. The job now is to make the paper communicate that as clearly and compellingly as possible.

---

## 2. The Project — Full Summary

### Company
**Nesco Gıda İçecek**, Ankara, Turkey. Founder/Industrial Advisor: **Nazlı Esen Ummansu**.  
Brand in scope: **BobaCo** — Turkey's first industrial-scale bubble tea manufacturer. B2B model (HORECA: cafés, restaurants, hotels, beverage chains). Exports to 30+ countries. Certifications: VEGAN, ISO 9001, FDA.

### Problem
BobaCo faces **high seasonal summer demand** it cannot meet with real-time production alone. Previous facility had no storage — inventory build-ahead was impossible. New facility has adequate storage. Products have 12–18 month shelf life. The company planned semi-manually using market intuition and past experience.

**Core tension:** balance holding costs (build too much inventory) vs. backlog costs (miss demand). Backlogs beyond 12 days risk order cancellations.

### Products (4 items, 2 production lines)
- **Line 1:** Plastic Tub Boba (finished, sold directly) · Semi-Finished Boba in Tubs (intermediate input — consumed by Line 2 products)
- **Line 2:** Cup Bubble Tea · Can Bubble Tea (Cup and Can cannot be produced on the same day due to pasteurization constraints)

**Critical structural feature:** Semi-Finished Boba is both produced on Line 1 and consumed as a raw input for Line 2 products. This creates a multi-level bill-of-materials dependency.

Each line can process at most **one product type per day** (no mid-day switching).

### What We Built
A **Python + Streamlit decision support system** ("Weekly Planner") that runs automatically each Monday and outputs:
- Weekly recommended production quantities per product
- Raw material order decisions (with lead times up to 75 days, minimum order quantities enforced)
- Interactive charts, data tables, multi-sheet Excel exports
- Accompanied by a full user manual

### Mathematical Architecture (3-layer hierarchical approach)

#### Layer 1: Two-Stage Stochastic Long-Term Aggregate Model (monthly, full year)
- **First stage** (months 1–2): deterministic decisions made before uncertainty is revealed
- **Second stage** (months 3–12): scenario-dependent recourse decisions $(P_{i,t,\omega}, I_{i,t,\omega}, B_{i,t,\omega})$
- Minimizes **expected total cost** = holding + backlog across scenario set $\Omega$
- Scenario generation: uniform sampling within user-provided uncertainty bands $[f_t(1-s_t),\ f_t(1+s_t)]$, equal probabilities $p_k = 1/N$
- Literature grounding: Birge & Louveaux (2011) two-stage stochastic programming framework

#### Layer 2: MILP Short-Term Scheduling Model (daily, 8-week rolling horizon)
- Full MILP with binary machine-selection variables ($X_{m,j,t}$)
- Enforces: line-based product separation, pasteurization constraints, raw material lead times, minimum order quantities, storage area limits
- Includes a **12-day critical backlog penalty** ($B_{i,t}^{12}$) separate from regular backlog — targets the order cancellation threshold
- Receives **inventory targets** from the long-term model at days 24 and 48 as linking constraints ($d^D_{i,1}$, $d^D_{i,2}$)

#### Layer 3: Rolling Horizon Execution
- Both models run in a rolling-horizon manner — replanned weekly as new demand information arrives
- Near-term decisions are stabilized to prevent excessive fluctuations (following Sahin et al. 2013)
- Motivation: full-year daily exact model is computationally intractable (Scenario 9 exceeded 2,200 seconds in testing)

### Key Results

| Metric | Current System | Proposed System |
|--------|---------------|-----------------|
| Base-case overtime days | 11 | 0 |
| Base-case critical backlog volume | 380,709 units | 0 |
| Base-case overtime delivery rate | 6.01% | 0.00% |
| Avg. overtime days (10 scenarios) | 28.2 | 0.3 |
| Range of overtime days | 17–37 | 0–1 |
| Weighted backlog-at-risk ratio | 12.49% | 0.08% |
| Scenarios with zero backlog & zero overtime | 0/10 | 7/10 |

**Stochastic vs. deterministic (100-iteration VSS analysis):**
- Average RP objective: 4,454,400
- Average EEV objective: 41,626,235
- Average VSS: 37,171,834 (80.48% of EEV)
- VSS was non-negative in all 100 iterations → stochastic approach strictly dominates

**Rolling-horizon cost comparison:**

| | Stochastic | Deterministic | Difference |
|--|--|--|--|
| Avg. holding cost | 5,634,045 | 2,901,458 | +2,732,587 |
| Avg. backlog cost | 48,057,008 | 89,656,018 | −41,599,010 |
| Avg. total cost | 53,691,052 | 92,557,476 | **−42% reduction** |

### Pilot Study
- **4-week live pilot** integrated into the company's real weekly planning process
- Week 1: supervised by project team; Weeks 2–4: run independently by the company
- Weekly decisions reviewed every Monday, finalized and documented
- Company confirmed decisions were feasible, understandable, and aligned with build-ahead goals
- Pilot did not coincide with peak season but validated the operational workflow

### Literature Positioned Against
- Nahmias (2015) — aggregate production planning, deterministic inventory control
- Karimi et al. (2003) — CLSP variants, NP-hardness motivation for heuristic
- Maes et al. (1991) — MLCLSP with bill-of-materials (our system fits this family)
- Pochet & Wolsey (1988) — backlogging in lot-sizing
- Bitran & Hax (1982) — hierarchical production planning formalization
- Liberatore & Miller (1985) — HPP implemented in industry (American Olean Tile)
- Sahin et al. (2013) — rolling-horizon schemes in supply chains
- Birge & Louveaux (2011) — two-stage stochastic programming framework

---

## 3. The Team

**7 student authors (all first authors, all Bilkent IE seniors, Spring 2026):**
- Bahadır Maral
- Berke Kemahlı
- Deniz Yaşar
- Derin Aktürk
- Kenan Arda Köymen
- Melike Karalar
- Osmantan Beşikci

**Academic Advisor:** Assoc. Prof. Özlem Çavuş İyigün, Bilkent University, Department of Industrial Engineering  
**Industrial Advisor:** Nazlı Esen Ummansu, Founder, Nesco Gıda İçecek

**Other context:**
- This is a Bilkent IE senior capstone project (course: `buIE47x`)
- The project was also submitted to/presented at **YAEM 2026** (Turkish national OR/IE conference) — independent external validation

---

## 4. Current Status

| Step | Status |
|------|--------|
| Step 1: Email Prof. Çavuş İyigün for reference letter | ✅ Done |
| Step 2: Decide base document (YAEM paper vs. course report) | Pending |
| Step 3: Reformat to INFORMS specs | **In progress — this is the main task** |
| Step 4: Confirm no co-authorship conflicts | Pending |
| Step 5: Submit via INFORMS portal by June 30 | Pending |

---

## 5. INFORMS Formatting Requirements (Hard Rules)

These are non-negotiable. The submission will be disqualified if violated.

| Requirement | Spec |
|-------------|------|
| Spacing | Double-spaced throughout |
| Font size | 11pt minimum |
| Margins | 1 inch on all four sides (left, right, top, bottom) |
| Page limit | **25 pages maximum** — including title, abstract, bibliography, appendices, figures, everything |
| Lines per page | Max 35 lines of text per page (except reference pages) |
| Paper size | Standard US letter (A4 will NOT be accepted) |
| Abstract | Standalone, ≤ 100 words, attached to paper |
| Authorship | At least one student as first author |
| Reference letter | Separate document, ≤ 2 pages, submitted alongside paper |

**Current file:** `report.tex` uses Bilkent's custom `buIE47x` document class — this must be replaced entirely with `\documentclass[11pt]{article}` plus standard packages.

---

## 6. What Needs to Change in the Paper

### 6a. Structural changes (required for compliance)

1. **Replace document class** — swap `buIE47x` for `article` with `geometry` (1-inch margins) and `setspace` (`\doublespacing`)
2. **Remove the appendix** — the 6 UI screenshots (Figures: UI input field, UI manual, Excel input template, workday config panel, file upload panel, file format help) consume ~3 pages and add nothing to the OR contribution. Drop the entire appendix.
3. **Rebuild title block** — use standard `\maketitle` with all 7 authors, advisor, industrial advisor, date omitted
4. **Standalone abstract** — must be ≤ 100 words. Current abstract is ~60 words but written informally for the course. Needs to be sharpened to lead with the OR contribution and quantified results.
5. **Page budget check** — with double spacing, the paper will expand significantly. Target sections for trimming: Section 1 (Company Information, ~2 pages, can be condensed to ~0.5 pages), redundant constraint explanation prose (some constraints explained twice), the TeaCo paragraph in Section 1 (irrelevant to the project).

### 6b. Content changes (for competitiveness)

These changes are about winning, not just compliance.

**Framing shift — lead with impact, not process:**
- Current opening: describes the company. INFORMS judges read dozens of papers. Open with the problem and the stakes: seasonal demand, new facility, opportunity to build-ahead, what it costs the company when they get it wrong.
- Do NOT use the phrase "course project" anywhere. This is an industry engagement with a live company.

**Abstract rewrite:**
- Current abstract doesn't mention the OR methods used or the quantified results. Winning abstracts say what methods were used AND what measurable impact they achieved. The 42% cost reduction and 28.2→0.3 overtime days should be in the abstract.

**Section 2 (System Analysis) — add a crisp problem statement paragraph:**
- Before the mathematical model, add a short paragraph explicitly stating: "The problem belongs to the MLCLSP family..." and framing why a monolithic exact approach is intractable, motivating the hierarchical heuristic. This tells judges you know where your work sits in the literature.

**Section 3 (Literature Review) — tighten:**
- Currently very thorough but slightly long. Each paragraph should end with a one-sentence bridge to your system: "This motivates our use of X in the long-term model." Make the literature do work for the reader, not just demonstrate knowledge.

**Model sections — unify notation:**
- Sets $K_1$, $K_2$, $T$, $S$ are re-defined in every sub-model section. Define them once in a shared notation table at the start of Section 4 and reference back. This saves ~1 page.

**Verification section — add a summary table:**
- Currently the verification results are described in prose. Add a compact summary table: columns = scenario, runtime (exact), runtime (heuristic), objective deviation %, 10-day backlog deviation. Makes the computational case for the heuristic visually clear.

**Conclusion — add a forward-looking sentence on generalizability:**
- INFORMS judges reward work that has broader OR significance beyond one company. Add 1–2 sentences: the hierarchical stochastic approach is directly applicable to any SME facing seasonal demand with long-horizon procurement lead times and a recently expanded storage capacity. This frames the contribution as generalizable.

---

## 7. Suggested Paper Structure (Target: ≤ 25 pages)

| Section | Suggested pages |
|---------|----------------|
| Title + Abstract (≤100 words) | 0.5 |
| 1. Introduction & Problem Motivation | 1.0 |
| 2. Company & System Description | 1.0 |
| 3. Literature Review | 1.5 |
| 4. Proposed Solution Architecture | 0.5 |
| 5. Mathematical Models (short-term MILP + long-term stochastic) | 5.0 |
| 6. Scenario Generation | 0.5 |
| 7. Heuristic Solution Approach (rolling horizon) | 1.0 |
| 8. Verification (short-term, heuristic, stochastic VSS) | 2.5 |
| 9. Validation | 1.0 |
| 10. Decision Support System & Pilot Study | 1.5 |
| 11. Benchmarking Results | 1.5 |
| 12. Conclusion & Future Work | 1.0 |
| References | 1.5 |
| **Total** | **~20 pages** |

This leaves ~5 pages of buffer for figures (keep: Figure 1 production flow, Figure 2 hierarchical models, Figure 3 heuristic vs. exact comparison, Figure 4 production vs. demand yearly chart, Figure 5 UI + weekly schedule). Drop all 6 appendix UI detail figures.

---

## 8. Figures to Keep vs. Drop

| Figure | File | Decision | Reason |
|--------|------|----------|--------|
| Production workflow (popping boba) | `figures/FCNew.png` | ✅ Keep | Explains the system structure clearly |
| Hierarchical models diagram | `figures/Hierarchical_models.png` | ✅ Keep | Core architectural diagram |
| Heuristic vs. exact comparison | `figures/fig5.jpg` | ✅ Keep | Validates the need for the heuristic |
| Production & demand yearly chart | `figures/prodem.png` | ✅ Keep | Shows validation behavior |
| UI + weekly schedule output | `figures/Ui_and_Wschedule.png` | ✅ Keep (1 figure only) | Shows deliverable; keep the combined one |
| UI input field | `figures/UI.png` | ❌ Drop (appendix) | Judges don't need UI detail |
| UI manual | `figures/UIMAN.png` | ❌ Drop (appendix) | Judges don't need UI detail |
| Excel input template | `figures/input.png` | ❌ Drop (appendix) | Judges don't need UI detail |
| Workday config panel | `figures/workdays.png` | ❌ Drop (appendix) | Judges don't need UI detail |
| File upload panel | `figures/file upload.png` | ❌ Drop (appendix) | Judges don't need UI detail |
| File format help | `figures/file format help.png` | ❌ Drop (appendix) | Judges don't need UI detail |

---

## 9. Key Files

| File | Location | Notes |
|------|----------|-------|
| Original course report | `/mnt/user-data/uploads/report.tex` | Source of truth for all content — do NOT edit directly |
| Reformatted INFORMS `.tex` (v1 draft) | `/mnt/user-data/outputs/report_INFORMS.tex` | First reformat pass already completed — use as starting point |
| Bibliography | `report.bib` | Must be in same directory as `.tex` when compiling |
| Figures | `figures/` directory | Must be alongside `.tex` when compiling |

---

## 10. Submission Checklist

- [ ] Document class: `\documentclass[11pt]{article}` with `geometry` (1in margins) and `setspace` (`\doublespacing`)
- [ ] Paper size: US Letter (not A4)
- [ ] Font: 11pt or larger throughout
- [ ] Page count: ≤ 25 pages (including everything)
- [ ] Lines per page: ≤ 35 (except reference pages)
- [ ] Standalone abstract: ≤ 100 words, attached to paper
- [ ] Abstract mentions OR methods AND quantified results
- [ ] Appendix UI figures: removed entirely
- [ ] Shared notation table: sets/parameters defined once, not repeated per sub-model
- [ ] No phrase "course project" anywhere in the paper
- [ ] Company and problem introduced before methods
- [ ] VSS table included
- [ ] Benchmarking results table included
- [ ] Pilot study described (4-week live deployment)
- [ ] Conclusion includes generalizability statement
- [ ] Reference letter from Prof. Çavuş İyigün: ≤ 2 pages, confirms undergraduate enrollment, describes individual contributions, mentions YAEM acceptance
- [ ] All 7 authors confirmed: none is co-author on a separate INFORMS undergrad prize submission this year
- [ ] Submitted via INFORMS online portal before June 30, 2026 at 11:59 pm ET

---

## 11. Useful Links

| Page | URL |
|------|-----|
| Prize overview | https://www.informs.org/Recognizing-Excellence/INFORMS-Prizes/Undergraduate-Operations-Research-Prize |
| Application process & submission portal | https://www.informs.org/Recognizing-Excellence/INFORMS-Prizes/Undergraduate-Operations-Research-Prize/Undergraduate-Operations-Research-Prize-Application-Process |
| 2026 Annual Meeting (San Francisco, Nov 1–4) | https://meetings.informs.org/wordpress/annual/ |
| All INFORMS prizes | https://www.informs.org/Recognizing-Excellence/INFORMS-Prizes |
