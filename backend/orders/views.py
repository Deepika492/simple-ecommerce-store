from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.db.models import Sum, Count, Q
from decimal import Decimal

from products.models import Product
from cart.models import Cart
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)

class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
        serializer = OrderSerializer(orders, many=True)
        return Response({
            "success": True,
            "message": "Orders retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        create_serializer = OrderCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid checkout details.",
                "errors": create_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        shipping_name = create_serializer.validated_data['shipping_name']
        shipping_address = create_serializer.validated_data['shipping_address']
        phone = create_serializer.validated_data['phone']
        payment_method = create_serializer.validated_data['payment_method']

        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('product').all()
            if not cart_items.exists():
                return Response({
                    "success": False,
                    "message": "Your cart is empty. Add products before checking out."
                }, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({
                "success": False,
                "message": "Cart not found."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Atomic Order Processing
        try:
            with transaction.atomic():
                subtotal = Decimal('0.00')

                # 1. Stock verification & calculation
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product.pk)
                    if product.stock < item.quantity:
                        raise ValueError(
                            f"Insufficient stock for '{product.name}'. Available: {product.stock}, in cart: {item.quantity}."
                        )
                    subtotal += product.price * item.quantity

                # 2. Compute authoritative pricing rules
                tax = round(subtotal * Decimal('0.05'), 2)
                shipping = Decimal('0.00') if subtotal >= Decimal('1000.00') else Decimal('50.00')
                total_amount = round(subtotal + tax + shipping, 2)

                # 3. Create Order
                order = Order.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    tax=tax,
                    shipping=shipping,
                    total_amount=total_amount,
                    shipping_name=shipping_name,
                    shipping_address=shipping_address,
                    phone=phone,
                    payment_method=payment_method,
                    status='PLACED'
                )

                # 4. Create OrderItems and reduce product stock
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product.pk)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_image=product.image_url,
                        quantity=item.quantity,
                        price=product.price # Historical purchase price
                    )
                    # Reduce stock
                    product.stock -= item.quantity
                    product.save()

                # 5. Clear Cart
                cart_items.delete()

                order_data = OrderSerializer(order).data
                return Response({
                    "success": True,
                    "message": f"Order #{order.id} placed successfully!",
                    "data": order_data
                }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"An error occurred while processing your order: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if request.user.is_staff or request.user.is_superuser:
                order = Order.objects.prefetch_related('items').get(pk=pk)
            else:
                order = Order.objects.prefetch_related('items').get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({
                "success": False,
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response({
            "success": True,
            "message": "Order details retrieved.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                "success": False,
                "message": "Admin authorization required."
            }, status=status.HTTP_403_FORBIDDEN)

        queryset = Order.objects.select_related('user').prefetch_related('items').all()
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(shipping_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(phone__icontains=search)
            )

        serializer = OrderSerializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Admin orders list retrieved.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                "success": False,
                "message": "Admin authorization required."
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.prefetch_related('items__product').get(pk=pk)
        except Order.DoesNotExist:
            return Response({
                "success": False,
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)

        status_serializer = OrderStatusUpdateSerializer(data=request.data)
        if not status_serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid status value.",
                "errors": status_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_status = status_serializer.validated_data['status']
        old_status = order.status

        # If transitioning to CANCELLED from non-cancelled, restore product stock
        if new_status == 'CANCELLED' and old_status != 'CANCELLED':
            with transaction.atomic():
                for item in order.items.all():
                    if item.product:
                        item.product.stock += item.quantity
                        item.product.save()
                order.status = new_status
                order.save()
        else:
            order.status = new_status
            order.save()

        return Response({
            "success": True,
            "message": f"Order #{order.id} status updated to {new_status}.",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                "success": False,
                "message": "Admin authorization required."
            }, status=status.HTTP_403_FORBIDDEN)

        total_revenue = Order.objects.exclude(status='CANCELLED').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_orders = Order.objects.count()
        placed_orders = Order.objects.filter(status='PLACED').count()
        delivered_orders = Order.objects.filter(status='DELIVERED').count()
        cancelled_orders = Order.objects.filter(status='CANCELLED').count()

        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock__lte=5, stock__gt=0).count()
        out_of_stock_products = Product.objects.filter(stock=0).count()

        recent_orders = Order.objects.select_related('user').all()[:5]

        return Response({
            "success": True,
            "message": "Dashboard statistics retrieved.",
            "data": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "placed_orders": placed_orders,
                "delivered_orders": delivered_orders,
                "cancelled_orders": cancelled_orders,
                "total_products": total_products,
                "low_stock_products": low_stock_products,
                "out_of_stock_products": out_of_stock_products,
                "recent_orders": OrderSerializer(recent_orders, many=True).data
            }
        }, status=status.HTTP_200_OK)
