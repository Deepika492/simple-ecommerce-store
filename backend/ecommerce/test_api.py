from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from decimal import Decimal

class EcommerceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.admin = User.objects.create_superuser('admin_test', 'admin@test.com', 'adminpass123')
        self.customer = User.objects.create_user('cust_test', 'cust@test.com', 'custpass123')
        
        # Create Category
        self.cat = Category.objects.create(name='Gadgets', slug='gadgets', description='Smart devices')
        
        # Create Products
        self.p1 = Product.objects.create(
            name='Test Earbuds',
            category=self.cat,
            price=Decimal('1000.00'),
            stock=10
        )
        self.p2 = Product.objects.create(
            name='Test Watch',
            category=self.cat,
            price=Decimal('500.00'),
            stock=2
        )

    def test_registration_and_login(self):
        # 1. Register new user
        reg_resp = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Pass@1234',
            'confirm_password': 'Pass@1234'
        }, format='json')
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(reg_resp.data['success'])
        self.assertIn('token', reg_resp.data['data'])

        # 2. Login
        login_resp = self.client.post('/api/login/', {
            'username': 'newuser',
            'password': 'Pass@1234'
        }, format='json')
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(login_resp.data['success'])
        token = login_resp.data['data']['token']

        # 3. Authenticated request using Token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        prof_resp = self.client.get('/api/users/profile/')
        self.assertEqual(prof_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(prof_resp.data['data']['user']['username'], 'newuser')

    def test_product_search_and_filters(self):
        resp = self.client.get('/api/products/?search=Earbuds')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['data']), 1)
        self.assertEqual(resp.data['data'][0]['name'], 'Test Earbuds')

        # Filter by max price
        resp_price = self.client.get('/api/products/?max_price=800')
        self.assertEqual(len(resp_price.data['data']), 1)
        self.assertEqual(resp_price.data['data'][0]['name'], 'Test Watch')

    def test_cart_and_atomic_order_processing(self):
        # Login customer
        login_resp = self.client.post('/api/login/', {
            'username': 'cust_test',
            'password': 'custpass123'
        }, format='json')
        token = login_resp.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # Add p1 to cart (qty 2 -> subtotal 2000)
        add_resp = self.client.post('/api/cart/', {
            'product_id': self.p1.id,
            'quantity': 2
        }, format='json')
        self.assertEqual(add_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(add_resp.data['data']['total_items'], 2)

        # Check cart calculation
        # Subtotal: 2000, Tax (5%): 100, Shipping (>=1000): 0, Grand Total: 2100
        cart_resp = self.client.get('/api/cart/')
        self.assertEqual(Decimal(str(cart_resp.data['data']['subtotal'])), Decimal('2000.00'))
        self.assertEqual(Decimal(str(cart_resp.data['data']['tax'])), Decimal('100.00'))
        self.assertEqual(Decimal(str(cart_resp.data['data']['shipping'])), Decimal('0.00'))
        self.assertEqual(Decimal(str(cart_resp.data['data']['grand_total'])), Decimal('2100.00'))

        # Place Order
        order_resp = self.client.post('/api/orders/', {
            'shipping_name': 'Jane Doe',
            'shipping_address': '456 Market Road',
            'phone': '9988776655',
            'payment_method': 'COD'
        }, format='json')
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(order_resp.data['success'])
        order_id = order_resp.data['data']['id']

        # Verify stock was decremented from 10 to 8
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 8)

        # Verify cart was cleared
        cart_after = self.client.get('/api/cart/')
        self.assertEqual(len(cart_after.data['data']['items']), 0)

        # Verify order history
        orders_resp = self.client.get('/api/orders/')
        self.assertEqual(len(orders_resp.data['data']), 1)
        self.assertEqual(orders_resp.data['data'][0]['id'], order_id)
        self.assertEqual(orders_resp.data['data'][0]['status'], 'PLACED')

    def test_stock_insufficient_rollback(self):
        # Login customer
        login_resp = self.client.post('/api/login/', {
            'username': 'cust_test',
            'password': 'custpass123'
        }, format='json')
        token = login_resp.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # Add p2 (stock = 2) to cart with qty 2
        self.client.post('/api/cart/', {'product_id': self.p2.id, 'quantity': 2}, format='json')

        # Simulate another buyer reducing stock to 1 in the background
        self.p2.stock = 1
        self.p2.save()

        # Place order should fail and rollback atomically
        order_resp = self.client.post('/api/orders/', {
            'shipping_name': 'Jane Doe',
            'shipping_address': '456 Market Road',
            'phone': '9988776655',
            'payment_method': 'COD'
        }, format='json')
        self.assertEqual(order_resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(order_resp.data['success'])
        self.assertIn('Insufficient stock', order_resp.data['message'])

        # Stock should remain 1, no order created
        self.assertEqual(Order.objects.count(), 0)

    def test_admin_permissions_and_status_update(self):
        # Login customer -> attempt to create product should fail (403 or 401)
        cust_login = self.client.post('/api/login/', {'username': 'cust_test', 'password': 'custpass123'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {cust_login.data['data']['token']}")
        prod_create_cust = self.client.post('/api/products/', {
            'name': 'Unauthorized Product',
            'price': 999,
            'stock': 5
        }, format='json')
        self.assertEqual(prod_create_cust.status_code, status.HTTP_403_FORBIDDEN)

        # Login admin -> create product should succeed
        admin_login = self.client.post('/api/login/', {'username': 'admin_test', 'password': 'adminpass123'}, format='json')
        admin_token = admin_login.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token}")
        prod_create_admin = self.client.post('/api/products/', {
            'name': 'Admin Approved Product',
            'price': 1499.00,
            'stock': 10,
            'category': self.cat.id
        }, format='json')
        self.assertEqual(prod_create_admin.status_code, status.HTTP_201_CREATED)
