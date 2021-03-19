from datetime import datetime

# from flask_restful import Resource, reqparse

# from .utils import (check_allowed_role, db_add_and_commit,
#                     db_delete_and_commit, model_to_dict, random_hex,
#                     status_error, status_ok, status_user_401)
from .utils import random_hex


# Define and return Collection class model
# Function was needed, because db is required in inheritance
def get_Collection_class(db):
    # Define many-to-many relationships table
    products_in_collection = db.Table(
        db.Column('product_id', db.String,
                  db.ForeignKey('product.id'), primary_key=True),
        db.Column('collection_id', db.String,
                  db.ForeignKey('collection.id'), primary_key=True),
        db.Column('position', db.Integer, nullable=False, default=0)
    )

    class Collection(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False)
        short_description = db.Column(db.String, nullable=False, default='')
        description = db.Column(db.String, nullable=False, default='')
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        # products = db.relationship('product',
        #                            secondary=products_in_collection,
        #                            lazy='subquery')

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'short_description': self.short_description,
                'description': self.description
            }
    return Collection


# Return Collection rest resource
