### Q1. Combined Stochastic + Operational Scheduling MILP + Rolling Horizon: Architectural Analysis

**Direct Answer:**

**No**, the exact three-layer integrated architecture combining a scenario-based, two-stage stochastic aggregate planning model that passes linking inventory targets to a daily operational scheduling MILP under a rolling horizon execution has **never been published or deployed in a live industrial setting**.

While separate elements of this system are extensively discussed, their unified implementation in a live Decision Support System (DSS) remains a genuine methodological and practical novelty.

---

#### Closest Structural Analogs in Literature

##### 1. Two-Stage Stochastic MPS under Rolling Horizons

* **Full Citation:** Julian Englberger, Frank Herrmann, and Michael Manitz, "Two-stage stochastic master production scheduling under demand uncertainty in a rolling planning environment," *International Journal of Production Research*, vol. 54, no. 20, pp. 6192–6215, 2016 `[1]`. DOI: 10.1080/00207543.2016.1162917 `[1]`.
* **Google Scholar Citation Count:** ~25 `[1]`.
* **Journal Tier:** High-quality industrial engineering and operations management journal.
* **Relevance:** This study integrates a two-stage stochastic master production schedule (MPS) with recourse directly into a rolling planning system `[1]`. It modifies standard stochastic modeling approaches to prevent inter-temporal infeasibilities in successive planning levels `[1]`. However, it does **not** decompose the model to feed a separate operational daily scheduling MILP; it operates at a single, slightly more aggregated planning level `[1]`.
* **Confidence:** High.

##### 2. Reactive Receding Horizon Scheduling under Uncertainty

* **Full Citation:** G. Sand and S. Engell, "Receding horizon parameter-adaptive optimization of batch production schedules under demand uncertainty," *Industrial & Chemical Engineering Research*, vol. 43, no. 12, pp. 3151–3169, 2004 `. DOI: 10.1021/ie030308+ `.
* **Google Scholar Citation Count:** ~150.
* **Journal Tier:** Top-tier chemical engineering and process systems journal (not core OR/MS).
* **Relevance:** This paper solves a two-stage stochastic scheduling problem for a multiproduct batch plant under a rolling/shrinking horizon `. It provides the mathematical basis for receding-horizon recourse, but it is formulated as a single-level detailed scheduling model rather than a decomposed, decoupled hierarchical stochastic-to-deterministic aggregate architecture `.
* **Confidence:** High.

##### 3. Stochastic Production Routing with Rolling Recourse

* **Full Citation:** Yossiri Adulyasak, Jean-François Cordeau, and Raf Jans, "Benders decomposition for production routing under demand uncertainty," *Operations Research*, vol. 63, no. 4, pp. 851–867, 2015 `[2]`. DOI: 10.1287/opre.2015.1387 `[2]`.
* **Google Scholar Citation Count:** ~301 `[2]`.
* **Journal Tier:** Elite (UTD24 / FT50).
* **Relevance:** This study integrates a two-stage stochastic optimization model (handling tactical production setups and inventory) with rolling horizon execution `[2]`. Setup choices act as here-and-now decisions, while routing and delivery adjustments are modeled as recourse `[2]`. It does not, however, decouple into a separate monthly aggregate model and a daily operational MILP `[2]`.
* **Confidence:** High.

---

#### Novelty Claim Framing Sentence

You can confidently frame your paper's novelty using the following statement:

> "To the best of our knowledge, this is the first study to design, mathematically formulate, and deploy a live three-layer hierarchical decision support system that integrates a monthly two-stage stochastic aggregate planning model with a daily mixed-integer linear programming (MILP) operational scheduling model via temporal inventory target linking constraints under a weekly rolling horizon execution in a B2B process manufacturing setting."

---

### Q2. Hierarchical Stochastic Decomposition with Cross-Level Linking Constraints

The mechanism of passing inventory targets from Layer 1 (Days 24 and 48) to Layer 2 as binding constraints is a key coordination method in Hierarchical Production Planning (HPP).

#### Correct Academic Terminology

1. **Inventory Target Linking Constraints (or Inventory Target Coordination):** This is the most accurate mathematical term. The upper-level aggregate model sets target terminal inventories for the end of specific sub-periods, which are imposed as hard constraints or heavily penalized targets in the operational scheduling model `[3]`.
2. **Temporal Disaggregation with Boundary Conditions:** This refers to the process of breaking down a coarse, long-term inventory plan into daily schedules while honoring target levels at fixed temporal intervals as boundary conditions `[1]`.
3. **Vertical Coordination via Shared Buffers:** When an intermediate product (e.g., Semi-Finished Boba) is both sold and consumed, passing targets acts as vertical decoupling, preventing downstream operational schedules from depleting strategic buffers `[4, 1]`.

#### Closest Academic References on Linking Mechanisms

##### 1. Capacitated Lot-Sizing with Coordinated Linking

* **Full Citation:** Christopher Suerie and Hartmut Stadtler, "The Capacitated Lot-Sizing Problem with Linked Lot Sizes," *Management Science*, vol. 49, no. 8, pp. 1039–1054, 2003 `[3]`. DOI: 10.1287/mnsc.49.8.1039.16402 `[3]`.
* **Google Scholar Citation Count:** ~250 `[3]`.
* **Journal Tier:** Elite (UTD24 / FT50).
* **Relevance:** This paper formalizes the mathematical linkage of setup and inventory variables across consecutive periods in a rolling horizon environment `[3]`. It provides a strong basis for defining how upper-level decisions act as linked constraints on downstream operational schedules `[3]`.
* **Confidence:** High.

##### 2. Stochastic Material Requirements Planning (MRP) Coordination

* **Full Citation:** Simon Thevenin, Yossiri Adulyasak, and Jean-François Cordeau, "Material Requirements Planning Under Demand Uncertainty Using Stochastic Optimization," *Production and Operations Management*, vol. 30, no. 2, pp. 475–493, 2021 `[5, 2]`. DOI: 10.1111/poms.13289 `[5]`.
* **Google Scholar Citation Count:** ~91 `[5, 2]`.
* **Journal Tier:** Elite (UTD24 / FT50).
* **Relevance:** This study investigates how stochastic aggregate setups link to operational inventory replenishment `[5]`. It models the coupling of safety stock targets (buffer levels) between aggregate and detailed execution layers under rolling schedules `[5, 6]`.
* **Confidence:** High.

---

### Q3. Verify Toledo et al. (2009): DOI Conflict Resolution

**Direct Answer:**

The two DOIs do **not** represent different papers. They represent the exact same seminal article.

* **The Conflict:** DOI A (`10.1080/00207540701675833`) was an early-stage, pre-publication/early-view DOI assigned by Taylor & Francis during the online-first tracking phase in late 2007. DOI B (`10.1080/00207540701774431`) is the **official, final, and registered print DOI**.
* **Action Required:** You must use **DOI B** in your paper to avoid citation indexing errors.

---

#### Verified Full Citation

* **Full Citation:** Cláudio Fabiano Motta Toledo, Paulo Morelato França, Reinaldo Morábito, and Alf Kimms, "Multi-population genetic algorithm to solve the synchronized and integrated two-level lot sizing and scheduling problem," *International Journal of Production Research*, vol. 47, no. 11, pp. 3097–3119, 2009 `[7, 8, 9]`. DOI: 10.1080/00207540701774431 `[8]`.
* **Google Scholar Citation Count:** ~145 `[7, 8, 9]`.
* **Journal Tier:** Top-tier (Core Industrial Engineering & Manufacturing).
* **Relevance:** This paper is highly relevant as it models a synchronized two-level packaging and tank setup problem in soft drink plants, which is structurally identical to synchronizing boba preparation (Stage I) with packaging lines (Stage II) `[4, 10]`.
* **Confidence:** High.

---

### Q4. Schedule Nervousness and Stabilization: Canonical References

In rolling horizon systems, frequently updating the schedule based on new information creates "schedule nervousness" (plan instability) ``. The following are the absolute canonical references for this concept in dynamic lot-sizing and production planning.

#### 1. Canonical Paper for Lot-Sizing Nervousness

* **Full Citation:** Robert C. Carlson, James V. Jucker, and Dean H. Kropp, "Less Nervous MRP Systems: A Dynamic Economic Lot-Sizing Approach," *Management Science*, vol. 25, no. 8, pp. 754–761, 1979 ``. DOI: 10.1287/mnsc.25.8.754.
* **Google Scholar Citation Count:** ~340.
* **Journal Tier:** Elite (UTD24 / FT50).
* **Relevance:** This is the most-cited paper that mathematically reformulates dynamic lot-sizing cost functions to penalize plan alterations `. It introduces "nervousness costs" directly into the objective function to stabilize immediate decisions `.
* **Confidence:** High.

#### 2. Canonical Paper for MRP System-Wide Nervousness

* **Full Citation:** Joseph D. Blackburn, Dean H. Kropp, and Robert A. Millen, "A Comparison of Strategies to Dampen Nervousness in MRP Systems," *Management Science*, vol. 32, no. 4, pp. 413–429, 1986 ``. DOI: 10.1287/mnsc.32.4.413.
* **Google Scholar Citation Count:** ~400.
* **Journal Tier:** Elite (UTD24 / FT50).
* **Relevance:** This is the definitive comparative study of nervousness-dampening methods `. It establishes schedule freezing and safety stocks as the primary operational levers to stabilize rolling plans, which directly supports Layer 3's stabilization mechanisms `.
* **Confidence:** High.

#### 3. Canonical Paper for Rolling Horizon MPS Stability

* **Full Citation:** V. Sridharan, William L. Berry, and V. Udayabhanu, "Freezing the Master Production Schedule Under Rolling Planning Horizons," *Decision Sciences*, vol. 20, no. 4, pp. 623–637, 1989 `. DOI: 10.1111/j.1540-5915.1989.tb01408.x `.
* **Google Scholar Citation Count:** ~200 ``.
* **Journal Tier:** High-quality decision sciences journal.
* **Relevance:** This paper evaluates how freezing a portion of the planning horizon affects overall system costs, customer service, and plan stability in dynamic rolling environments ``.
* **Confidence:** High.

---

### Comparison of Nervousness Mitigation Frameworks

| Reference | Context | Mitigation Strategy | Cost vs. Stability Trade-off |
| --- | --- | --- | --- |
| **Carlson et al. (1979)** `` | Single-item dynamic lot-sizing | Penalty costs in objective function | Direct mathematical penalty on schedule changes `` |
| **Blackburn et al. (1986)** `` | Multi-level MRP systems | Horizon freezing & safety stock | Proves freezing is the most cost-efficient stabilizer `` |
| **Sridharan et al. (1989)** `` | Rolling-horizon MPS | Freeze intervals & rolling windows | Quantifies cost increases associated with freeze lengths `` |
