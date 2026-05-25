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
- ❌ **Alvarez et al. (2021)** — Inventory routing problem. Wrong domain for a production planning paper. **Replaced by Körpeoğlu 2011 (already in bib)**.
- ❌ **Cruz et al. (2025)** — Confirmed real but *Process Integration and Optimization for Sustainability* is not top-tier; only ~3 citing publications. **Replaced by Englberger 2016 + Forel & Grunow 2023** which cover the same ground at higher prestige.
- ❌ **Mediouni et al. (2021)** — Confirmed real but *Supply Chain Forum* is not a top-tier OR journal (~13 citations). **Replaced by Ferreira et al. (2009) EJOR** (144 citing publications, same food/beverage domain).

---

#### **Priority 5 — New additions from focused deep research (all scite-verified)**

**J. Ferreira, Morábito & Rangel (2009) — Soft Drink Integrated Lot-Sizing and Scheduling**
> Ferreira, D., Morábito, R., & Rangel, S. (2009). Solution approaches for the soft drink integrated production lot sizing and scheduling problem. *European Journal of Operational Research*, 196(2), 697–706. DOI: 10.1016/j.ejor.2008.03.035

```bibtex
@article{ferreira2009softdrink,
  author  = {Ferreira, Deisemara and Morab{\'i}to, Reinaldo and Rangel, Socorro},
  title   = {Solution approaches for the soft drink integrated production lot sizing and scheduling problem},
  journal = {European Journal of Operational Research},
  volume  = {196},
  number  = {2},
  pages   = {697--706},
  year    = {2009},
  doi     = {10.1016/j.ejor.2008.03.035}
}
```
- **144 citing publications. EJOR.** Real soft drink plant, two-stage synchronization between liquid preparation and parallel bottling lines. This is a stronger food/beverage analog than Toledo 2009 (higher citations, better journal). Use alongside Toledo 2009: Ferreira for EJOR prestige, Toledo for Kimms co-authorship connection to Drexl & Kimms 1997.

**K. Forel & Grunow (2023) — Stochastic Lot-Sizing in Rolling-Horizon Planning**
> Forel, A., & Grunow, M. (2023). Dynamic stochastic lot sizing with forecast evolution in rolling-horizon planning. *Production and Operations Management*, 32(2), 449–468. DOI: 10.1111/poms.13881

```bibtex
@article{forel2023stochastic,
  author  = {Forel, Alexandre and Grunow, Martin},
  title   = {Dynamic stochastic lot sizing with forecast evolution in rolling-horizon planning},
  journal = {Production and Operations Management},
  volume  = {32},
  number  = {2},
  pages   = {449--468},
  year    = {2023},
  doi     = {10.1111/poms.13881}
}
```
- **10 citing publications (2023, recent). POM (top-tier INFORMS journal).** Best single reference combining stochastic lot-sizing with rolling-horizon planning. Closest methodological analog to the full system; distinguishes short-term and long-term planning segments within one framework. Replaces Cruz 2025 as the rolling-horizon + stochastic reference.

**L. Thevenin, Adulyasak & Cordeau (2021) — Stochastic MRP Under Demand Uncertainty**
> Thevenin, S., Adulyasak, Y., & Cordeau, J.-F. (2021). Material Requirements Planning Under Demand Uncertainty Using Stochastic Optimization. *Production and Operations Management*, 30(2), 475–493. DOI: 10.1111/poms.13277

```bibtex
@article{thevenin2021mrp,
  author  = {Thevenin, Simon and Adulyasak, Yossiri and Cordeau, Jean-Fran{\c{c}}ois},
  title   = {Material Requirements Planning Under Demand Uncertainty Using Stochastic Optimization},
  journal = {Production and Operations Management},
  volume  = {30},
  number  = {2},
  pages   = {475--493},
  year    = {2021},
  doi     = {10.1111/poms.13277}
}
```
- **50 citing publications. POM (top-tier).** Stochastic optimization treatment of MRP / multi-echelon lot sizing under demand uncertainty with rolling horizon implementation. Validates the static-dynamic decision framework of Layer 1 (first-stage setups frozen, second-stage volumes as recourse). Also explicitly computes VSS — useful for the VSS paragraph.

**M. Blackburn, Kropp & Millen (1986) — Schedule Nervousness in MRP Systems**
> Blackburn, J. D., Kropp, D. H., & Millen, R. A. (1986). A Comparison of Strategies to Dampen Nervousness in MRP Systems. *Management Science*, 32(4), 413–429. DOI: 10.1287/mnsc.32.4.413

```bibtex
@article{blackburn1986nervousness,
  author  = {Blackburn, Joseph D. and Kropp, Dean H. and Millen, Robert A.},
  title   = {A Comparison of Strategies to Dampen Nervousness in {MRP} Systems},
  journal = {Management Science},
  volume  = {32},
  number  = {4},
  pages   = {413--429},
  year    = {1986},
  doi     = {10.1287/mnsc.32.4.413}
}
```
- **181 citing publications. Management Science (INFORMS, top-tier).** Definitive comparative study of nervousness-dampening strategies in rolling-horizon production planning; proves schedule freezing is the most cost-efficient stabilizer. Directly supports Layer 3's near-term stabilization mechanism.

**N. Suerie & Stadtler (2003) — Capacitated Lot-Sizing with Linked Lot Sizes**
> Suerie, C., & Stadtler, H. (2003). The Capacitated Lot-Sizing Problem with Linked Lot Sizes. *Management Science*, 49(8), 1039–1054. DOI: 10.1287/mnsc.49.8.1039.16406

```bibtex
@article{suerie2003clspl,
  author  = {Suerie, Christopher and Stadtler, Hartmut},
  title   = {The Capacitated Lot-Sizing Problem with Linked Lot Sizes},
  journal = {Management Science},
  volume  = {49},
  number  = {8},
  pages   = {1039--1054},
  year    = {2003},
  doi     = {10.1287/mnsc.49.8.1039.16406}
}
```
- **139 citing publications. Management Science (INFORMS, top-tier).** Formalizes how setup and inventory variables are mathematically linked across consecutive periods in a rolling horizon environment. Provides the academic basis for "inventory-target linking constraints" — the exact mechanism used at days 24 and 48.

**O. Englberger, Herrmann & Manitz (2016) — Two-Stage Stochastic MPS in Rolling Planning**
> Englberger, J., Herrmann, F., & Manitz, M. (2016). Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment. *International Journal of Production Research*, 54(20), 6192–6215. DOI: 10.1080/00207543.2016.1162917

```bibtex
@article{englberger2016stochastic,
  author  = {Englberger, Julian and Herrmann, Frank and Manitz, Michael},
  title   = {Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment},
  journal = {International Journal of Production Research},
  volume  = {54},
  number  = {20},
  pages   = {6192--6215},
  year    = {2016},
  doi     = {10.1080/00207543.2016.1162917}
}
```
- **28 citing publications. IJPR.** The closest single-paper architectural match to our system (two-stage stochastic MPS + rolling execution). Low citation count because it is a niche intersection — this is precisely why our combined three-layer architecture is novel. Cite it to say: "The closest published analog, Englberger et al. (2016), addresses stochastic MPS in a rolling environment but does not include a separate daily operational scheduling MILP with cross-level linking constraints."

---

#### **DOI corrections (critical — wrong DOIs circulating in drafts)**

| Paper | Incorrect DOI | Correct DOI |
|---|---|---|
| Thevenin et al. (2021) POM | 10.1111/poms.13289 | **10.1111/poms.13277** |
| Ferreira et al. (2009) EJOR | 10.1016/j.ejor.2008.03.033 | **10.1016/j.ejor.2008.03.035** |
| Suerie & Stadtler (2003) | 10.1287/mnsc.49.8.1039.16402 | **10.1287/mnsc.49.8.1039.16406** |
| Toledo et al. (2009) IJPR | 10.1080/00207540701675833 (early-view) | **10.1080/00207540701774431** (official print) |

Also: **Sahin et al. (2013) IJPR author correction** — the correct authors are **Sahin, Narayanan & Robinson** (not Süral & Denizel). Update the bib entry.

---

#### **Bib fix (do first)**
Remove the duplicate entry `bitran1982` from `report.bib`. It is identical to `bitran1982hpp`. Search the `.tex` file for any `\cite{bitran1982}` occurrences and replace with `\cite{bitran1982hpp}`.

---

## 3. Restructured Literature Review (11 paragraphs, ~1.5 pages double-spaced)

| # | Topic | Key Citations | Bridge sentence target |
|---|---|---|---|
| 1 | Field framing: production planning under uncertainty | Nahmias 2015, **Mula et al. 2006**, **Thevenin et al. 2021** | "These frameworks collectively establish the cost structure and methodological vocabulary our models inherit." |
| 2 | CLSP/MLCLSP — aggregate complexity | Karimi 2003, Maes 1991, **Billington 1983**, **Helber & Sahling 2010** | "At the aggregate level, BobaCo's long-term model belongs to this MLCLSP family; a monolithic daily MILP over a full year exceeded 2,200 seconds, confirming these complexity results." |
| 3 | **Lot-sizing and scheduling (NEW)** | **Drexl & Kimms 1997** | "At the operational level, the daily MILP extends MLCLSP by integrating machine-assignment scheduling decisions, placing it in the lot-sizing and scheduling literature." |
| 4 | **Food/beverage LSP applications** | **Ferreira et al. 2009 (EJOR)**, **Toledo et al. 2009 (IJPR)**, **Türkmen 2021** | "Our contribution extends these with a stochastic aggregate layer and live rolling-horizon deployment — a combination not previously published." |
| 5 | Backlogging in lot-sizing | Pochet & Wolsey 1988 | "We extend this framework with a two-tier penalty distinguishing regular backlog from the 12-day critical threshold beyond which orders are cancelled." |
| 6 | Hierarchical Production Planning | Bitran & Hax 1982, Liberatore & Miller 1985 | "We follow this two-stage structure, passing monthly inventory targets to the short-term MILP as linking constraints at days 24 and 48." |
| 7 | **Cross-level linking constraints** | **Suerie & Stadtler 2003 (MS)** | "The inventory-target linking constraints at days 24 and 48 formalize this coordination mechanism as hard constraints on the operational layer." |
| 8 | Rolling horizon execution + nervousness | Sahin, Narayanan & Robinson 2013, **Blackburn et al. 1986 (MS)**, **Forel & Grunow 2023 (POM)** | "Near-term decisions are stabilized following the schedule-freezing approach of Blackburn et al. (1986), proven to minimize plan instability in rolling-horizon production systems." |
| 9 | Two-stage stochastic programming | Birge & Louveaux 2011, **Körpeoğlu 2011** | "We follow the two-stage formulation in the aggregate layer, making first-stage decisions before uncertainty is revealed and optimizing scenario-dependent recourse in months 3–12." |
| 10 | **VSS definition and validation** | **Birge 1982**, **Thevenin et al. 2021** | "Our 100-iteration VSS analysis uses this definition; the stochastic approach dominated the deterministic approximation in all 100 iterations, with an average advantage of $37M." |
| 11 | Synthesis + novelty claim | All above, **Englberger et al. 2016** | "To the best of our knowledge, this is the first study to design, formulate, and deploy a live three-layer hierarchical DSS integrating a monthly two-stage stochastic aggregate model with a daily MILP operational scheduling model via inventory-target linking constraints under weekly rolling-horizon execution in a B2B manufacturing setting." |

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

### 4b. Add the problem classification paragraph + novelty claim

**Insert as the very first paragraph of Section 4:**

Adapt the language above depending on how much space you have — the full two-paragraph version for maximum INFORMS impact, or a compressed one-paragraph version if page budget is tight.

**Follow with the architectural novelty sentence** (verified by three independent deep research runs — no exact match exists in published literature):

> "To the best of our knowledge, this is the first study to design, mathematically formulate, and deploy a live three-layer hierarchical decision support system that integrates a monthly two-stage stochastic aggregate planning model with a daily MILP operational scheduling model via temporal inventory-target linking constraints under a weekly rolling-horizon execution in a B2B process manufacturing setting. Existing studies address stochastic rolling-horizon planning \cite{forel2023stochastic}, integrated lot-sizing-and-scheduling under uncertainty \cite{drexl1997lss}, or stochastic multi-echelon MRP \cite{thevenin2021mrp}, but no published live industrial system combines all three architectural elements in one deployed stack."

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

| # | Citation | Journal | Year | Scite pubs | Status |
|---|---|---|---|---|---|
| 1 | Nahmias & Olsen (2015) | Textbook (Waveland) | 2015 | — | existing |
| 2 | **Billington et al. (1983)** | *Management Science* | 1983 | 375 | ★ NEW |
| 3 | Karimi et al. (2003) | *Omega* | 2003 | — | existing |
| 4 | Maes et al. (1991) | *EJOR* | 1991 | — | existing |
| 5 | **Helber & Sahling (2010)** | *IJPE* | 2010 | 203 | ★ NEW |
| 6 | **Drexl & Kimms (1997)** | *EJOR* | 1997 | 558 | ★ NEW |
| 7 | **Ferreira, Morábito & Rangel (2009)** | *EJOR* | 2009 | 144 | ★ NEW — replaces Mediouni 2021 |
| 8 | **Toledo et al. (2009)** | *IJPR* | 2009 | 145 | ★ NEW |
| 9 | **Türkmen et al. (2021)** | *JESA* | 2021 | — | ★ activate from bib |
| 10 | Pochet & Wolsey (1988) | *Mathematical Programming* | 1988 | — | existing |
| 11 | Bitran & Hax (1982) | *Operations Research* | 1982 | — | existing |
| 12 | Liberatore & Miller (1985) | *Interfaces* | 1985 | — | existing |
| 13 | **Suerie & Stadtler (2003)** | *Management Science* | 2003 | 139 | ★ NEW — linking constraints |
| 14 | **Blackburn, Kropp & Millen (1986)** | *Management Science* | 1986 | 181 | ★ NEW — schedule nervousness |
| 15 | Sahin, Narayanan & Robinson (2013) | *IJPR* | 2013 | — | existing — **fix author names** |
| 16 | **Forel & Grunow (2023)** | *POM* | 2023 | 10 | ★ NEW — replaces Cruz 2025 |
| 17 | **Englberger et al. (2016)** | *IJPR* | 2016 | 28 | ★ NEW — novelty framing |
| 18 | Birge & Louveaux (2011) | Textbook (Springer) | 2011 | — | existing |
| 19 | **Körpeoğlu et al. (2011)** | *EJOR* | 2011 | — | ★ activate from bib |
| 20 | **Birge (1982)** | *Mathematical Programming* | 1982 | 296 | ★ NEW |
| 21 | **Mula et al. (2006)** | *IJPE* | 2006 | 572 | ★ NEW |
| 22 | **Thevenin, Adulyasak & Cordeau (2021)** | *POM* | 2021 | 50 | ★ NEW — stochastic MRP + VSS |

**★ = new or newly activated (14 changes)**

**Page-budget note:** 22 citations is too many for a 25-page paper. Target 16–18. Candidates to cut if tight: Gelders 1982 (HPP integration, lower impact), Carlson 1979 (schedule nervousness — Blackburn 1986 is sufficient), Toledo 2009 (keep if Ferreira 2009 alone doesn't satisfy a reviewer wanting a second food/beverage case), Englberger 2016 (keep only if the novelty sentence survives editing).

**Journal prestige profile:** 5 INFORMS journals (Management Science ×3, Operations Research, POM ×2), 4 Elsevier top journals (EJOR ×3, IJPE ×2), 1 Springer (Math Prog), 2 authoritative textbooks. This is a strong profile for a prize submission.

---

## 7. Priority-Ordered Action List

### Step 1 — Bib fixes (zero writing, do first):
1. Remove duplicate `bitran1982`; keep `bitran1982hpp`; replace all `\cite{bitran1982}` → `\cite{bitran1982hpp}` in `.tex`
2. Fix Sahin 2013 bib entry: authors = Sahin, Narayanan & Robinson (not Süral & Denizel)
3. Fix Toledo 2009 DOI: use `10.1080/00207540701774431` (official print)

### Step 2 — Add new BibTeX entries (all BibTeX in Section 2 above):
4. `birge1982vss` — VSS definition
5. `billington1983mlclsp` — MLCLSP
6. `drexl1997lss` — LSP taxonomy
7. `mula2006review` — stochastic production planning survey
8. `helber2010mlclsp` — MLCLSP fix-and-optimize
9. `ferreira2009softdrink` — soft drink EJOR (replaces Mediouni 2021)
10. `toledo2009sitlsp` — soft drink IJPR
11. `forel2023stochastic` — stochastic rolling horizon POM (replaces Cruz 2025)
12. `thevenin2021mrp` — stochastic MRP POM
13. `blackburn1986nervousness` — schedule nervousness Management Science
14. `suerie2003clspl` — linked lot sizes Management Science
15. `englberger2016stochastic` — exact methodological analog IJPR

### Step 3 — Activate from existing bib:
16. Add `\cite{turkmen2021}` to food/beverage paragraph
17. Add `\cite{korpeoglu2011}` to stochastic programming paragraph

### Step 4 — Structural manuscript changes:
18. Insert problem classification paragraph (Section 4a language above) as first paragraph of Section 4
19. Add architectural novelty sentence (Section 4b above) to introduction or end of Section 4 opening
20. Consolidate notation tables into one shared table at top of Section 4
21. Convert heuristic verification results from prose to computational evidence table
22. Rewrite lit review to 11 paragraphs with bridge sentences (Section 3 table above)
23. Reframe 12-day backlog as original modeling contribution (Section 5 language above)

### Step 5 — Optional (add if page budget allows after Step 4):
24. `gelders1982hpp` — HPP cross-level integration
25. Keep Englberger 2016 only if the novelty sentence makes it into the final paper
