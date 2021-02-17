from datetime import datetime

from flask_restful import Resource

from .utils import model_to_dict, random_hex, status_error, status_ok


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


# Return Product rest resource
class ProductRest(Resource):
    @classmethod
    def add_Product(cls, db, Product):
        cls.db = db
        cls.Product = Product
        return cls

    def get_first_by_id(self, id: str):
        return self.Product.query.filter_by(id=id).first()

    def get(self, id: str = None) -> tuple:
        if id:
            product = self.get_first_by_id(id)
            if product:
                return status_ok(product=product.to_dict())
            return self.status_product_404()
        return status_ok(products=model_to_dict(self.Product))

    @staticmethod
    def status_product_404() -> tuple:
        return status_error(error_code=404, message='Product not found!')
