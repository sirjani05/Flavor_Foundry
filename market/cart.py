from decimal import Decimal
from django.conf import settings
from .models import Product

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Validates against stock_quantity.
        Returns a tuple: (success: bool, message: str)
        """
        product_id = str(product.id)
        current_qty = self.cart.get(product_id, {}).get('quantity', 0)

        if override_quantity:
            new_qty = quantity
        else:
            new_qty = current_qty + quantity

        if not product.is_available:
            return False, f"Sorry, '{product.name}' is currently out of stock."

        if new_qty > product.stock_quantity:
            max_add = max(0, product.stock_quantity - current_qty)
            if override_quantity:
                return False, f"Only {product.stock_quantity} unit(s) of '{product.name}' in stock."
            else:
                return False, f"Cannot add {quantity} more unit(s). Only {product.stock_quantity} in stock ({current_qty} already in cart)."

        if new_qty <= 0:
            self.remove(product)
            return True, f"Removed '{product.name}' from your cart."

        self.cart[product_id] = {
            'quantity': new_qty,
            'price': str(product.price)
        }
        self.save()
        return True, f"Added {quantity} x '{product.name}' to cart."

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True
