"""
Ontology module for the Bookstore Management System (BMS).
Uses Owlready2 to define classes, properties and SWRL rules.
"""
from typing import Optional
from owlready2 import (
    get_ontology, Thing, DataProperty, ObjectProperty, FunctionalProperty,
    Imp, sync_reasoner, default_world , swrl
)


try:
    from owlready2 import sync_reasoner_pellet as _sync_reasoner_impl
except Exception:
    _sync_reasoner_impl = sync_reasoner

IRI = "http://example.org/bookstore.owl"
onto = get_ontology(IRI)

with onto:
    # === Classes ===
    class Store(Thing): pass
    class Book(Thing): pass
    class Customer(Thing): pass
    class Employee(Thing): pass
    class Order(Thing): pass
    class InventoryItem(Thing): pass
    class LowStock(Thing): pass  # inferred

    # === Object Properties ===
    class holds(ObjectProperty): 
        domain = [InventoryItem]
        range = [Book]
    class purchasedBook(ObjectProperty, FunctionalProperty):
        domain = [Order]
        range = [Book]
    class placedBy(ObjectProperty, FunctionalProperty):
        domain = [Order]
        range = [Customer]
    class handledBy(ObjectProperty):
        domain = [Order]
        range = [Employee]
    class worksAt(ObjectProperty):
        domain = [Employee]
        range = [Store]
    class restocks(ObjectProperty):
        domain = [Employee]
        range = [InventoryItem]
    class purchases(ObjectProperty):
        domain = [Customer]
        range = [Book]

    # === Data Properties ===
    class hasAuthor(DataProperty, FunctionalProperty):
        domain = [Book]
        range = [str]
    class hasGenre(DataProperty):
        domain = [Book]
        range = [str]
    class hasPrice(DataProperty, FunctionalProperty):
        domain = [Book]
        range = [float]
    class availableQuantity(DataProperty, FunctionalProperty):
        domain = [InventoryItem]
        range = [int]
    class restockThreshold(DataProperty, FunctionalProperty):
        domain = [InventoryItem]
        range = [int]
    class orderTotal(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [float]

    # === SWRL Rules ===
    # R1: If an Order is placedBy a Customer and purchasedBook a Book -> purchases(Customer, Book)
    r1 = Imp()
    r1.set_as_rule("""
        Order(?o) ^ placedBy(?o, ?c) ^ purchasedBook(?o, ?b) -> purchases(?c, ?b)
    """)

    # R2: If availableQuantity < restockThreshold -> LowStock(InventoryItem)
    r2 = Imp()
    r2.set_as_rule("""
    InventoryItem(?i) ^ availableQuantity(?i, ?q) ^ restockThreshold(?i, ?th) ^ lessThan(?q, ?th) -> LowStock(?i)
    """)

def new_store(name: str) -> 'Store':
    return onto.Store(name)

def new_book(name: str, author: str, genre: str, price: float) -> 'Book':
    b = onto.Book(name)
    # Functional data properties should be assigned scalar values, not lists
    b.hasAuthor = author
    b.hasGenre.append(genre)
    b.hasPrice = float(price)
    return b

def new_inventory(name: str, book: 'Book', qty: int, threshold: int = 5) -> 'InventoryItem':
    inv = onto.InventoryItem(name)
    inv.holds = [book]
    inv.availableQuantity = int(qty)
    inv.restockThreshold = int(threshold)
    return inv

def new_customer(name: str) -> 'Customer':
    return onto.Customer(name)

def new_employee(name: str, store: Optional['Store'] = None) -> 'Employee':
    e = onto.Employee(name)
    if store:
        e.worksAt.append(store)
    return e

def new_order(name: str, book: 'Book', customer: 'Customer', employee: 'Employee', total: float) -> 'Order':
    o = onto.Order(name)
    # Functional object properties also take single values
    o.purchasedBook = book
    o.placedBy = customer
    o.handledBy.append(employee)
    o.orderTotal = float(total)
    return o

def save_ontology(path: str):
    path = str(path)
    default_world.save(file=path, format="rdfxml")

def run_reasoner():
    """
    Try to run the built-in Owlready2 reasoner. On systems without Java/Pellet,
    this will raise; callers should catch exceptions if needed.
    """
    _sync_reasoner_impl(infer_property_values=True, infer_data_property_values=True, debug=0)
