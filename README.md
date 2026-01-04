# Ontology‑Driven Bookstore Management System (BMS)
**Owlready2 + SWRL + Mesa (Python)**

This is the reference implementation matching the assignment brief. It contains:
- An **OWL ontology** (Owlready2) with **SWRL rules** for purchase attribution and low‑stock inference.
- A **multi‑agent simulation** (Mesa) with **Customer**, **Employee**, and **Book** agents communicating over a simple **message bus**.
- **KPIs** collected each step and exported to CSV, plus an ontology snapshot for evidence.

## 1) Install
> Python 3.10+ recommended
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install owlready2 mesa pandas numpy matplotlib
```

## 2) Run
```bash
python run_simulation.py --steps 200 --seed 42
```
Outputs are written to `output/run_logs/metrics.csv` and `output/ontology/bookstore.owl`.

## 3) Files
```
bms/
├─ bms_model/
│  ├─ ontology.py      # Ontology + SWRL
│  ├─ bus.py           # Message bus
│  ├─ agents.py        # CustomerAgent, EmployeeAgent, BookAgent
│  ├─ model.py         # BookstoreModel + KPIs
│  └─ scenarios.py     # DEFAULT_SCENARIO
├─ run_simulation.py
└─ README.md
```

## 4) Evidence to capture for the report
1. Screenshot of classes/properties and SWRL rules in `ontology.py` (or load saved `bookstore.owl` in Protégé).
2. Console summary after a run.
3. A quick plot of `revenue` and `avg_inventory` from `output/run_logs/metrics.csv`.
4. Inspect individuals (Orders, LowStock) in the snapshot to show inferences occurred.

## 5) Notes
- SWRL handles **inference** (e.g., `purchases(Customer, Book)`, `LowStock(InventoryItem)`); quantity increments/decrements are done by the **agents** on commit.
- The reasoner is invoked per step; if a Java reasoner is not available, the model still runs (restocking can be handled without inference, but SWRL inferences will be visible when reasoner is available).



















bms/
├─ bms_model/
│  ├─ ontology.py      # Ontology + SWRL
│  ├─ bus.py           # Message bus
│  ├─ agents.py        # CustomerAgent, EmployeeAgent, BookAgent
│  ├─ model.py         # BookstoreModel 
│  └─ scenarios.py     # DEFAULT_SCENARIO
├─ run_simulation.py
└─ README.md
