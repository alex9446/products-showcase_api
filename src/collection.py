from datetime import datetime

from .utils import random_hex, records_to_dict


# Define many-to-one relationships to product with position
def get_ProductWithPosition_class(db):
    class ProductWithPosition(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        product_id = db.Column(db.String, db.ForeignKey('product.id'))
        product = db.relationship('Product')
        collection_id = db.Column(db.String, db.ForeignKey('collection.id'))
        position = db.Column(db.Integer, nullable=False, default=0)

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                # 'product': records_to_dict(self.product),
                'product': self.product.to_dict(),
                'position': self.position
            }
    return ProductWithPosition


# Define and return Collection class model
# Function was needed, because db is required in inheritance
def get_Collection_class(db):
    class Collection(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False)
        short_description = db.Column(db.String, nullable=False, default='')
        description = db.Column(db.String, nullable=False, default='')
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        products_positions = db.relationship('ProductWithPosition')

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'short_description': self.short_description,
                'description': self.description,
                'products_positions': records_to_dict(self.products_positions)
            }
    return Collection


# Return Collection rest resource
