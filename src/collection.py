from datetime import datetime

from .utils import random_hex


# Define and return Collection class model
# Function was needed, because db is required in inheritance
def get_Collection_class(db, products_collection_table):
    class Collection(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False)
        short_description = db.Column(db.String, nullable=False, default='')
        description = db.Column(db.String, nullable=False, default='')
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        products = db.relationship(
            'Product',
            secondary=products_collection_table,
            lazy='subquery'
        )

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'short_description': self.short_description,
                'description': self.description
            }
    return Collection


# Return Collection rest resource
