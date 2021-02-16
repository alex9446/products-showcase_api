from datetime import datetime

from .utils import random_hex


# Define and return Product class model
# Function was needed, because db is required in inheritance
def get_Product_class(db):
    class Product(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False)
        sku = db.Column(db.String, nullable=False)
        description = db.Column(db.String, nullable=False, default='')
        price = db.Column(db.Float, nullable=True)
        discount_percent = db.Column(db.Float, nullable=True)
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'sku': self.sku,
                'description': self.description,
                'price': self.price,
                'discount_percent': self.discount_percent,
            }
    return Product
