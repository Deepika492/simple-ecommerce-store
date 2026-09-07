from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response({
            "success": True,
            "message": "Cart retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            return Response({
                "success": False,
                "message": "Quantity must be greater than 0."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({
                "success": False,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if product.stock < 1:
            return Response({
                "success": False,
                "message": f"Sorry, '{product.name}' is currently out of stock."
            }, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return Response({
                    "success": False,
                    "message": f"Cannot add {quantity} more. Only {product.stock} items available in stock (you already have {cart_item.quantity} in cart)."
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
        else:
            if quantity > product.stock:
                return Response({
                    "success": False,
                    "message": f"Requested quantity ({quantity}) exceeds available stock ({product.stock})."
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity

        cart_item.save()
        serializer = CartSerializer(cart)
        return Response({
            "success": True,
            "message": f"'{product.name}' added to cart.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({
                "success": False,
                "message": "Invalid quantity provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.select_related('product', 'cart').get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Cart item not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            cart_item.delete()
            cart = Cart.objects.get(user=request.user)
            return Response({
                "success": True,
                "message": "Item removed from cart.",
                "data": CartSerializer(cart).data
            }, status=status.HTTP_200_OK)

        if quantity > cart_item.product.stock:
            return Response({
                "success": False,
                "message": f"Requested quantity ({quantity}) exceeds available stock ({cart_item.product.stock})."
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        cart = Cart.objects.get(user=request.user)
        return Response({
            "success": True,
            "message": "Cart updated.",
            "data": CartSerializer(cart).data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            cart_item.delete()
            cart = Cart.objects.get(user=request.user)
            return Response({
                "success": True,
                "message": "Item removed from cart.",
                "data": CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Cart item not found."
            }, status=status.HTTP_404_NOT_FOUND)


class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({
                "success": True,
                "message": "Cart cleared successfully.",
                "data": CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({
                "success": True,
                "message": "Cart is already empty."
            }, status=status.HTTP_200_OK)
