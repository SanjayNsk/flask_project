# Flask Inventory Management App

A simple, well-structured Flask application to manage inventory across warehouses. It implements:
- Products (Add / Edit / View)
- Locations (Add / Edit / View)
- Product Movements (Add / Edit / View) supporting inbound, outbound, and transfer
- Report: balance quantity per Product per Warehouse

## Tech
- Flask + SQLAlchemy
- SQLite by default; switch to MySQL via `DATABASE_URL`
- Bootstrap for clean UI

## Quick Start (SQLite)
1. Create a virtual environment and install dependencies:
   - `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
   - `pip install -r requirements.txt`
2. (Optional) Copy `.env.example` to `.env`, and set `SECRET_KEY`.
3. Seed sample data:
   - `python scripts/seed_data.py`
4. Run the app:
   - `export FLASK_APP=app.py && flask run` (Windows: `set FLASK_APP=app.py && flask run`)
5. Open http://127.0.0.1:5000

## MySQL (Optional)
Set `DATABASE_URL` in `.env` like:
\`\`\`
DATABASE_URL=mysql+pymysql://username:password@host:3306/database_name
\`\`\`
Then re-run `python scripts/seed_data.py` to initialize tables and data.

## Use Cases Covered
- Create 3/4 Products
- Create 3/4 Locations
- Make ~20 Product Movements including:
  - Move Product A to Location X
  - Move Product B to Location X
  - Move Product A from Location X to Location Y
- View the balance report with columns: Product, Warehouse, Qty

## Screens to Capture for Submission
- Products list and form
- Locations list and form
- Movements list and form
- Balance report

Add your screenshots to the README (e.g., `docs/`) before pushing to GitHub.

## Notes
- Primary keys for Product and Location are text/varchar.
- Movement supports inbound (to only), outbound (from only), or transfer (both).
- The balance report uses a concise SQL that works for SQLite/MySQL.

Good luck with your evaluation!
