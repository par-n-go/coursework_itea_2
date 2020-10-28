import mongoengine as me
import datetime

me.connect('webshopbot_db')


class Supplier(me.Document):
    name = me.StringField(required=True, min_length=2, max_length=256)


class Admin(me.Document):
    login = me.StringField(min_length=6, max_length=64, required=True, unique=True)
    password = me.StringField(min_length=8, max_length=128, required=True)
    email = me.EmailField()


class User(me.Document):
    telegram_id = me.IntField(primary_key=True)
    name = me.StringField(min_length=2, max_length=256)
    phone = me.StringField(min_length=8, max_length=12)
    address = me.StringField(min_length=4, max_length=128)

    def get_cart(self):
        cart = Cart.objects.filter(user=self, is_active=True).first()
        if not cart:
            cart = Cart.objects.create(user=self)
        return cart

    @classmethod
    def initial_create(cls, telegram_id: int, name: str):
        try:
            cls.objects.create(
                telegram_id=telegram_id,
                name=name
            )
        except me.errors.NotUniqueError:
            pass


class Review(me.Document):
    rating = me.IntField(min_value=0, max_value=10)
    comment = me.StringField(min_length=1, max_length=256)
    product = me.ReferenceField('Product')
    user = me.ReferenceField(User)



# Root -> parent == None
# Subcat -> parent != None

#           Электроника (root, parent == None)
#          /                                \
#       Смартфоны(дочерняя, parent!=None)   Бытовая техника(дочерняя, parent!=None)
#                                               /
#                                           Стиральные машины(дочерняя, parent!=None, parent==Бытовая техника)


class Category(me.Document):
    title = me.StringField(min_length=2, max_length=128, required=True)
    description = me.StringField(max_length=2048)
    parent = me.ReferenceField('self')
    subcategories = me.ListField(me.ReferenceField('self'))

    @classmethod
    def get_root_categories(cls):
        return cls.objects(parent=None)

    def get_products(self):
        return Product.objects(
            category=self,
            in_stock=True

        )

    def add_subcategory(self, subcategory: 'Category'):
        subcategory.parent = self
        self.subcategories.append(subcategory)
        subcategory.save()
        self.save()


class Parameters(me.EmbeddedDocument):
    height = me.FloatField()
    width = me.FloatField()
    weight = me.FloatField()


class Product(me.Document):
    title = me.StringField(min_length=2, max_length=128, required=True)
    description = me.StringField(max_length=2048)
    price = me.DecimalField(force_string=True, required=True, min_value=0)
    discount = me.IntField(min_value=0, max_value=100, default=0)
    in_stock = me.BooleanField(default=True)
    category = me.ReferenceField(Category)
    supplier = me.ReferenceField(Supplier)
    image = me.FileField()
    parameters = me.EmbeddedDocumentField(Parameters)


class News(me.Document):
    title = me.StringField(min_length=2, max_length=256, required=True)
    body = me.StringField(min_length=2, max_length=4096, required=True)
    created = me.DateTimeField(default=datetime.datetime.now())


class Cart(me.Document):
    user = me.ReferenceField(User)
    products = me.ListField(me.ReferenceField(Product))
    is_active = me.BooleanField(default=True)
    created = me.DateTimeField(default=datetime.datetime.now())

    def add_product(self, product: Product):
        self.products.append(product)
        self.save()

