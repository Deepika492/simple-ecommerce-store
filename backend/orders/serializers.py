from rest_framework import serializers
from .models import Order, OrderItem
from users.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    item_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price', 'item_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_details',
            'items',
            'subtotal',
            'tax',
            'shipping',
            'total_amount',
            'shipping_name',
            'shipping_address',
            'phone',
            'payment_method',
            'status',
            'total_items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'subtotal', 'tax', 'shipping', 'total_amount', 'status', 'created_at', 'updated_at']

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


class OrderCreateSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=150, required=True)
    shipping_address = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=20, required=True)
    payment_method = serializers.ChoiceField(choices=['COD', 'DEMO'], default='COD')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        'PLACED', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'
    ])
