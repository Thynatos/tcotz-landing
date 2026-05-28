# REVIEW: Dynamic Production Planning Under Seasonal and Stochastic Demand (Bilkent IE Team 21)

**Reviewer:** Simulated INFORMS Undergraduate OR Prize judge (adversarial pre-submission review)
**Date:** 2026-05-28
**Submission reviewed:** `TCOTZ_21/report.pdf` (24 pages) and `TCOTZ_21/report.bib`

---

## 1. Top-Line Verdict

This paper would make my shortlist but not my podium. It is a competent, well-cited applied submission with a real industrial deployment and a defensible mathematical contribution — substantially above the median applied entry. However, the architectural novelty claim is over-engineered, the headline cost-reduction figure in the abstract misattributes which two systems are being compared, and the methodological contribution (a two-tier backlog penalty plus a textbook combination of stochastic programming, MILP, and rolling horizon) is not strong enough to compete with the algorithmic novelty of recent winners. The paper sits in **Tier-2 (honorable mention candidate)** as currently written. With targeted revisions to the abstract, the novelty framing, and the deployment evidence, it could push toward borderline Tier-1.

## 2. Scoring (0–10)

| Criterion | Score | One-line justification |
|---|---|---|
| **Significance** | 6.5 | Real industrial problem with a credible sponsor, but the domain (small/medium F&B manufacturer, 4 products, 2 lines) is not at the scale of past applied winners (Toronto Parking Authority, AnadoluJet); the "any SME" generalizability claim is too vague to elevate it. |
| **OR methodology** | 6.0 | Sound integration of well-established techniques (two-stage stochastic programming, MILP, rolling horizon, hierarchical decomposition) with all canonical citations present; the two-tier backlog penalty is a legitimate but minor original contribution; no algorithmic novelty that an off-the-shelf solver couldn't reproduce given the same data. |
| **Measurable value** | 6.0 | KPI improvements are substantial (overtime 28.2 → 0.3 days, 7/10 scenarios with zero backlog), and the 45-day baseline is defended; however, costs are in model units rather than dollars, the pilot is only 4 weeks, and the abstract's 42% cost reduction figure is misattributed (it's vs. deterministic approximation, not vs. semi-manual system). |

## 3. Strengths

1. **Canonical-citation discipline is exemplary** (Section 3, throughout). Birge (1982) for VSS, Billington et al. (1983) for MLCLSP, Drexl & Kimms (1997) for the lot-sizing/scheduling distinction, Pochet & Wolsey (1988) for backlogging, Blackburn et al. (1986) for nervousness, Suerie & Stadtler (2003) for linked lot sizes, Bitran et al. (1982) for HPP, Englberger et al. (2016) explicitly named as the closest analog. This is the cleanest foundational-citation set I have seen in an applied submission this year.

2. **The benchmark baseline is defended in text rather than asserted** (Section 5.2, p. 20). The 45-day backward allocation rule is calibrated against historical logs and confirmed by the industrial advisor; the "33 days of buffer past the 12-day cancellation threshold" framing forecloses the "your baseline is a strawman" objection. This is rare in capstone submissions.

3. **The two-tier backlog penalty is a real, industrially motivated modeling contribution** (Section 4.3.1, p. 10). The 12-day cancellation threshold is empirically grounded and the cost differentiation between $b_i$ and $b_i^{12}$ is clean. This extension to Pochet & Wolsey (1988) is small but genuine.

4. **Full mathematical specification with sets, parameters, decision variables, and 18 numbered constraints** (Section 4.3.1, pp. 8–10). The paper does not hand-wave the model.

5. **The Streamlit web application with user manual** (Section 5.1, p. 19; Figure 5, p. 21) is concrete deliverable evidence — not a Jupyter notebook the company will never open.

## 4. Weaknesses That Would Lose Points

### Critical (fix before submission)

**C1. Abstract misattributes the 42% cost reduction.** The abstract reads "Compared with the current semi-manual system, the proposed approach reduces average total cost by 42% and average overtime from 28.2 to 0.3 days." But the body (Conclusion, p. 21; Table 9, p. 18) is explicit that the 42% is stochastic vs. deterministic approximation under the rolling horizon, not vs. the semi-manual baseline. The semi-manual comparison (Section 5.2, Table 10) reports overtime and backlog KPIs only — no cost figure. A judge reading the abstract will assume the 42% is the headline industrial impact; the body contradicts that reading. **This is a credibility-killer if a judge notices, and judges always notice the abstract.** Fixable in 5 minutes by separating the two claims.

**C2. The "three-layer" framing contradicts the architecture figure.** Figure 2 (p. 12) shows a two-box diagram: Long-Term Model → Short-Term Model. The "three-layer" label requires counting "weekly rolling-horizon execution" as a layer, which is non-standard — rolling horizon is a *protocol*, not a model layer. The contributions section (p. 7) and the architectural novelty paragraph (p. 7) both lean on "three-layer." A reviewer will see the figure first and the claim second and conclude the team is inflating. Either rename the diagram to show three layers, or rewrite as "two-layer hierarchical model executed in a rolling horizon."

### Major

**M1. Architectural novelty claim is over-qualified.** "First study to design, mathematically formulate, and deploy a live three-layer hierarchical decision support system that integrates a monthly two-stage stochastic aggregate planning model with a daily MILP operational scheduling model via temporal inventory-target linking constraints under a weekly rolling-horizon execution in a B2B process manufacturing setting" (p. 7). Each qualifier shrinks the claim space. The distinction from Englberger et al. (2016) — separating the operational MILP into a distinct layer with hard linking constraints — is real but narrow. A senior reviewer will read this as "we did Englberger 2016 with an extra constraint family." Recommend rewriting as a more honest "to the best of our knowledge, no published deployed system combines these elements," dropping "first."

**M2. The pilot is 4 weeks.** Section 5.3 (p. 21) reports a 4-week pilot in which "the company approved every weekly plan as feasible." Compare to the 2013 Bilkent winner (AnadoluJet, system in routine use) and 2019 Waterloo (Toronto Parking Authority, deployed system). A 4-week pilot in which the company *approves* plans is weaker than a deployment in which the company *runs the system* independently for months. The paper should be clearer about whether (a) BobaCo executed production from the system's outputs in those 4 weeks, and (b) whether the company committed to continued use after the pilot.

**M3. The "exact" benchmark in Table on p. 17 is itself suboptimal in stress scenarios.** The verification table compares heuristic vs. Gurobi across 10 scenarios. The text claims (Section 4.5.1, p. 16) that Scenario 9 exceeded 2,200 seconds. But the table shows Gurobi *did* produce a solution in Scenarios 9 and 10 (with massive 12-day backlogs of 49M and 47M units respectively). Either Gurobi was given unlimited time (in which case "intractable" is too strong) or the Gurobi solution is time-limited and suboptimal (in which case the "Opt. Gap" column is misleading). This circular dependency between the intractability argument and the verification benchmark weakens both claims.

**M4. Costs reported in "model units" undermine the 42% claim's interpretability.** The VSS analysis (Section 4.5.3, p. 18) explicitly disclaims that cost figures are model units, not accounting costs. This is honest but means the headline 42% is mathematically valid yet financially uninterpretable. Past applied winners reported dollarized impact (Waterloo 2019: multi-million-dollar revenue; Bilkent 2013: deployed system handling routine flight scheduling). Without a dollar figure, the magnitude of impact is hard for a judge to evaluate.

**M5. Notation inconsistency between models.** The daily mathematical model (p. 9, eq. 8) uses $u_{2i}$ in the BOM coupling constraint; the long-term deterministic model (p. 12, eq. 4) and the two-stage stochastic model (p. 14) use $u_{i2}$. These are mathematically equivalent given the indexing but confusing for a careful reader.

**M6. Equations (15)–(16) on p. 15 appear visually garbled in the PDF.** The linking constraints render with overlapping/truncated symbols (likely a `\hspace{-2cm}` interaction with the alignat environment). The .tex source is logically correct, but a judge reading the PDF will see what looks like a typesetting error in the most important equation of the paper — the cross-level linking constraint that justifies the hierarchical decomposition. Fix by rewriting with a simpler equation environment.

**M7. The 80.48% VSS magnitude requires more context.** Table 8 (p. 18) reports an average VSS of 80.48%, with Avg RP = 4.45M and Avg EEV = 41.6M units — i.e., the stochastic solution costs only 10.7% of the deterministic-under-uncertainty solution. The paper acknowledges this is driven by the 1:160:10,000 cost asymmetry (Conclusion, p. 21). But an 80% VSS is suspiciously large and will provoke "this is rigged by the cost ratio" objections. The paper should either (a) report VSS under a more moderate cost ratio as a sensitivity, or (b) add a single sentence noting that VSS is bounded above by the EEV cost structure and the magnitude reflects the catastrophic-cancellation regime BobaCo actually faces.

### Minor

**m1. Abstract is approximately 102 words.** Borderline against a 100-word INFORMS limit. Trim by 2–5 words.

**m2. Verification Case IX ("near-zero lead times → markedly elevated computation time") conflates verification with performance.** Verification asks "does the model behave logically?" not "does it solve quickly?" Drop or relabel.

**m3. The VSS table reports min/max but no standard deviation.** The "Min VSS = 0.00" is explained as degenerate iterations where the EEV solution is feasible, which is fine — but a histogram or stddev would be more rigorous than min/max.

**m4. The generalizability claim ("applicable to any SME facing seasonal demand with long-horizon procurement lead times and recently expanded storage capacity, particularly in food and beverage manufacturing where multi-level BOM dependencies and synchronized line constraints are common") is structurally specific but operationally vague.** It names features but does not identify the next plant the system could be deployed at. A concrete example would strengthen.

**m5. Future work is one sentence and addresses only scenario generation.** A paper at this level should have a more developed future-work paragraph covering, at minimum, multi-stage extension, demand learning, and the path from 4-week pilot to permanent use.

**m6. Türkmen et al. (2021) is cited from *Journal Européen des Systèmes Automatisés***, which is below the journal tier of the rest of the bibliography (Management Science, EJOR, IJPR, POM, Mathematical Programming, Operations Research). Defensible because it is a Turkish F&B precedent, but a reviewer will notice the dip.

## 5. Citation Audit

The bibliography is, overall, the strongest part of the paper.

| Cited work | Journal/Tier | Use | Verdict |
|---|---|---|---|
| Birge (1982) | Mathematical Programming | VSS definition | **Canonical, correctly attributed** |
| Billington et al. (1983) | Management Science | MLCLSP formal definition | **Canonical, correctly attributed** |
| Drexl & Kimms (1997) | EJOR | Lot-sizing vs. scheduling | **Canonical, correctly attributed** |
| Pochet & Wolsey (1988) | Mathematical Programming | Backlog formulation | **Canonical, correctly attributed** |
| Blackburn et al. (1986) | Management Science | Schedule nervousness | **Canonical, correctly attributed** |
| Suerie & Stadtler (2003) | Management Science | Linked lot sizes | **Canonical, correctly attributed** |
| Bitran et al. (1982) | Operations Research | HPP foundation | **Canonical, correctly attributed** |
| Liberatore & Miller (1985) | Interfaces | Deployed HPP precedent | Good, appropriately cited |
| Maes et al. (1991) | EJOR | MLCLSP complexity | Good |
| Karimi et al. (2003) | Omega | CLSP review | Good |
| Helber & Sahling (2010) | IJPE | Fix-and-optimize | Good |
| Englberger et al. (2016) | IJPR | Closest analog | **Critical citation, correctly framed as the comparison baseline** |
| Forel & Grunow (2023) | POM | Stochastic + rolling horizon | Good, recent, top journal |
| Thevenin et al. (2021) | POM | Stochastic MRP | Good, recent, top journal |
| Sahin et al. (2013) | IJPR | Rolling horizon survey | Good |
| Körpeoğlu et al. (2011) | EJOR | MPS under uncertainty | Good |
| Mula et al. (2006) | IJPE | Production planning review | Good, dominant survey |
| Ferreira et al. (2009) | EJOR | Soft drink structural analog | Good |
| Toledo et al. (2009) | IJPR | Two-level lot-sizing/scheduling | Good |
| Türkmen et al. (2021) | JESA | Turkish F&B precedent | **Weakest citation in the set**; defensible only because the contextual analog is rare |
| Nahmias & Olsen (2015) | Textbook | Foundational reference | Appropriate as textbook citation |
| Birge & Louveaux (2011) | Textbook | Two-stage stochastic framework | Appropriate; **Birge (1982) is also present for the VSS-specific claim, which is the correct discipline** |
| BobaCo company webpage | Web | Company description | Appropriate |

**Verdict on citation hygiene: Strong.** Every canonical foundational paper expected for this methodology stack is present. One weak citation (Türkmen) is defensible by context. No survey-substituted-for-primary issues. No missing Birge (1982). No missing Billington (1983).

## 6. Comparison to a Prize-Winning Standard

**What past winners had that this paper lacks:**

- **2019 Waterloo (Toronto Parking Authority):** Multi-million-dollar quantified impact in real currency. System used by the city after the project. This paper has overtime-day reduction (strong) but no dollarized impact and no evidence of continued sponsor use beyond a 4-week pilot.

- **2013 Bilkent (AnadoluJet flight scheduling):** Deployed system that became the routine scheduling tool for the airline, with operational integration of complex side constraints (crew, equipment, aircraft type). The OR contribution was visible in the model formulation. This paper has the deployment claim but at a much smaller scale and shorter duration, and the OR contribution (two-tier backlog) is incremental.

- **2021 Georgia Tech (Atlanta bicycle network):** Methodologically novel algorithmic contribution that solves a published-literature-recognizable problem. This paper combines existing methods rather than introducing a new one.

- **2024 NUS (partial optimal transport):** Companion AAAI 2024 publication, external validation. This paper has no concurrent venue, no external recognition, no co-publication path mentioned.

**The gold-medal version of this paper would have:**

1. A clean abstract distinguishing two analyses (stochastic vs. deterministic, and proposed vs. semi-manual) with separate quantified figures for each.
2. A pilot of at least 8–12 weeks with the company independently running the system, plus a stated commitment to continued use.
3. Dollarized impact: "in the 2026 summer season, the system is projected to save BobaCo ₺X million in cancellation losses and overtime premiums" — even if only an estimate, with the conversion logic in an appendix.
4. A *named* methodological contribution — e.g., "the *two-tier backlog formulation with cancellation-threshold linkage* (TBT-CTL)" — that future papers could cite.
5. A simpler architecture diagram showing three labeled layers, matching the three-layer claim.
6. A companion submission to IFORS 2026, INFORMS Annual Meeting 2026, or an IJPE/POM journal pipeline mentioned in the paper.

## 7. Tier Classification

**Tier-2 (honorable mention candidate)** as currently written.

Drivers of this classification:
- Solid problem grounding and real industrial collaboration (Tier-2 marker)
- Well-cited methodology with all canonical sources present (Tier-1 marker, partially)
- Defended baseline and quantified KPI improvement (Tier-2 marker)
- No algorithmic novelty — combination of established methods (below Tier-1)
- Pilot of 4 weeks rather than months of independent operation (below Tier-1 deployment marker)
- Costs in model units, not dollarized (weaker than Tier-1 impact magnitude)
- Architectural novelty claim is heavily qualified and partly contradicted by the architecture figure (below Tier-1 contribution sentence)
- No external validation, conference, or continued-use evidence (below Tier-1 stretch markers)

With the C1 and C2 fixes plus M2 and M4 improvements, this paper could become an upper-Tier-2 / borderline Tier-1 candidate.

## 8. Final Actionable Recommendations (Ranked by Impact per Hour)

1. **(30 min, very high impact) Fix the abstract.** Separate the two comparisons. Specifically: "The stochastic formulation reduces total cost by 42% relative to its deterministic approximation across 100 VSS iterations; compared with the current semi-manual planning system, the proposed approach reduces overtime requirements from 28.2 to 0.3 days on average and achieves zero backlog and zero overtime in 7 of 10 demand scenarios." Then verify abstract length is ≤100 words.

2. **(15 min, high impact) Re-frame "three-layer" or fix Figure 2.** Either rewrite "three-layer" as "two-layer hierarchical model with weekly rolling-horizon execution" throughout, or redraw Figure 2 to actually depict three labeled layers (Aggregate / Operational / Rolling-Horizon Protocol).

3. **(1 hr, high impact) Fix the rendering of equations (15)–(16) on p. 15.** Move the linking constraints out of the `alignat` block into a standalone `align` block without `\hspace`. These are the constraints that justify the entire decomposition; they must render cleanly.

4. **(1 hr, high impact) Soften the "first study" novelty claim.** Replace "to the best of our knowledge, this is the first study to..." with "we are not aware of any published deployed system that combines..." — this is honest, sounds less inflated, and is harder to attack.

5. **(2 hr, medium-high impact) Add a dollarized impact estimate.** Even an appendix paragraph estimating ₺ savings from overtime reduction and avoided cancellations would give the judge a number they can interpret. Use BobaCo's actual overtime cost per day if available.

6. **(2 hr, medium impact) Strengthen the pilot description.** State explicitly: did BobaCo execute production from the system's outputs in the pilot weeks (vs. just reviewing them)? Has the company committed to continued use? If yes, name the commitment. If no, acknowledge as future work.

7. **(1 hr, medium impact) Fix the notation inconsistency** ($u_{2i}$ vs. $u_{i2}$) by standardizing across all three model formulations.

8. **(30 min, medium impact) Add a sentence after Table 8** acknowledging that the 80.48% VSS magnitude is driven by the 1:160:10,000 cost ratio and reflects the catastrophic-cancellation regime, with a forward reference to the sensitivity test.

9. **(30 min, low-medium impact) Drop or relabel Verification Case IX** ("near-zero lead times → elevated computation") — it conflates verification with performance.

10. **(15 min, low impact) Audit unused .bib entries** (kok2018, mahmutogullari2019, Hakkimizda, Ramsay1983, Nahmias2020, Kunsch1989, Dudek2014, Zhang2013, Armstrong2004) and remove them to signal a tight, intentional bibliography.

11. **(2 hr, low-medium impact) Develop the Future Work paragraph** beyond scenario generation to include multi-stage extension, demand learning under forecast evolution, and the path from pilot to permanent deployment.

12. **(low priority, if time) Identify a concurrent venue** for companion submission (IFORS 2026, INFORMS Annual Meeting, IJPE/POM) and mention it in the paper, even as "we are preparing a journal-length companion to this manuscript." External validation matters at the prize-decision margin.

---

Items 1, 2, 3, and 4 are the unblockers for this submission. Without them, a careful judge will dock the paper on credibility (C1) and novelty inflation (C2, M1). With them, the paper becomes a legitimate Tier-2 finalist with an outside shot at the medal if the applied field is weaker than the theoretical field in 2026.
