from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AuthenticationValidationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Seed test customer and admin
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@store.com',
            password='Customer@123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@store.com',
            password='Admin@123'
        )

    # 1. Valid registration succeeds
    def test_valid_registration_succeeds(self):
        resp = self.client.post('/api/register/', {
            'username': 'deepika_r',
            'email': 'deepika@gmail.com',
            'password': 'Deepika@123',
            'confirm_password': 'Deepika@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['success'])
        self.assertIn('token', resp.data['data'])
        self.assertEqual(resp.data['data']['user']['username'], 'deepika_r')
        self.assertEqual(resp.data['data']['user']['email'], 'deepika@gmail.com')

    # 2. Invalid email formats rejected
    def test_invalid_email_formats_rejected(self):
        invalid_emails = [
            'deepika@gmail',
            'deepika@',
            '@gmail.com',
            'deepika gmail.com',
            'deepika@gmail.',
            'deepika..test@gmail.com',
        ]
        for email in invalid_emails:
            resp = self.client.post('/api/register/', {
                'username': f'user_{abs(hash(email)) % 10000}',
                'email': email,
                'password': 'AuraStore@2026',
                'confirm_password': 'AuraStore@2026'
            }, format='json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, f"Failed for email: {email}")
            self.assertFalse(resp.data['success'])
            self.assertEqual(resp.data['errors'].get('email'), 'Please enter a valid email address.')

    # 3. Password < 8 characters rejected
    def test_password_too_short_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'Aa@1',
            'confirm_password': 'Aa@1'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 4. Password missing uppercase rejected
    def test_password_missing_uppercase_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'deepika@123',
            'confirm_password': 'deepika@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 5. Password missing lowercase rejected
    def test_password_missing_lowercase_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password': 'DEEPA@123',
            'confirm_password': 'DEEPA@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 6. Password missing number rejected
    def test_password_missing_number_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser4',
            'email': 'test4@example.com',
            'password': 'Deepika@',
            'confirm_password': 'Deepika@'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 7. Password missing special character rejected
    def test_password_missing_special_character_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser5',
            'email': 'test5@example.com',
            'password': 'Deepika123',
            'confirm_password': 'Deepika123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 8. Password with spaces rejected
    def test_password_with_spaces_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser6',
            'email': 'test6@example.com',
            'password': 'Deepika 123@',
            'confirm_password': 'Deepika 123@'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 9. Password numeric only rejected
    def test_password_numeric_only_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser7',
            'email': 'test7@example.com',
            'password': '12345678',
            'confirm_password': '12345678'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data['errors'])

    # 10. Password mismatch rejected
    def test_password_mismatch_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'testuser8',
            'email': 'test8@example.com',
            'password': 'Deepika@123',
            'confirm_password': 'DifferentPass@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['errors'].get('confirm_password'), 'Passwords do not match.')

    # 11. Username too short rejected (< 3 chars)
    def test_username_too_short_rejected(self):
        resp = self.client.post('/api/register/', {
            'username': 'de',
            'email': 'de@example.com',
            'password': 'Deepika@123',
            'confirm_password': 'Deepika@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', resp.data['errors'])

    # 12. Username with spaces or invalid chars rejected
    def test_username_with_spaces_or_special_chars_rejected(self):
        for invalid_u in ['deepika r', 'deepika@123', 'deep!ka']:
            resp = self.client.post('/api/register/', {
                'username': invalid_u,
                'email': 'valid@example.com',
                'password': 'Deepika@123',
                'confirm_password': 'Deepika@123'
            }, format='json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('username', resp.data['errors'])

    # 13. Duplicate username & email rejected
    def test_duplicate_user_and_email_rejected(self):
        # customer already exists in setUp
        resp1 = self.client.post('/api/register/', {
            'username': 'customer',
            'email': 'unique@example.com',
            'password': 'Shop@India123',
            'confirm_password': 'Shop@India123'
        }, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp1.data['errors'].get('username'), 'This username is already taken.')

        resp2 = self.client.post('/api/register/', {
            'username': 'unique_user',
            'email': 'customer@store.com',
            'password': 'Shop@India123',
            'confirm_password': 'Shop@India123'
        }, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp2.data['errors'].get('email'), 'This email is already registered.')

    # 14. Valid login via username & email
    def test_valid_login_via_username_and_email(self):
        # Login via username
        resp_u = self.client.post('/api/login/', {
            'username': 'customer',
            'password': 'Customer@123'
        }, format='json')
        self.assertEqual(resp_u.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_u.data['success'])
        self.assertIn('token', resp_u.data['data'])

        # Login via email
        resp_e = self.client.post('/api/login/', {
            'username': 'customer@store.com',
            'password': 'Customer@123'
        }, format='json')
        self.assertEqual(resp_e.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_e.data['success'])

    # 15. Invalid login rejected without exposing account existence
    def test_invalid_login_rejected(self):
        resp = self.client.post('/api/login/', {
            'username': 'nonexistent_user',
            'password': 'WrongPassword@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp.data['success'])
        self.assertEqual(resp.data['message'], 'Invalid username/email or password.')

        resp_wrong_pw = self.client.post('/api/login/', {
            'username': 'customer',
            'password': 'WrongPassword@123'
        }, format='json')
        self.assertEqual(resp_wrong_pw.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_wrong_pw.data['message'], 'Invalid username/email or password.')

    # 16. Existing admin account works
    def test_existing_admin_account_works(self):
        resp = self.client.post('/api/login/', {
            'username': 'admin',
            'password': 'Admin@123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['data']['user']['is_staff'])
