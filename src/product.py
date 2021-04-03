from datetime import datetime

from flask_restful import Resource, reqparse

from .utils import (check_allowed_role, db_add_and_commit,
                    db_delete_and_commit, model_to_dict, random_hex,
                    records_to_dict, status_error, status_ok, status_user_401)


# Define and return Product class model
# Function was needed, because db is required in inheritance
def get_Product_class(db):
    class Product(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False)
        sku = db.Column(db.String, nullable=False, unique=True)
        description = db.Column(db.String, nullable=False, default='')
        price = db.Column(db.Float, nullable=True)
        discount_percent = db.Column(db.Float, nullable=True)
        position = db.Column(db.Integer, nullable=False, default=0)
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        images = db.relationship('ProductImages', lazy=True,
                                 cascade='all, delete, delete-orphan')

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'sku': self.sku,
                'description': self.description,
                'price': self.price,
                'discount_percent': self.discount_percent,
                'position': self.position,
                'images': records_to_dict(self.images)
            }
    return Product


# Define and return ProductImages class model
# Function was needed, because db is required in inheritance
def get_ProductImages_class(db):
    class ProductImages(db.Model):
        product_id = db.Column(db.String, db.ForeignKey('product.id'),
                               primary_key=True)
        position = db.Column(db.Integer, primary_key=True)
        base64_image = db.Column(db.String, nullable=False)

        def to_dict(self) -> dict:
            return {
                'position': self.position,
                'base64_image': self.base64_image
            }
    return ProductImages


# Return Product rest resource
class ProductRest(Resource):
    @classmethod
    def add_Product(cls, db, Product, ProductImages,
                    jwt_secret: str, user_role: dict):
        cls.db = db
        cls.Product = Product
        cls.ProductImages = ProductImages
        cls.jwt_secret = jwt_secret
        cls.user_role = user_role
        return cls

    def check_allowed_role(self, allowed_role: str) -> bool:
        return check_allowed_role(allowed_role=allowed_role,
                                  jwt_secret=self.jwt_secret,
                                  user_role=self.user_role)

    def get_first_by_id(self, id: str):
        return self.Product.query.filter_by(id=id).first()

    def get_first_by_sku(self, sku: str):
        return self.Product.query.filter_by(sku=sku).first()

    def delete(self, id: str = None) -> tuple:
        if not self.check_allowed_role('manager'):
            return status_user_401()
        product = self.get_first_by_id(id)
        if product:
            db_delete_and_commit(self.db, product)
            return status_ok(product=product.to_dict())
        return self.status_product_404()

    def get(self, id: str = None) -> tuple:
        if id:
            product = self.get_first_by_id(id)
            if product:
                return status_ok(product=product.to_dict())
            return self.status_product_404()
        return status_ok(products=model_to_dict(self.Product))

    def post(self, id: str = None) -> tuple:
        if not self.check_allowed_role('manager'):
            return status_user_401()

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, nullable=False)
        parser.add_argument('sku', type=str, required=True, nullable=False)
        parser.add_argument('description', type=str,
                            nullable=False, default='')
        parser.add_argument('price', type=float, default=None)
        parser.add_argument('discount_percent', type=float, default=None)
        parser.add_argument('position', type=int, default=0)
        parser.add_argument('images', type=list, default=[], location='json')
        parsed_values = parser.parse_args()

        if self.get_first_by_sku(parsed_values['sku']):
            return self.status_product_409()
        product_images = parsed_values.pop('images')
        product = self.Product(**parsed_values)
        self.manage_images(product_images, product, self.ProductImages)
        db_add_and_commit(self.db, product)
        return status_ok(product=product.to_dict())

    def put(self, id: str = None) -> tuple:
        manager_role = self.check_allowed_role('manager')
        if not (manager_role or self.check_allowed_role('unscrambler')):
            return status_user_401()
        product = self.get_first_by_id(id)
        if product is None:
            return self.status_product_404()

        parser = reqparse.RequestParser()
        if manager_role:
            parser.add_argument('name', type=str, nullable=False,
                                default=product.name)
            parser.add_argument('sku', type=str, nullable=False,
                                default=product.sku)
            parser.add_argument('description', type=str, nullable=False,
                                default=product.description)
            parser.add_argument('price', type=float, default=product.price)
            parser.add_argument('discount_percent', type=float,
                                default=product.discount_percent)
        parser.add_argument('position', type=int, default=product.position)
        parser.add_argument('images', type=list, default=[], location='json')
        parsed_values = parser.parse_args()

        if (('sku' in parsed_values) and
           (product.sku != parsed_values['sku']) and
           self.get_first_by_sku(parsed_values['sku'])):
            return self.status_product_409()
        product_images = parsed_values.pop('images')
        self.Product.query.filter_by(id=id).update(parsed_values)
        self.manage_images(product_images, product, self.ProductImages)
        self.db.session.commit()
        return status_ok(product=product.to_dict())

    @staticmethod
    def manage_images(images: list, product, ProductImages) -> None:
        for image_dict in images:
            position = image_dict['position']
            b64 = image_dict['base64_image']
            image = ProductImages.query.filter_by(product_id=product.id,
                                                  position=position).first()
            if (b64 is None) and (image is not None):
                product.images.remove(image)
            elif b64 is not None:
                if image is None:
                    image = ProductImages(position=position)
                    product.images.append(image)
                image.base64_image = b64

    @staticmethod
    def status_product_404() -> tuple:
        return status_error(error_code=404, message='Product not found!')

    @staticmethod
    def status_product_409() -> tuple:
        return status_error(error_code=409, message='SKU already taken!')
