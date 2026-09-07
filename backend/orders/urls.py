from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    AdminOrderListView,
    AdminOrderStatusUpdateView,
    AdminStatsView
)

urlpatterns = [
    # Customer order routes
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # Admin order routes
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-orders-list'),
    path('admin/orders/<int:pk>/status/', AdminOrderStatusUpdateView.as_view(), name='admin-order-status'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
]
