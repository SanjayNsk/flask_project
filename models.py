from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "product"
    product_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Location(db.Model):
    __tablename__ = "location"
    location_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class ProductMovement(db.Model):
    __tablename__ = "product_movement"
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    from_location = db.Column(
        db.String(64), db.ForeignKey("location.location_id"), nullable=True
    )
    to_location = db.Column(
        db.String(64), db.ForeignKey("location.location_id"), nullable=True
    )

    product_id = db.Column(
        db.String(64), db.ForeignKey("product.product_id"), nullable=False
    )
    qty = db.Column(db.Integer, nullable=False)

    # Optional relationships for convenience (not strictly required)
    product = db.relationship("Product", backref="movements", lazy="joined")
    from_loc = db.relationship("Location", foreign_keys=[from_location], lazy="joined")
    to_loc = db.relationship("Location", foreign_keys=[to_location], lazy="joined")
