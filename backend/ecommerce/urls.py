"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Direct convenience imports for root SRS endpoints (/api/register/, /api/login/, /api/logout/)
from users.views import RegisterView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Authentication SRS aliases and namespaced endpoints
    path('api/register/', RegisterView.as_view(), name='api-register-alias'),
    path('api/login/', LoginView.as_view(), name='api-login-alias'),
    path('api/logout/', LogoutView.as_view(), name='api-logout-alias'),
    path('api/user/', ProfileView.as_view(), name='api-user-alias'),
    path('api/users/', include('users.urls')),

    # Products & Categories
    path('api/', include('products.urls')),

    # Shopping Cart
    path('api/', include('cart.urls')),

    # Orders & Admin
    path('api/', include('orders.urls')),

    # Direct Frontend Template Rendering (for unified local hosting)
    path('', TemplateView.as_view(template_name='index.html'), name='home-page'),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('products.html', TemplateView.as_view(template_name='products.html')),
    path('product-details.html', TemplateView.as_view(template_name='product-details.html')),
    path('login.html', TemplateView.as_view(template_name='login.html')),
    path('register.html', TemplateView.as_view(template_name='register.html')),
    path('cart.html', TemplateView.as_view(template_name='cart.html')),
    path('checkout.html', TemplateView.as_view(template_name='checkout.html')),
    path('orders.html', TemplateView.as_view(template_name='orders.html')),
    path('admin.html', TemplateView.as_view(template_name='admin.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
    urlpatterns += static('css/', document_root=settings.STATICFILES_DIRS[0] / 'css')
    urlpatterns += static('js/', document_root=settings.STATICFILES_DIRS[0] / 'js')
