from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    item_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'item_total', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'tax', 'shipping', 'grand_total', 'total_items', 'updated_at']

    def get_subtotal(self, obj):
        total = sum(item.product.price * item.quantity for item in obj.items.all())
        return round(Decimal(total), 2)

    def get_tax(self, obj):
        subtotal = self.get_subtotal(obj)
        # Tax = Subtotal * 5%
        return round(subtotal * Decimal('0.05'), 2)

    def get_shipping(self, obj):
        subtotal = self.get_subtotal(obj)
        if subtotal == Decimal('0.00'):
            return Decimal('0.00')
        # Shipping = 0 when Subtotal >= 1000, else 50
        return Decimal('0.00') if subtotal >= Decimal('1000.00') else Decimal('50.00')

    def get_grand_total(self, obj):
        subtotal = self.get_subtotal(obj)
        if subtotal == Decimal('0.00'):
            return Decimal('0.00')
        tax = self.get_tax(obj)
        shipping = self.get_shipping(obj)
        return round(subtotal + tax + shipping, 2)

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
