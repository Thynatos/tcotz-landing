# Literature Review Strengthening Plan — INFORMS 2026

## Current State (Gaps)

Your report cites **8 papers** but the methodology touches **10+ OR subfields**, several lacking proper literature grounding:

| OR Method Used | Cited? | Gap |
|---|---|---|
| MLCLSP with BOM | Karimi 2003, Maes 1991 | Both are old surveys. No recent food-industry MLCLSP paper. |
| Hierarchical Production Planning | Bitran & Hax 1982, Liberatore & Miller 1985 | Good, but no integration/slack management citation |
| Rolling Horizon | Sahin et al. 2013 | One paper is fine |
| Two-stage stochastic prog. | Birge & Louveaux 2011 | Standard text, good |
| **VSS methodology** | **None** | You computed VSS but never cited where it comes from |
| **Scenario generation** | **None** | No paper backing your uniform sampling approach |
| **12-day critical backlog penalty** | **None** | Novel modeling — needs justification from literature |
| **Machine-selection binary formulation** | **None** | Common in MILP but no citation |
| **Food/beverage industry application** | **None** | Helps to show this is an active OR domain |

---

## Phase 1: Papers to Add (~6 new citations)

### 1. VSS Methodology
**Escudero, L. F., Garín, A., Merino, M., & Pérez, G. (2007).** The value of the stochastic solution in multistage problems. *TOP*, 15(1), 48–64.

- **Why:** This is the standard VSS reference for stochastic programming. Your VSS analysis (100 iterations, $37M average, 100% non-negative) is a standout result. Citing this signals you know the formal VSS framework.
- **Where it fits:** End of the two-stage stochastic paragraph, after Birge & Louveaux.

### 2. Food Industry MLCLSP
**Mediouni, A., Zufferey, N., Rached, M., & Cheikhrouhou, N. (2021).** The multi-period multi-level capacitated lot-sizing and scheduling problem in the dairy soft-drink industry. *Supply Chain Forum: An International Journal*.

- **Why:** Directly analogous to BobaCo — beverage production with BOM structure, shelf-life constraints, parallel lines. Shows MLCLSP is actively researched in food/beverage.
- **Where it fits:** After the existing CLSP/MLCLSP paragraph. Evidence that your problem class is relevant today.

### 3. Rolling Horizon with Stochastic Demand (Food Context)
**Cruz, J. A., de Salles-Neto, L. L., & Schenekemberg, C. M. (2025).** A rolling horizon approach for a production planning and inventory management problem under stochastic demand. *Process Integration and Optimization for Sustainability*, 9, 2021–2046.

- **Why:** Very recent. Dairy producer case study with stochastic demand + rolling horizon + perishability. Same methodological stack as your project. Validates the rolling-horizon approach in a comparable setting.
- **Where it fits:** After the Sahin rolling horizon paragraph. Concrete evidence that rolling horizon works for stochastic food production.

### 4. Two-Stage Stochastic Programming with VSS in Industry
**Alvarez, A., Cordeau, J.-F., Jans, R., Munari, P., & Morabito, R. (2021).** Inventory routing under stochastic supply and demand. *Omega*, 102, 102304.

- **Why:** Uses two-stage stochastic programming + VSS analysis + backlogging recourse actions. Methodologically similar. Shows the VSS framework being applied in a real industrial context.
- **Where it fits:** Reinforces the stochastic programming paragraph.

### 5. HPP Integration
**Gelders, L. F. & Van Wassenhove, L. N. (1982).** Hierarchical integration in production planning: Theory and practice. *Journal of Operations Management*, 3(1), 27–35.

- **Why:** Your two-model hierarchical approach needs integration — how do the LT and ST models talk to each other? This paper discusses exactly that (slack, cross-level consistency).
- **Where it fits:** After the existing HPP paragraph. Bridges from "why hierarchical" to "how we integrated the two levels."

### 6. Scenario Generation in Stochastic Programming
**Birge & Louveaux (2011), Chapter 5** already covers scenario generation, but you could also cite a sampling-based approach paper if desired. The current description (uniform sampling within bands) is clear enough — this may not need a new citation.

---

## Phase 2: Restructured Lit Review (Target: ~9 paragraphs)

Current structure (6 paragraphs). Proposed restructure:

| # | Topic | Papers | Purpose for INFORMS |
|---|---|---|---|
| 1 | CLSP/MLCLSP framing | Karimi 2003, Maes 1991 | "This problem belongs to the MLCLSP family" |
| 2 | **Food industry MLCLSP** | Mediouni 2021 | Shows active research in beverage production |
| 3 | Backlogging in lot-sizing | Pochet & Wolsey 1988 | Justifies your backlog modeling |
| 4 | Hierarchical PP | Bitran & Hax 1982, Liberatore & Miller 1985 | Architecture motivation |
| 5 | **HPP integration** | Gelders & Van Wassenhove 1982 | Your two-model link — integration is key |
| 6 | Rolling horizon | Sahin et al. 2013 | Justifies replanning frequency |
| 7 | **Rolling horizon + stochastic food** | Cruz et al. 2025 | Directly comparable case study |
| 8 | Two-stage stochastic + VSS | Birge & Louveaux 2011, Escudero 2007 | Grounds VSS analysis in literature |
| 9 | Synthesis | All above | "These motivate our hierarchical stochastic rolling-horizon approach" |

---

## Phase 3: Framing for INFORMS Judges

### What judges care about (from prize description + past winners):
1. **Is the work significant?** → Your $37M VSS and 42% cost reduction answer this.
2. **Did it require clever OR methodology?** → This is where the lit review matters. Each citation should show you *chose* a specific technique for a reason, not that you read a paper.
3. **Did it create substantial, measurable value?** → The benchmarking table and pilot study answer this.

### Key rules for every lit review paragraph:
- **End with a bridge sentence** connecting the paper to *your* modeling choice. Example: "This motivates our use of a hierarchical decomposition to keep the short-term MILP tractable while capturing uncertainty in the aggregate layer."
- **Don't just summarize papers** — tell a story about why these techniques fit your specific problem structure (multi-level BOM, seasonal demand, 12-day backlog threshold).
- **The VSS analysis is a standout result** — make sure it's cited properly in the lit review so judges see it's grounded in formal stochastic programming theory.

### Before/After example (current lit review paragraph 1):

**Before (current):**
> CLSP and MLCLSP studies describe the "fully integrated" benchmark for multi-product, multi-period planning with capacity limits and intermediate items, and they also explain why such models quickly become difficult to solve at realistic scale.

**After (with bridge):**
> CLSP and MLCLSP studies describe the "fully integrated" benchmark for multi-product, multi-period planning with capacity limits and intermediate items, and they also explain why such models quickly become difficult to solve at realistic scale. Recent work in the food and beverage industry, such as Mediouni et al. (2021), confirms that MLCLSP formulations with shelf-life constraints and multi-level BOM structures remain computationally challenging in practice. Our problem inherits this complexity — a monolithic daily MILP over a full-year horizon exceeded 2,200 seconds in testing — which motivates the decomposed hierarchical approach described in Section 4.

---

## Summary of Deliverables

1. Add 4–6 new BibTeX entries to `report.bib` (all DOIs known)
2. Expand lit review from 6 → 9 paragraphs
3. Add bridge sentences to the end of each existing paragraph
4. Add a sentence citing Escudero (2007) for the VSS methodology
5. No AI-generated prose — paper URLs and BibTeX provided for you to craft the text
