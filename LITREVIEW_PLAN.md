# Literature Review & Methodology Rewrite Plan — INFORMS 2026

> **Philosophy:** Every citation must earn its place. INFORMS judges are OR faculty. They will recognize weak journals and unnecessary citations. Aim for 13–16 total references: the current 8 + 5–8 high-quality additions. Quality over quantity.

---

## 1. Problems with the Current Literature Review

| Issue | Impact on Score |
|---|---|
| VSS analysis reported (100 iterations, $37M average) but VSS never cited | Judges think you don't know what VSS is formally |
| MLCLSP formally defined by Billington 1983 (MS, 375 citations) — not cited | You're missing the paper that named the problem you're solving |
| Birge (1982) — the original VSS definition in Math Prog — not cited, only his 2011 textbook | Textbook is fine for the framework; the 1982 paper is the VSS definition |
| No review of stochastic production planning literature; Mula et al. (2006), 572 citations, not cited | Judges see you haven't read the field's most important survey |
| Helber & Sahling (2010), the leading MLCLSP methods paper, not cited | You claim NP-hardness as motivation but don't cite the methods literature |
| `turkmen2021` and `korpeoglu2011` already in bib, never used in lit review | Free citations you're not using |
| Alvarez et al. 2021 (inventory routing) proposed as "stochastic production" citation | Wrong domain — IRP ≠ production planning; judges will notice |
| Duplicate bib entry: `bitran1982` and `bitran1982hpp` | BibTeX compile error risk and judge confusion |
| Bridge sentences absent from paragraphs 1–5 | Lit review summarizes knowledge rather than motivating choices |

---

## 2. Revised Citation Strategy

### Citations to Add (all verified, with scite citation counts)

#### **Priority 1 — Must add (cited results with no citation)**

**A. Birge (1982) — Canonical VSS Definition**
> Birge, J. R. (1982). The value of the stochastic solution in stochastic linear programs with fixed recourse. *Mathematical Programming*, 24(1), 314–325. DOI: 10.1007/bf01585113

```bibtex
@article{birge1982vss,
  author  = {Birge, John R.},
  title   = {The value of the stochastic solution in stochastic linear programs with fixed recourse},
  journal = {Mathematical Programming},
  volume  = {24},
  number  = {1},
  pages   = {314--325},
  year    = {1982},
  doi     = {10.1007/bf01585113}
}
```
- **Why:** 296 citing publications. Published in *Mathematical Programming*. This is *the* paper where VSS was defined by John Birge himself. The standard citation is not the 2011 textbook for the definition — it is this 1982 paper. Multiple papers cite it as: "for the definition of VSS, we refer to Birge (1982)." Your 100-iteration VSS analysis currently has no citation for what VSS is.
- **Where:** Single sentence in the stochastic programming paragraph: "We evaluate this benefit using the Value of the Stochastic Solution (VSS), originally defined by \citet{birge1982vss} as the difference between the recourse problem objective and the expected cost when first-stage decisions are fixed to the deterministic optimum."

**B. Billington, McClain & Thomas (1983) — Formal MLCLSP Definition (for the long-term model)**
> Billington, P. J., McClain, J. O., & Thomas, L. J. (1983). Mathematical programming approaches to capacity-constrained MRP systems: Review, formulation and problem reduction. *Management Science*, 29(10), 1126–1141. DOI: 10.1287/mnsc.29.10.1126

```bibtex
@article{billington1983mlclsp,
  author  = {Billington, Peter J. and McClain, John O. and Thomas, L. Joseph},
  title   = {Mathematical programming approaches to capacity-constrained {MRP} systems: Review, formulation and problem reduction},
  journal = {Management Science},
  volume  = {29},
  number  = {10},
  pages   = {1126--1141},
  year    = {1983},
  doi     = {10.1287/mnsc.29.10.1126}
}
```
- **Why:** 375 citing publications. Published in *Management Science* (INFORMS). Formally defined and named the MLCLSP. The long-term model (monthly aggregate with BOM dependency) fits this class. Karimi (2003) and Maes (1991) both cite it. Note: the short-term MILP (with machine-assignment binaries) extends beyond MLCLSP into the lot-sizing and scheduling literature — see Section 4a classification guidance.
- **Where:** First sentence of the MLCLSP paragraph: "At the aggregate level, the problem resembles the Multi-Level Capacitated Lot Sizing Problem (MLCLSP), formally introduced by \citet{billington1983mlclsp}..."

**B2. Drexl & Kimms (1997) — Lot-Sizing AND Scheduling Survey (for the short-term model)**
> Drexl, A., & Kimms, A. (1997). Lot sizing and scheduling — Survey and extensions. *European Journal of Operational Research*, 99(2), 221–235. DOI: 10.1016/S0377-2217(97)00030-1

```bibtex
@article{drexl1997lss,
  author  = {Drexl, Andreas and Kimms, Alf},
  title   = {Lot sizing and scheduling --- {Survey} and extensions},
  journal = {European Journal of Operational Research},
  volume  = {99},
  number  = {2},
  pages   = {221--235},
  year    = {1997},
  doi     = {10.1016/S0377-2217(97)00030-1}
}
```
- **Why:** 558 citing publications. THE reference for classifying multi-level lot-sizing and scheduling problems (where production sequence and machine assignment are integrated with lot-sizing). BobaCo's short-term MILP has binary machine-assignment variables where production is fully determined by the binary — this is a scheduling feature, not a classical MLCLSP feature. Helber & Sahling (2010) and Toledo et al. (2009) both cite Drexl & Kimms as the taxonomy reference.
- **Where:** New paragraph (between MLCLSP and backlogging paragraphs): after explaining MLCLSP complexity, add one sentence: "At the operational level, our daily MILP integrates machine-assignment scheduling with inventory decisions, extending the MLCLSP into the lot-sizing and scheduling framework surveyed by \citet{drexl1997lss}."\

---

#### **Priority 2 — Should add (high impact, direct domain fit)**

**C. Mula, Poler & García-Sabater (2006) — Production Planning Under Uncertainty Survey**
> Mula, J., Poler, R., & García-Sabater, J. P. (2006). Models for production planning under uncertainty: A review. *International Journal of Production Economics*, 103(1), 271–285. DOI: 10.1016/j.ijpe.2005.09.001

```bibtex
@article{mula2006review,
  author  = {Mula, Josefa and Poler, Ra{\'u}l and Garc{\'i}a-Sabater, Jos{\'e} P.},
  title   = {Models for production planning under uncertainty: {A} review},
  journal = {International Journal of Production Economics},
  volume  = {103},
  number  = {1},
  pages   = {271--285},
  year    = {2006},
  doi     = {10.1016/j.ijpe.2005.09.001}
}
```
- **Why:** 572 citing publications — the most-cited review of stochastic production planning. Covers hierarchical production planning with demand uncertainty explicitly. Citing it signals that you have surveyed the field and know where your contribution fits within a 20-year research tradition.
- **Where:** New opening paragraph of the literature review, or closing synthesis: "Production planning under uncertainty has attracted sustained research attention, spanning aggregate, hierarchical, and lot-sizing models \cite{mula2006review}. Our system integrates three distinct strands of this literature..."

**D. Helber & Sahling (2010) — MLCLSP Fix-and-Optimize (Leading Methods Paper)**
> Helber, S., & Sahling, F. (2010). A fix-and-optimize approach for the multi-level capacitated lot sizing problem. *International Journal of Production Economics*, 123(2), 247–256. DOI: 10.1016/j.ijpe.2009.08.022

```bibtex
@article{helber2010mlclsp,
  author  = {Helber, Stefan and Sahling, Florian},
  title   = {A fix-and-optimize approach for the multi-level capacitated lot sizing problem},
  journal = {International Journal of Production Economics},
  volume  = {123},
  number  = {2},
  pages   = {247--256},
  year    = {2010},
  doi     = {10.1016/j.ijpe.2009.08.022}
}
```
- **Why:** 203 citing publications. The leading MILP methods paper for MLCLSP. It explicitly states that for capacitated production systems with non-zero setup times, "the question whether a feasible production plan (without overtime) exists has been shown to be NP-complete, see Maes et al. (1991)." Citing this alongside Maes (1991) and Karimi (2003) strengthens your NP-hardness motivation: it shows that even the best state-of-the-art exact methods are impractical at realistic scale, which is what you observed (2,200 seconds for full-year daily model).
- **Where:** After the Karimi/Maes MLCLSP paragraph: "Even state-of-the-art methods such as the fix-and-optimize approach of \citet{helber2010mlclsp} target medium-scale instances; in our testing, a monolithic full-year daily MILP exceeded 2,200 seconds, confirming that a hierarchical decomposition is necessary."

---

#### **Priority 3 — Activate (already in bib, add citation)**

**E. Körpeoğlu, Yaman & Aktürk (2011) — Already in bib as `korpeoglu2011`**
- Multi-stage stochastic programming for master production scheduling, *EJOR*, 213(1), 166–179.
- **Why:** Stochastic programming applied directly to production scheduling. Better fit than Alvarez et al. 2021 (IRP). Adds an EJOR-caliber reference for the stochastic production planning angle.
- **Action:** Add `\cite{korpeoglu2011}` in the two-stage stochastic paragraph, after Birge & Louveaux: "...and has been applied to master production scheduling in similar multi-period settings \cite{korpeoglu2011}."

**F. Türkmen, Çelebi & Güray (2021) — Already in bib as `turkmen2021`**
- Multi-stage production planning for a small food/beverage company.
- **Why:** Closest existing case study to BobaCo. Small company + food/beverage + multi-stage. Directly validates that your problem class is real and industrially studied.
- **Action:** Add `\cite{turkmen2021}` in new food/beverage paragraph alongside Mediouni 2021.

---

#### **Priority 4 — Add if space allows**

**G. Gelders & Van Wassenhove (1982) — HPP Integration**
> Gelders, L. F., & Van Wassenhove, L. N. (1982). Hierarchical integration in production planning: Theory and practice. *Journal of Operations Management*, 3(1), 27–35. DOI: 10.1016/0272-6963(82)90019-5

```bibtex
@article{gelders1982hpp,
  author  = {Gelders, L. F. and Van Wassenhove, L. N.},
  title   = {Hierarchical integration in production planning: Theory and practice},
  journal = {Journal of Operations Management},
  volume  = {3},
  number  = {1},
  pages   = {27--35},
  year    = {1982},
  doi     = {10.1016/0272-6963(82)90019-5}
}
```
- **Why:** Addresses how aggregate and detailed planning levels stay consistent — directly relevant to your inventory-target linking constraints (days 24 and 48).
- **Note:** Lower priority if page budget is tight; Bitran & Hax 1982 already addresses hierarchical integration.

**H. Mediouni et al. (2021) — Food Industry MLCLSP**
Already included in previous plan (DOI: 10.1080/16258312.2021.2007735). Confirmed real. Use alongside `turkmen2021` for the food/beverage paragraph.

**I. Cruz et al. (2025) — Rolling Horizon + Stochastic Demand, Food Context**
Already included in previous plan. Use for rolling horizon paragraph if space allows. Most recent comparable case study.

---

#### **Drop from previous plan**

- ❌ **Escudero et al. (2007)** — TOP journal, lower prestige. **Replaced by Birge (1982) in Mathematical Programming.** Birge 1982 is the original VSS definition; Escudero 2007 extends it to multistage. Since your model is two-stage (not multistage), Birge 1982 is the exact citation.
- ❌ **Alvarez et al. (2021)** — Inventory routing problem. Wrong domain for a production planning paper. Judges will notice the mismatch. **Replaced by Körpeoğlu 2011 (already in bib)**.

---

#### **Bib fix (do first)**
Remove the duplicate entry `bitran1982` from `report.bib`. It is identical to `bitran1982hpp`. Search the `.tex` file for any `\cite{bitran1982}` occurrences and replace with `\cite{bitran1982hpp}`.

---

## 3. Restructured Literature Review (10 paragraphs, ~1.5 pages double-spaced)

| # | Topic | Key Citations | Bridge sentence target |
|---|---|---|---|
| 1 | Field framing: production planning under uncertainty | Nahmias 2015, **Mula et al. 2006** | "These frameworks collectively establish the cost structure and methodological vocabulary our models inherit." |
| 2 | CLSP/MLCLSP — aggregate complexity | Karimi 2003, Maes 1991, **Billington 1983** | "At the aggregate level, BobaCo's problem belongs to this MLCLSP family; a monolithic daily MILP over a full year exceeded 2,200 seconds, confirming these complexity results." |
| 3 | **Lot-sizing and scheduling (NEW)** | **Drexl & Kimms 1997** | "At the operational level, the daily MILP extends MLCLSP by integrating machine-assignment scheduling decisions, placing it in the lot-sizing and scheduling literature." |
| 4 | **Food/beverage LSP applications** | **Türkmen 2021**, **Mediouni 2021** | "The most structurally similar case is the two-level soft drink scheduling problem; our contribution extends these with a stochastic aggregate layer and live rolling-horizon deployment." |
| 5 | Backlogging in lot-sizing | Pochet & Wolsey 1988 | "We extend this framework with a two-tier penalty distinguishing regular backlog from the 12-day critical threshold beyond which orders are cancelled." |
| 6 | Hierarchical Production Planning | Bitran & Hax 1982, Liberatore & Miller 1985 | "We follow this two-stage structure, passing monthly inventory targets to the short-term MILP as linking constraints at days 24 and 48." |
| 7 | **HPP integration** | **Gelders & Van Wassenhove 1982** | "The cross-level inventory-target linking constraints we introduce are motivated by this consistency requirement." |
| 8 | Rolling horizon execution | Sahin 2013, Cruz 2025 | "We replicate every Monday with near-term stabilization, limiting fluctuations in the production schedule while tracking new demand information." |
| 9 | Two-stage stochastic programming | Birge & Louveaux 2011, **Körpeoğlu 2011** | "We follow the two-stage formulation in the aggregate layer, making first-stage decisions before uncertainty is revealed and optimizing scenario-dependent recourse in months 3–12." |
| 10 | **VSS definition and validation** | **Birge 1982** | "Our 100-iteration VSS analysis uses this definition; the stochastic approach dominated the deterministic approximation in all 100 iterations, with an average advantage of $37M." |
| 11 | Synthesis | All above | "Taken together, these strands motivate the hierarchical stochastic rolling-horizon approach in Section 4: a two-stage stochastic aggregate model passes inventory targets to an operational MILP that simultaneously solves lot-sizing and machine-assignment scheduling, replanned weekly in a rolling horizon." |

---

## 4. Methodology Section Rewrite Guidance

The methodology section needs three structural changes to compete at INFORMS level.

### 4a. The Classification Question — MLCLSP vs. Lot-Sizing and Scheduling

**This is the most important precision issue in the paper. Do not blindly call this "MLCLSP."**

After examining the actual short-term model formulation (constraints 2–18), the problem has features that classical MLCLSP does not:

| Feature | Classical MLCLSP | BobaCo short-term model |
|---|---|---|
| Period type | Big-bucket (multiple items per period if capacity allows) | Effectively small-bucket: Line 2 has exclusive constraint between products 3 and 4 |
| Production quantity | Continuous variable $P_{k,t}$, independent of setup binary | **Fully determined by binary**: $P_{j,t} = \sum_m \kappa_m X_{m,j,t}$ |
| Decision binaries | Setup indicator $y_{k,t}$ (is item $k$ produced in period $t$?) | Machine-assignment $X_{m,j,t}$ (which machine, which product, which day) |
| BOM dependency | ✅ Yes (multi-level) | ✅ Yes (product 2 feeds products 3 and 4) |

This means the short-term MILP is more precisely a **multi-level lot-sizing and scheduling problem** in the sense of Drexl & Kimms (1997) — it integrates inventory/BOM decisions with daily machine-assignment scheduling decisions.

**Drexl & Kimms (1997)** — the canonical survey distinguishing lot-sizing problems (quantities only) from lot-sizing AND scheduling problems (quantities + sequence/assignment):
> Drexl, A., & Kimms, A. (1997). Lot sizing and scheduling — Survey and extensions. *European Journal of Operational Research*, 99(2), 221–235. DOI: 10.1016/S0377-2217(97)00030-1

```bibtex
@article{drexl1997lss,
  author  = {Drexl, Andreas and Kimms, Alf},
  title   = {Lot sizing and scheduling --- {Survey} and extensions},
  journal = {European Journal of Operational Research},
  volume  = {99},
  number  = {2},
  pages   = {221--235},
  year    = {1997},
  doi     = {10.1016/S0377-2217(97)00030-1}
}
```
- **558 citing publications.** THE reference for classifying combined lot-sizing + scheduling problems. Cites Drexl & Kimms as: "A literature review for the single-level, the continuous time and the multi-level lot-sizing and scheduling problems can be found in Drexl and Kimms (1997)."

**Crucially, the two model layers have DIFFERENT correct classifications:**

- **Long-term model** (monthly, two-stage stochastic): aggregate production quantities without machine-level scheduling — fits the MLCLSP / stochastic aggregate production planning literature (Billington 1983, Karimi 2003, Maes 1991, Körpeoğlu 2011)
- **Short-term model** (daily MILP): machine-assignment binaries, product exclusivity, BOM — fits the **multi-level lot-sizing and scheduling** (LSP) literature (Drexl & Kimms 1997)

**Correct language for the paper:**

> "The planning problem faced by BobaCo spans two interconnected problem classes. At the aggregate planning level, the problem resembles a multi-level capacitated lot-sizing problem (MLCLSP) under demand uncertainty \cite{billington1983mlclsp, karimi2003cls, maes1991mlcls, korpeoglu2011}, where decisions concern monthly production volumes and inventory targets for a multi-level bill-of-materials. At the operational scheduling level, the problem integrates lot-sizing with daily machine-assignment decisions — a structure classified by \citet{drexl1997lss} as a multi-level lot-sizing and scheduling problem (LSP). A full-year, daily-resolution exact formulation of the combined problem exceeded 2,200 seconds in testing, motivating the hierarchical decomposition developed in this section."

**Close analogy to cite (bonus, if space allows):**
> Toledo, C. F. M., França, P. M., & Morábito, R. (2009). Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem. *International Journal of Production Research*, 47(11), 3097–3119. DOI: 10.1080/00207540701675833

```bibtex
@article{toledo2009sitlsp,
  author  = {Toledo, Cl{\'a}udio Fabiano Motta and Fran{\c{c}}a, Paulo Morelato and Morab{\'i}to, Reinaldo},
  title   = {Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem},
  journal = {International Journal of Production Research},
  volume  = {47},
  number  = {11},
  pages   = {3097--3119},
  year    = {2009},
  doi     = {10.1080/00207540701675833}
}
```
- **94 citing publications.** Addresses a **real soft drink company in Brazil** with a two-level production process, parallel machines, and integrated scheduling. This is the closest structural analog to BobaCo in the published literature. Use it to say: "Our problem structure is analogous to the two-level scheduling problem studied in soft drink manufacturing by \citet{toledo2009sitlsp}, extended here with a stochastic aggregate layer and a live rolling-horizon deployment."

### 4b. Add the problem classification paragraph

**Insert as the very first paragraph of Section 4:**

Adapt the language above depending on how much space you have — the full two-paragraph version for maximum INFORMS impact, or a compressed one-paragraph version if page budget is tight.

### 4c. Unify the notation table (saves ~1 page)

### 4b. Unify the notation table (saves ~1 page)

Sets $K_1$, $K_2$, $T$, $S$ are re-defined in every sub-model section. Define them once in a shared "Sets and Parameters" table at the start of Section 4. Each sub-model section then says only: "Using the notation from Table X..." This is standard practice in OR papers and a signal of professional polish.

### 4c. Add a computational evidence table to Section 8 (Verification)

INFORMS judges reward empirical rigor. Currently the computational justification for the heuristic is in prose. Convert to a compact table:

| Scenario | Exact solver runtime (s) | Heuristic runtime (s) | Obj. deviation (%) | 10-day backlog deviation |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |
| ... | | | | |
| 9 | 2,247 | 38 | 1.2% | 0 |

This makes the case for the heuristic visually undeniable in 5 seconds of reading.

---

## 5. What to Do About the 12-Day Critical Backlog Penalty

No exact literature analog was found — this is appropriate. The modeling choice is:
1. **Grounded in** Pochet & Wolsey (1988) for the general backlogging structure
2. **Novel extension:** the two-tier penalty ($B_{i,t}$ for regular backlog, $B_{i,t}^{12}$ for critical backlog beyond 12 days) is an original contribution motivated by the company's observed order cancellation threshold

**How to write it:** Do NOT hunt for a citation that doesn't exist. Instead, write it explicitly as a modeling contribution:

> "We extend the standard backlogging formulation \cite{PochetWolsey1988} by introducing a second backlog variable $B_{i,t}^{12}$ that tracks demand unmet for more than 12 days — the empirically observed threshold beyond which BobaCo's customers cancel orders. This two-tier penalty structure allows the model to distinguish between operationally tolerable short delays and service failures with direct revenue consequences."

Framing it this way turns a potential weakness (no citation) into a strength (original modeling contribution grounded in industrial data).

---

## 6. Final Citation Count and Journal Prestige Profile

| # | Citation | Journal | Year | Scite pubs |
|---|---|---|---|---|
| 1 | Nahmias & Olsen (2015) | Textbook (Waveland) | 2015 | — |
| 2 | **Billington et al. (1983)** ★ NEW | *Management Science* | 1983 | 375 |
| 3 | Karimi et al. (2003) | *Omega* | 2003 | (existing) |
| 4 | Maes et al. (1991) | *EJOR* | 1991 | (existing) |
| 5 | **Helber & Sahling (2010)** ★ NEW | *IJPE* | 2010 | 203 |
| 6 | **Türkmen et al. (2021)** ★ activate | *JESA* | 2021 | — |
| 7 | **Mediouni et al. (2021)** ★ NEW | *Supply Chain Forum* | 2021 | — |
| 8 | Pochet & Wolsey (1988) | *Mathematical Programming* | 1988 | (existing) |
| 9 | Bitran & Hax (1982) | *Operations Research* | 1982 | (existing) |
| 10 | Liberatore & Miller (1985) | *Interfaces* | 1985 | (existing) |
| 11 | **Gelders & Van Wassenhove (1982)** ★ NEW | *J. Operations Mgmt* | 1982 | — |
| 12 | Sahin et al. (2013) | *IJPR* | 2013 | (existing) |
| 13 | **Cruz et al. (2025)** ★ NEW | *PIOS* | 2025 | — |
| 14 | Birge & Louveaux (2011) | Textbook (Springer) | 2011 | — |
| 15 | **Körpeoğlu et al. (2011)** ★ activate | *EJOR* | 2011 | — |
| 16 | **Birge (1982)** ★ NEW | *Mathematical Programming* | 1982 | 296 |
| 17 | **Mula et al. (2006)** ★ NEW | *IJPE* | 2006 | 572 |

**★ = new or newly activated (9 changes)**  
Journal prestige after changes: 3 INFORMS journals (OR/MS/INFORMS-published), 3 Springer journals (Math Prog, EJOR, AOR), 2 Elsevier top journals (IJPE, Omega), 2 authoritative textbooks.

---

## 7. Priority-Ordered Action List

### Do immediately (free, already in bib):
1. Fix bib: remove `bitran1982`, keep `bitran1982hpp`; update all `\cite{bitran1982}` → `\cite{bitran1982hpp}` in `.tex`
2. Add `\cite{turkmen2021}` to the MLCLSP/food paragraph
3. Add `\cite{korpeoglu2011}` to the stochastic programming paragraph

### Add to bib and cite (3 new entries with highest ROI):
4. Add `birge1982vss` BibTeX → cite for VSS definition (replaces Escudero 2007)
5. Add `billington1983mlclsp` BibTeX → cite at start of MLCLSP paragraph
6. Add `mula2006review` BibTeX → cite in opening/synthesis paragraph
7. Add `helber2010mlclsp` BibTeX → cite after NP-hardness claim

### Structural changes to manuscript:
8. Insert problem classification paragraph as first paragraph of Section 4
9. Consolidate notation tables into one shared table at top of Section 4
10. Convert heuristic verification results from prose to a computational evidence table
11. Add bridge sentences to end of all 10 lit review paragraphs
12. Reframe 12-day backlog as an explicit modeling contribution (no new citation needed)

### Optional (if space budget permits):
13. Add `gelders1982hpp` for HPP integration
14. Add `mediouni2021mlclsp` for food industry paragraph
15. Add `cruz2025rolling` for rolling horizon paragraph
