import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from models import db, Product, Location, ProductMovement

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///inventory.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("report"))

    # Products
    @app.route("/products")
    def product_list():
        products = Product.query.order_by(Product.product_id.asc()).all()
        return render_template("product_list.html", products=products)

    @app.route("/products/new", methods=["GET", "POST"])
    def product_new():
        if request.method == "POST":
            product_id = request.form.get("product_id", "").strip()
            name = request.form.get("name", "").strip()
            if not product_id or not name:
                flash("Product ID and Name are required.", "danger")
                return render_template("product_form.html", product=None)
            if Product.query.get(product_id):
                flash("Product ID already exists.", "danger")
                return render_template("product_form.html", product=None)

            p = Product(product_id=product_id, name=name)
            db.session.add(p)
            db.session.commit()
            flash("Product created.", "success")
            return redirect(url_for("product_list"))
        return render_template("product_form.html", product=None)

    @app.route("/products/<product_id>/edit", methods=["GET", "POST"])
    def product_edit(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Product Name is required.", "danger")
                return render_template("product_form.html", product=product)
            product.name = name
            db.session.commit()
            flash("Product updated.", "success")
            return redirect(url_for("product_list"))
        return render_template("product_form.html", product=product)

    @app.route("/products/<product_id>/delete", methods=["POST"])
    def product_delete(product_id):
        product = Product.query.get_or_404(product_id)
        # Optional: prevent deletion if movements exist
        has_movements = ProductMovement.query.filter_by(product_id=product_id).first()
        if has_movements:
            flash("Cannot delete product with existing movements.", "warning")
            return redirect(url_for("product_list"))
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted.", "success")
        return redirect(url_for("product_list"))

    # Locations
    @app.route("/locations")
    def location_list():
        locations = Location.query.order_by(Location.location_id.asc()).all()
        return render_template("location_list.html", locations=locations)

    @app.route("/locations/new", methods=["GET", "POST"])
    def location_new():
        if request.method == "POST":
            location_id = request.form.get("location_id", "").strip()
            name = request.form.get("name", "").strip()
            if not location_id or not name:
                flash("Location ID and Name are required.", "danger")
                return render_template("location_form.html", location=None)
            if Location.query.get(location_id):
                flash("Location ID already exists.", "danger")
                return render_template("location_form.html", location=None)

            l = Location(location_id=location_id, name=name)
            db.session.add(l)
            db.session.commit()
            flash("Location created.", "success")
            return redirect(url_for("location_list"))
        return render_template("location_form.html", location=None)

    @app.route("/locations/<location_id>/edit", methods=["GET", "POST"])
    def location_edit(location_id):
        location = Location.query.get_or_404(location_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Location Name is required.", "danger")
                return render_template("location_form.html", location=location)
            location.name = name
            db.session.commit()
            flash("Location updated.", "success")
            return redirect(url_for("location_list"))
        return render_template("location_form.html", location=location)

    @app.route("/locations/<location_id>/delete", methods=["POST"])
    def location_delete(location_id):
        location = Location.query.get_or_404(location_id)
        has_movements = ProductMovement.query.filter(
            (ProductMovement.from_location == location_id) |
            (ProductMovement.to_location == location_id)
        ).first()
        if has_movements:
            flash("Cannot delete location with existing movements.", "warning")
            return redirect(url_for("location_list"))
        db.session.delete(location)
        db.session.commit()
        flash("Location deleted.", "success")
        return redirect(url_for("location_list"))

    # Movements
    @app.route("/movements")
    def movement_list():
        movements = (
            ProductMovement.query
            .order_by(ProductMovement.timestamp.desc(), ProductMovement.movement_id.desc())
            .limit(200)
            .all()
        )
        return render_template("movement_list.html", movements=movements)

    @app.route("/movements/new", methods=["GET", "POST"])
    def movement_new():
        products = Product.query.order_by(Product.product_id.asc()).all()
        locations = Location.query.order_by(Location.location_id.asc()).all()

        if request.method == "POST":
            product_id = request.form.get("product_id", "").strip()
            from_location = request.form.get("from_location", "").strip() or None
            to_location = request.form.get("to_location", "").strip() or None
            qty_raw = request.form.get("qty", "").strip()
            timestamp_raw = request.form.get("timestamp", "").strip()

            # Validation
            if not product_id or not Product.query.get(product_id):
                flash("Valid Product is required.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            if not from_location and not to_location:
                flash("Either From Location, To Location, or both must be provided.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            if from_location == to_location and from_location is not None:
                flash("From and To Location cannot be the same.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            if from_location and not Location.query.get(from_location):
                flash("From Location does not exist.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            if to_location and not Location.query.get(to_location):
                flash("To Location does not exist.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            try:
                qty = int(qty_raw)
                if qty <= 0:
                    raise ValueError()
            except ValueError:
                flash("Quantity must be a positive integer.", "danger")
                return render_template("movement_form.html", movement=None, products=products, locations=locations)

            if timestamp_raw:
                try:
                    ts = datetime.fromisoformat(timestamp_raw)
                except ValueError:
                    flash("Invalid timestamp format. Use YYYY-MM-DDTHH:MM:SS", "danger")
                    return render_template("movement_form.html", movement=None, products=products, locations=locations)
            else:
                ts = datetime.utcnow()

            m = ProductMovement(
                product_id=product_id,
                from_location=from_location,
                to_location=to_location,
                qty=qty,
                timestamp=ts,
            )
            db.session.add(m)
            db.session.commit()
            flash("Movement recorded.", "success")
            return redirect(url_for("movement_list"))

        return render_template("movement_form.html", movement=None, products=products, locations=locations)

    @app.route("/movements/<int:movement_id>/edit", methods=["GET", "POST"])
    def movement_edit(movement_id):
        movement = ProductMovement.query.get_or_404(movement_id)
        products = Product.query.order_by(Product.product_id.asc()).all()
        locations = Location.query.order_by(Location.location_id.asc()).all()

        if request.method == "POST":
            product_id = request.form.get("product_id", "").strip()
            from_location = request.form.get("from_location", "").strip() or None
            to_location = request.form.get("to_location", "").strip() or None
            qty_raw = request.form.get("qty", "").strip()
            timestamp_raw = request.form.get("timestamp", "").strip()

            if not product_id or not Product.query.get(product_id):
                flash("Valid Product is required.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            if not from_location and not to_location:
                flash("Either From Location, To Location, or both must be provided.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            if from_location == to_location and from_location is not None:
                flash("From and To Location cannot be the same.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            if from_location and not Location.query.get(from_location):
                flash("From Location does not exist.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            if to_location and not Location.query.get(to_location):
                flash("To Location does not exist.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            try:
                qty = int(qty_raw)
                if qty <= 0:
                    raise ValueError()
            except ValueError:
                flash("Quantity must be a positive integer.", "danger")
                return render_template("movement_form.html", movement=movement, products=products, locations=locations)

            if timestamp_raw:
                try:
                    ts = datetime.fromisoformat(timestamp_raw)
                except ValueError:
                    flash("Invalid timestamp format. Use YYYY-MM-DDTHH:MM:SS", "danger")
                    return render_template("movement_form.html", movement=movement, products=products, locations=locations)
            else:
                ts = datetime.utcnow()

            movement.product_id = product_id
            movement.from_location = from_location
            movement.to_location = to_location
            movement.qty = qty
            movement.timestamp = ts
            db.session.commit()
            flash("Movement updated.", "success")
            return redirect(url_for("movement_list"))

        return render_template("movement_form.html", movement=movement, products=products, locations=locations)

    # Report: Balance quantity in each location
    @app.route("/report")
    def report():
        # Concise SQL to compute balances per product-location
        sql = text("""
            SELECT
              p.product_id AS product_id,
              l.location_id AS location_id,
              COALESCE(SUM(CASE WHEN m.to_location = l.location_id THEN m.qty ELSE 0 END), 0) -
              COALESCE(SUM(CASE WHEN m.from_location = l.location_id THEN m.qty ELSE 0 END), 0) AS qty
            FROM product p
            CROSS JOIN location l
            LEFT JOIN product_movement m
              ON m.product_id = p.product_id
             AND (m.to_location = l.location_id OR m.from_location = l.location_id)
            GROUP BY p.product_id, l.location_id
            ORDER BY p.product_id, l.location_id
        """)
        rows = db.session.execute(sql).mappings().all()
        # rows: list of dicts with keys product_id, location_id, qty
        return render_template("report.html", rows=rows)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
