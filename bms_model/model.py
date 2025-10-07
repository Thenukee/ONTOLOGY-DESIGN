from __future__ import annotations
from typing import Dict, Any, List
import os
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from .bus import MessageBus
from .agents import CustomerAgent, EmployeeAgent, BookAgent, PURCHASE_REQUEST
from .ontology import (
    onto, new_store, new_book, new_inventory, new_customer, new_employee, save_ontology, run_reasoner
)

class BookstoreModel(Model):
    def __init__(self, seed: int, scenario: Dict[str, Any]):
        super().__init__()
        self.random.seed(seed)
        self.bus = MessageBus()
        self.schedule = RandomActivation(self)

        self.revenue: float = 0.0
        self.fulfilled_orders: int = 0
        self.rejected_orders: int = 0
        self.restock_actions: int = 0
        self.order_seq: int = 1
        self.last_orders: List[str] = []

        # Ontology individuals and indices
        self.store = new_store("main_store")
        self.book_inds: Dict[str, Any] = {}
        self.inventory_by_book: Dict[str, Any] = {}
        self.customer_inds: Dict[str, Any] = {}
        self.employee_inds: Dict[str, Any] = {}

        self._seed_entities_and_agents(scenario)

        self.datacollector = DataCollector(
            model_reporters={
                "revenue": lambda m: m.revenue,
                "orders_fulfilled": lambda m: m.fulfilled_orders,
                "orders_rejected": lambda m: m.rejected_orders,
                "restock_actions": lambda m: m.restock_actions,
                "avg_inventory": lambda m: m.avg_inventory(),
            }
        )

    # --- Seeding helpers ---
    def _seed_entities_and_agents(self, sc: Dict[str, Any]):
        # Books + inventory + BookAgents
        for b in sc.get("books", []):
            bk = new_book(b["name"], b["author"], b["genre"], b["price"])
            inv = new_inventory(f"inv_{b['name']}", bk, b["qty"], b.get("threshold", 5))
            self.book_inds[bk.name] = bk
            self.inventory_by_book[bk.name] = inv
            a = BookAgent(f"book_{bk.name}", self, bk)
            self.schedule.add(a)

        # Employees
        for i, emp in enumerate(sc.get("employees", []), start=1):
            a = EmployeeAgent(f"emp_{i}", self, restock_amount=emp.get("amount", 10))
            self.schedule.add(a)
            # ensure Employee individual
            ind = new_employee(a.unique_id, self.store)
            self.employee_inds[a.unique_id] = ind
            self.bus.subscribe(PURCHASE_REQUEST, a.unique_id)

        # Customers
        for i, c in enumerate(sc.get("customers", []), start=1):
            uid = f"cust_{i}"
            a = CustomerAgent(uid, self, c.get("prefs", []), c.get("budget", 50.0))
            self.schedule.add(a)
            # ensure Customer individual
            ind = new_customer(uid)
            self.customer_inds[uid] = ind

    # --- Convenience ---
    def ensure_customer(self, uid: str):
        if uid in self.customer_inds:
            return self.customer_inds[uid]
        ind = new_customer(uid)
        self.customer_inds[uid] = ind
        return ind

    def ensure_employee(self, uid: str):
        if uid in self.employee_inds:
            return self.employee_inds[uid]
        ind = new_employee(uid, self.store)
        self.employee_inds[uid] = ind
        return ind

    def avg_inventory(self) -> float:
        invs = [int(inv.availableQuantity) for inv in self.inventory_by_book.values() if inv.availableQuantity]
        return sum(invs) / len(invs) if invs else 0.0

    def reason(self):
        try:
            run_reasoner()
        except Exception as e:
            # In case reasoner is not available in the environment,
            # the simulation still runs; low-stock can be handled via direct check.
            pass

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_for(self, steps: int):
        for _ in range(int(steps)):
            self.step()

    def persist_results(self, out_dir: str):
        """Save KPIs CSV and ontology snapshot"""
        os.makedirs(out_dir, exist_ok=True)
        model_df = self.datacollector.get_model_vars_dataframe()
        csv_path = os.path.join(out_dir, "metrics.csv")
        model_df.to_csv(csv_path, index_label="step")
        return csv_path

    def save_ontology_snapshot(self, out_path: str):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        save_ontology(out_path)
