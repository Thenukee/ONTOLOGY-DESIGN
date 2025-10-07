#!/usr/bin/env python3
"""
Run the Bookstore Management System (BMS) simulation.

Usage:
  python run_simulation.py --steps 200 --seed 42
"""
import argparse, os, sys, json
from pathlib import Path

from bms_model.model import BookstoreModel
from bms_model.scenarios import DEFAULT_SCENARIO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=200, help="Number of simulation steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default="output", help="Output directory")
    args = parser.parse_args()

    model = BookstoreModel(seed=args.seed, scenario=DEFAULT_SCENARIO)
    model.run_for(args.steps)

    # Persist results & ontology snapshot
    out_dir = Path(args.out) / "run_logs"
    csv_path = model.persist_results(str(out_dir))
    onto_path = Path(args.out) / "ontology" / "bookstore.owl"
    model.save_ontology_snapshot(str(onto_path))

    # Print summary
    print("=== Simulation Summary ===")
    print(f"Steps: {args.steps}")
    print(f"Revenue: {model.revenue:.2f}")
    print(f"Fulfilled orders: {model.fulfilled_orders}")
    print(f"Rejected orders: {model.rejected_orders}")
    print(f"Restock actions: {model.restock_actions}")
    print(f"Avg inventory (final step): {model.avg_inventory():.2f}")
    print(f"Metrics CSV: {csv_path}")
    print(f"Ontology snapshot: {onto_path}")

if __name__ == "__main__":
    main()
