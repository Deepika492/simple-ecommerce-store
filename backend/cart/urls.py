from django.urls import path
from .views import CartView, CartItemDetailView, CartClearView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/clear/', CartClearView.as_view(), name='cart-clear'),
    path('cart/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
]
