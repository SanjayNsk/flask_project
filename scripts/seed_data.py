import os
from datetime import datetime, timedelta
from app import create_app, db, Product, Location, ProductMovement

"""
Run:
  # Ensure venv and dependencies are installed
  # Copy .env.example to .env and set variables if needed
  python scripts/seed_data.py
"""

def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create 4 products
        products = [
            Product(product_id="PROD-A", name="Product A"),
            Product(product_id="PROD-B", name="Product B"),
            Product(product_id="PROD-C", name="Product C"),
            Product(product_id="PROD-D", name="Product D"),
        ]
        db.session.add_all(products)

        # Create 4 locations
        locations = [
            Location(location_id="LOC-X", name="Warehouse X"),
            Location(location_id="LOC-Y", name="Warehouse Y"),
            Location(location_id="LOC-Z", name="Warehouse Z"),
            Location(location_id="LOC-Q", name="Warehouse Q"),
        ]
        db.session.add_all(locations)
        db.session.commit()

        now = datetime.utcnow()

        # Required sample use cases:
        # Move Product A to Location X
        db.session.add(ProductMovement(product_id="PROD-A", to_location="LOC-X", qty=10, timestamp=now))
        # Move Product B to Location X
        db.session.add(ProductMovement(product_id="PROD-B", to_location="LOC-X", qty=5, timestamp=now + timedelta(minutes=1)))
        # Move Product A from Location X to Location Y
        db.session.add(ProductMovement(product_id="PROD-A", from_location="LOC-X", to_location="LOC-Y", qty=4, timestamp=now + timedelta(minutes=2)))

        # Additional movements to total ~20
        extra = [
            # Inbounds
            ("PROD-C", None, "LOC-Z", 12),
            ("PROD-D", None, "LOC-Q", 7),
            ("PROD-A", None, "LOC-X", 3),
            ("PROD-B", None, "LOC-Y", 9),
            # Transfers
            ("PROD-C", "LOC-Z", "LOC-Y", 5),
            ("PROD-D", "LOC-Q", "LOC-X", 2),
            ("PROD-B", "LOC-X", "LOC-Z", 3),
            # Outbounds
            ("PROD-A", "LOC-Y", None, 2),
            ("PROD-C", "LOC-Y", None, 1),
            ("PROD-D", "LOC-X", None, 1),
            # More variety
            ("PROD-A", "LOC-X", "LOC-Q", 3),
            ("PROD-B", None, "LOC-Q", 6),
            ("PROD-C", "LOC-Y", "LOC-Z", 2),
            ("PROD-D", None, "LOC-X", 4),
            ("PROD-A", "LOC-Q", None, 1),
            ("PROD-B", "LOC-Q", "LOC-X", 2),
        ]

        for i, (pid, frm, to, qty) in enumerate(extra, start=3):
            db.session.add(ProductMovement(
                product_id=pid,
                from_location=frm,
                to_location=to,
                qty=qty,
                timestamp=now + timedelta(minutes=i)
            ))

        db.session.commit()
        print("[seed] Seeded products, locations, and ~20 movements.")

if __name__ == "__main__":
    seed()
