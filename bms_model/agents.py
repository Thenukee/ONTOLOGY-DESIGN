from __future__ import annotations
from typing import List, Dict, Any, Optional
from mesa import Agent
from .ontology import onto, new_order

# Topics used by the MessageBus
PURCHASE_REQUEST = "PURCHASE_REQUEST"
PURCHASE_COMMIT = "PURCHASE_COMMIT"
PURCHASE_REJECTED = "PURCHASE_REJECTED"
RESTOCK_DONE = "RESTOCK_DONE"

class CustomerAgent(Agent):
    def __init__(self, unique_id: str, model, prefs: List[str], budget: float):
        # Mesa 3.0.3 Agent signature is Agent(model). We then overwrite unique_id for readability
        super().__init__(model)
        self.unique_id = unique_id  # override auto integer id with provided string id
        self.prefs = prefs or []
        self.budget = float(budget)

    def _choose_book(self):
        # Weight by preference where possible
        books = onto.Book.instances()
        if not books:
            return None
        preferred = [b for b in books if b.hasGenre and b.hasGenre[0] in self.prefs]
        pool = preferred if preferred else books
        return self.random.choice(pool)

    def step(self):
        # 60% chance to attempt a purchase
        if self.random.random() < 0.6 and self.budget > 0:
            b = self._choose_book()
            if not b or not b.hasPrice:
                return
            price = float(b.hasPrice)
            if self.budget >= price:
                payload = {
                    "book_name": b.name,
                    "qty": 1,
                    "price": price,
                    "customer_id": self.unique_id,
                    "t": self.model.schedule.time
                }
                self.model.bus.publish("PURCHASE_REQUEST", {
                    "type": PURCHASE_REQUEST,
                    "sender": self.unique_id,
                    "receiver": "checkout",
                    "payload": payload
                })

class EmployeeAgent(Agent):
    def __init__(self, unique_id: str, model, restock_amount: int = 10):
        super().__init__(model)
        self.unique_id = unique_id
        self.restock_amount = int(restock_amount)

    def _process_purchase(self, payload: Dict[str, Any]):
        book_ind = self.model.book_inds.get(payload["book_name"])
        if not book_ind:
            self.model.rejected_orders += 1
            self.model.bus.publish(PURCHASE_REJECTED, {"reason": "UnknownBook", "payload": payload})
            return

        inv = self.model.inventory_by_book.get(book_ind.name)
        if inv and inv.availableQuantity and int(inv.availableQuantity) >= 1:
            # Decrement quantity
            inv.availableQuantity = int(inv.availableQuantity) - 1

            # Create customer and employee individuals if not already
            cust = self.model.customer_inds.get(payload["customer_id"])
            if not cust:
                cust = self.model.ensure_customer(payload["customer_id"])

            emp = self.model.employee_inds.get(self.unique_id)
            if not emp:
                emp = self.model.ensure_employee(self.unique_id)

            order_name = f"order_{self.model.order_seq}"
            self.model.order_seq += 1
            o = new_order(order_name, book_ind, cust, emp, total=float(payload["price"]))
            self.model.revenue += float(payload["price"])
            self.model.fulfilled_orders += 1
            self.model.last_orders.append(o.name)
            self.model.bus.publish(PURCHASE_COMMIT, {"order": o.name, "payload": payload})
        else:
            self.model.rejected_orders += 1
            self.model.bus.publish(PURCHASE_REJECTED, {"reason": "OutOfStock", "payload": payload})

    def _restock_low_items(self):
        # After reasoning, LowStock items are instances of LowStock
        lows = list(onto.LowStock.instances())
        for inv in lows:
            current = int(inv.availableQuantity) if inv.availableQuantity else 0
            inv.availableQuantity = current + self.restock_amount
            self.model.restock_actions += 1
            self.model.bus.publish(RESTOCK_DONE, {"inventory": inv.name, "new_qty": int(inv.availableQuantity)})

    def step(self):
        # Process all purchase requests this step
        for msg in self.model.bus.drain(PURCHASE_REQUEST):
            self._process_purchase(msg["payload"])

        # Run reasoner (to infer LowStock using SWRL)
        self.model.reason()

        # Restock any LowStock items
        self._restock_low_items()

class BookAgent(Agent):
    def __init__(self, unique_id: str, model, book_ind):
        super().__init__(model)
        self.unique_id = unique_id
        self.book = book_ind

    def step(self):
        # Placeholder for dynamic behavior (e.g., pricing strategy)
        pass
