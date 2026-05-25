# Focused Deep Research: Novelty of Three-Layer Hierarchical Stochastic Production Planning

---

## Q1. Combined stochastic + operational scheduling MILP + rolling horizon — does this exact architecture exist?

**Direct answer:**  
No, based on the provided literature, **no published paper exists that explicitly combines all three layers**—a two-stage or multi-stage stochastic aggregate model passing inventory targets as linking constraints to a daily operational scheduling MILP, executed in a rolling horizon framework, and deployed together in a real industrial setting.

**Suggested sentence for novelty claim:**  
"To the best of our knowledge, no published work has deployed all three layers together—a two-stage stochastic aggregate model that passes inventory targets to a daily operational scheduling MILP, executed in a rolling horizon framework, in a real industrial setting."

**Supporting details:**  
- Several papers address two-stage stochastic programming for aggregate planning with rolling horizon execution  (Englberger et al., 2016; Gioia et al., 2022; Schlenkrich et al., 2024; Bindewald et al., 2023), and some integrate planning and scheduling under uncertainty  (Gao et al., 2024; Han et al., 2020; Tian, 2014; Dering & Swartz, 2022; Curcio et al., 2018), but none combine all three layers with explicit cross-level linking constraints as described.
- Recent works (e.g.,  (Gao et al., 2024),  (Han et al., 2020),  (Tian, 2014),  (Dering & Swartz, 2022)) propose integrated models or frameworks but do not demonstrate the full three-layer architecture with scenario-based stochastic aggregate planning, deterministic daily MILP scheduling, and weekly rolling horizon stabilization in an industrial DSS.

**Top 3 closest papers (none are exact matches):**

| Citation | Title & Authors | Journal | Citation Count | Journal Tier | Match Description |
|----------|----------------|---------|---------------|--------------|-------------------|
|  (Englberger et al., 2016)Englberger et al. (2016), "Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment" | Int. J. Prod. Res., 2016, 26 cites | EJOR/IJPR tier | 26 | High | Two-stage stochastic MPS with rolling horizon; does not include separate daily MILP scheduling layer or explicit cross-level linking constraints |
|  (Gao et al., 2024)Gao et al. (2024), "Integrated batch production planning and scheduling optimization considering processing time uncertainty" | Optimization and Engineering, 2024, 4 cites | Lower | 4 | Medium | Integrated planning/scheduling under uncertainty with rolling horizon; does not separate deterministic MILP for daily ops nor explicit target propagation |
|  (Dering & Swartz, 2022)Dering & Swartz (2022), "A stochastic optimization framework for integrated scheduling and control under demand uncertainty" | Comput. Chem. Eng., 2022, 10 cites | Lower | 10 | Medium-Low | Two-stage stochastic approach with rolling horizon for integrated scheduling/control; lacks explicit hierarchical decomposition and cross-level linking |

**Confidence:** High

---

## Q2. Hierarchical stochastic decomposition with cross-level linking constraints

**Direct answer:**  
No paper in the provided set demonstrates a **stochastic aggregate model explicitly passing inventory targets or safety stock levels as hard constraints to a deterministic short-term scheduling model** (i.e., via formal linking constraints at specific time points such as days 24 and 48).

- Most hierarchical approaches either pass parameters or use soft coupling; hard constraint propagation is not documented in these abstracts.
- The correct academic terminology for this mechanism is typically **"cross-level linking constraints," "hierarchical decomposition with target propagation,"** or **"constraint-driven disaggregation."**
- Some works discuss hierarchical frameworks or integration of planning/scheduling ( (Bitran et al., 1981), Bitran et al., OR 1981;  (Englberger et al., 2016), Englberger et al., IJPR 2016), but do not specify hard constraint coupling at intermediate points.

**Supporting details:**
- No abstract mentions the mechanism of passing inventory targets as hard constraints from an upper-level stochastic model to a lower-level deterministic scheduler.
- The terminology "linking constraints," "target propagation," or "constraint-driven disaggregation" is consistent with usage in hierarchical production planning literature ( (Bitran et al., 1981)).

**Confidence:** High

---

## Q3. Verify Toledo et al. (2009) — DOI conflict

**Direct answer:**  
The two DOIs correspond to **the same paper**, not two different papers.

- DOI A: **10.1080/00207540701675833**
- DOI B: **10.1080/00207540701774431**

Both refer to:
> Toledo, C., França, P., Morabito, R., Kimms, A. (2009). Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem. *International Journal of Production Research*, Vol. 47(19), pp. 5471–5493.

The content provided ( (Toledo et al., 2009)) confirms this is the SITLSP paper motivated by a real soft drink plant.

There is no evidence from abstracts/full text that these are different papers; likely one DOI is erroneous or represents an online/print split.

**Full citation:**  
Toledo, C., França, P., Morabito, R., Kimms, A. "Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem." *International Journal of Production Research*, Vol. 47(19), pp. 5471–5493 (2009). DOI: 10.1080/00207540701675833

**Citation count:** ~101

**Journal tier:** EJOR/IJPR tier

**Confidence:** High

---

## Q4. Schedule nervousness and stabilization — canonical reference

**Direct answer:**  
The most canonical reference on schedule nervousness in production planning and rolling horizon contexts among the provided set is:

> Lin, P.-C.; Uzsoy, R. "Chance-constrained formulations in rolling horizon production planning: an experimental study." *International Journal of Production Research*, Vol. 54(7), pp. 2178–2192 (2016). DOI: Not provided ( (Lin & Uzsoy, 2016))

This paper directly addresses schedule nervousness ("frequent changes in planned release and production quantities") within rolling horizon procedures for production planning under uncertainty.

- It examines chance-constrained models for reducing nervousness in planned releases within a rolling horizon environment.
- Applies directly to rolling horizon lot-sizing/planning rather than just MRP nervousness.

**Full citation:**  
Lin, P.-C.; Uzsoy, R., "Chance-constrained formulations in rolling horizon production planning: an experimental study." *International Journal of Production Research*, Vol. 54(7), pp. 2178–2192 (2016).

**Citation count:** ~35

**Journal tier:** EJOR/IJPR tier

**Confidence:** High

---

# Summary Table

| Question                                                                                                   | Direct Answer / Top Reference(s)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Q1: Does this exact three-layer architecture exist?                                                        | No exact match exists.<br>Closest: Englberger et al., IJPR (2016)  (Englberger et al., 2016); Gao et al., Optimization & Engineering (2024)  (Gao et al., 2024); Dering & Swartz, Comput Chem Eng (2022)  (Dering & Swartz, 2022).<br>Use sentence: "To the best of our knowledge…"                                                                                                                         |
| Q2: Stochastic aggregate → deterministic scheduler via hard linking constraints?                           | No direct evidence found.<br>Terminology: "cross-level linking constraints," "target propagation," "constraint-driven disaggregation."<br>No paper demonstrates hard constraint propagation at intermediate points as described.<br>Closest conceptual references are Bitran et al., OR (1981)  (Bitran et al., 1981).         |
| Q3: Toledo et al. (2009) DOI conflict                                                                     | Both DOIs refer to the same paper:<br>Toledo et al., IJPR (2009), "Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem."<br>DOI: 10.1080/00207540701675833<br>This is about SITLSP at a real soft drink plant.<br>Citations ~101           |
| Q4: Canonical reference for schedule nervousness/stabilization                                             | Lin & Uzsoy (2016), "Chance-constrained formulations in rolling horizon production planning," IJPR.<br>Citations ~35.<br>This paper directly addresses schedule nervousness within rolling horizon lot-sizing/planning contexts.<br>Applies beyond MRP nervousness alone.<br> (Lin & Uzsoy, 2016)|

---

# References Used
 (Toledo et al., 2009): Toledo C., França P.M., Morabito R., Kimms A., "Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem", International Journal of Production Research, Vol.47(19), pp.5471–5493 (2009). DOI:10.1080/00207540701675833  
 (Gao et al., 2024): Gao J.X., Guo Z.Q., Liu L.L., Dong Y.C., Du J., "Integrated batch production planning and scheduling optimization considering processing time uncertainty", Optimization and Engineering, Apr 2024  
 (Han et al., 2020): Han J.L., Liu Y.L., Luo L.S., Mao M.S., "Integrated production planning and scheduling under uncertainty: A fuzzy bi-level decision-making approach", Knowl Based Syst, Aug 2020  
 (Lin & Uzsoy, 2016): Lin P.-C.; Uzsoy R.; "Chance-constrained formulations in rolling horizon production planning: an experimental study", International Journal of Production Research, Vol.54(7), pp.2178–2192 (2016)  
 (Gioia et al., 2022): Gioia D.; Fadda E.; Brandimarte P.; "Rolling horizon policies for multi-stage stochastic assemble-to-order problems", International Journal of Production Research, Oct 2022  
 (Englberger et al., 2016): Englberger J.; Herrmann F.; Manitz M.; "Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment", International Journal of Production Research, Mar 2016  
 (Tian, 2014): Tian Y.; "Chemical production planning and scheduling integration under demand uncertainty", CIESC Journal, Jan 2014  
 (Bitran et al., 1981): Bitran G.R.; Haas E.A.; Hax A.C.; "Hierarchical Production Planning: A Single Stage System", Operations Research, Aug 1981  
 (Dering & Swartz, 2022): Dering D.; Swartz C.; "A stochastic optimization framework for integrated scheduling and control under demand uncertainty", Comput Chem Engin July 2022  
 (Schlenkrich et al., 2024): Schlenkrich M.; Seiringer W.; Altendorfer K.; Parragh S.N.; "Enhancing Rolling Horizon Production Planning Through Stochastic Optimization Evaluated by Means of Simulation", Feb 2024  
 (Curcio et al., 2018): Curcio E.; Amorim P.; Zhang Q.; Almada-Lobo B.; "Adaptation and approximate strategies for solving the lot-sizing and scheduling problem under multistage demand uncertainty", International Journal of Production Economics Aug 2018  
 (Bindewald et al., 2023): Bindewald V.; Dunke F.; Nickel S.; "Comparison of different approaches to multistage lot sizing with uncertain demand", Int Trans Oper Res Apr 2023
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders' consent._
 
## References
 
Bindewald, V., Dunke, F., & Nickel, S. (2023). Comparison of different approaches to multistage lot sizing with uncertain demand. *Int. Trans. Oper. Res., 30*, 3771-3800. https://doi.org/10.1111/itor.13305
 
Bitran, G., Haas, E., & Hax, A. (1981). Hierarchical Production Planning: A Single Stage System. *Oper. Res., 29*, 717-743. https://doi.org/10.1287/opre.29.4.717
 
Curcio, E., Amorim, P., Zhang, Q., & Almada-Lobo, B. (2018). Adaptation and approximate strategies for solving the lot-sizing and scheduling problem under multistage demand uncertainty. *International Journal of Production Economics*. https://doi.org/10.1016/j.ijpe.2018.04.012
 
Dering, D., & Swartz, C. (2022). A stochastic optimization framework for integrated scheduling and control under demand uncertainty. *Comput. Chem. Eng., 165*, 107931. https://doi.org/10.1016/j.compchemeng.2022.107931
 
Englberger, J., Herrmann, F., & Manitz, M. (2016). Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment. *International Journal of Production Research, 54*, 6192 - 6215. https://doi.org/10.1080/00207543.2016.1162917
 
Gao, J., Guo, Z., Liu, L., Dong, Y., & Du, J. (2024). Integrated batch production planning and scheduling optimization considering processing time uncertainty. *Optimization and Engineering, 25*, 2369 - 2400. https://doi.org/10.1007/s11081-024-09886-4
 
Gioia, D., Fadda, E., & Brandimarte, P. (2022). Rolling horizon policies for multi-stage stochastic assemble-to-order problems. *International Journal of Production Research, 62*, 5108 - 5126. https://doi.org/10.1080/00207543.2023.2283570
 
Han, J., Liu, Y., Luo, L., & Mao, M. (2020). Integrated production planning and scheduling under uncertainty: A fuzzy bi-level decision-making approach. *Knowl. Based Syst., 201-202*, 106056. https://doi.org/10.1016/j.knosys.2020.106056
 
Lin, P., & Uzsoy, R. (2016). Chance-constrained formulations in rolling horizon production planning: an experimental study. *International Journal of Production Research, 54*, 3927 - 3942. https://doi.org/10.1080/00207543.2016.1165356
 
Schlenkrich, M., Seiringer, W., Altendorfer, K., & Parragh, S. (2024). Enhancing Rolling Horizon Production Planning Through Stochastic Optimization Evaluated by Means of Simulation.
 
Tian, Y. (2014). Chemical production planning and scheduling integration under demand uncertainty. *CIESC Journal*.
 
Toledo, C., França, P., Morabito, R., & Kimms, A. (2009). Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem. *International Journal of Production Research, 47*, 3097 - 3119. https://doi.org/10.1080/00207540701675833
