# Simple E-Commerce Store

## Project Overview
**Simple E-Commerce Store (AuraStore)** is a complete, production-ready Full-Stack E-Commerce web application built with a modern client–server architecture. The system features a robust Python/Django REST API backend and a responsive, interactive frontend powered by HTML5, CSS3, and ES6 Vanilla JavaScript. It delivers an end-to-end shopping experience for customers and a comprehensive administrative portal for product, stock, and order management.

---

## Features

### 👤 Customer Features
- **User Registration and Login**: Secure token-based user authentication system.
- **Email and Password Validation**: Real-time frontend checklist validation and strict backend enforcement (uppercase, lowercase, number, special character, min 8 characters, no spaces, valid RFC email).
- **Product Catalog**: Dynamic grid display with high-resolution imagery, prices, badges, and stock availability.
- **Product Search**: Real-time search query filtering by product title and description.
- **Category Filtering**: Instant category switching (Electronics, Audio & Sound, Smart Home, Fashion & Apparel, Accessories).
- **Price Sorting & Filtering**: Range slider filters and multiple sorting options (Price Low-to-High, Price High-to-Low, Newest, Name).
- **Product Details**: Dedicated detailed product view with stock counter and quantity selectors.
- **Shopping Cart**: Real-time cart management with quantity steppers, subtotal/tax/shipping breakdown, and navigation badge counter.
- **Checkout**: Multi-field shipping address verification with Cash on Delivery (COD) and Demo/Test payment support.
- **Order Placement**: Atomic database transactions (`@transaction.atomic`) preventing inventory race conditions.
- **Order History**: Personalized list of all previous orders with detailed item breakdowns.
- **Order Status Tracking**: Visual progression timeline (`PLACED` ➔ `CONFIRMED` ➔ `PROCESSING` ➔ `SHIPPED` ➔ `DELIVERED`).

### 🛡️ Administrator Features
- **Admin Dashboard**: Real-time KPI metrics for Total Revenue, Total Orders, Active Products, and Low-Stock Warnings.
- **Admin Product Management**: Full CRUD capabilities (Create, Read, Update, Delete products) with interactive modals.
- **Stock Management**: Real-time inventory tracking, low-stock alerts, and fast inline stock adjustments.
- **Admin Order Management**: Status dispatch management with automatic inventory restoration upon order cancellation.
- **Responsive Modern UI**: Sleek, glassmorphism-inspired design with dark navbar/footer, smooth transitions, and mobile drawer navigation.

---

## Technology Stack

### Frontend:
- **HTML5**: Semantic and accessible markup
- **CSS3**: Custom modern design system, responsive grid/flexbox layouts, CSS variables, micro-animations
- **JavaScript (ES6+)**: Fetch API client, live DOM manipulation, interactive validators, localStorage session management

### Backend:
- **Python**: Core programming language
- **Django**: Web framework and ORM
- **Django REST Framework (DRF)**: RESTful API design, serializers, and token authentication
- **django-cors-headers**: Cross-Origin Resource Sharing middleware
- **Pillow**: Image processing capabilities

### Database:
- **SQLite**: Lightweight relational database managed through Django ORM

### Authentication:
- **Django REST Framework Token Authentication** (`rest_framework.authtoken`) with PBKDF2 password hashing

---

## Project Structure

```text
code alpha/
├── backend/                              # Django Backend Application
│   ├── cart/                             # Shopping cart app (models, serializers, views, urls)
│   ├── ecommerce/                        # Core project settings, URL routing, test suite
│   │   ├── __init__.py
│   │   ├── settings.py                   # Django configuration & password validators
│   │   ├── test_api.py                   # Integration & API tests
│   │   ├── urls.py                       # Global API URL configuration
│   │   └── wsgi.py
│   ├── orders/                           # Order placement & history app (atomic checkout logic)
│   ├── products/                         # Products & categories catalog app
│   │   └── management/commands/seed_data.py # Initial database seeder script
│   ├── users/                            # User management & authentication app
│   │   ├── models.py                     # UserProfile model
│   │   ├── serializers.py                # Register & Login serializers
│   │   ├── tests.py                      # 16 comprehensive auth validation tests
│   │   ├── urls.py                       # Auth endpoints (/api/register/, /api/login/, etc.)
│   │   ├── validators.py                 # Strict email & password complexity validators
│   │   └── views.py                      # Auth API views
│   ├── manage.py                         # Django management script
│   └── requirements.txt                  # Python dependencies
├── frontend/                             # Client-Side Application
│   ├── css/
│   │   └── style.css                     # Complete UI design system & responsive stylesheet
│   ├── js/
│   │   ├── admin.js                      # Admin dashboard management & stock logic
│   │   ├── api.js                        # Centralized ApiClient & error handling
│   │   ├── auth.js                       # Session state, route guards & navbar updater
│   │   ├── cart.js                       # Cart operations & badge manager
│   │   ├── orders.js                     # Order placement & timeline tracking
│   │   └── products.js                   # Product catalog rendering, search & filters
│   ├── admin.html                        # Admin KPI dashboard & inventory management
│   ├── cart.html                         # Shopping cart & order cost breakdown
│   ├── checkout.html                     # Checkout & shipping address entry
│   ├── index.html                        # Storefront landing page & hero banners
│   ├── login.html                        # Sign-in page with 1-click demo helpers
│   ├── orders.html                       # Order tracking & purchase history
│   ├── product-details.html              # Individual product overview & details
│   ├── products.html                     # Full searchable & filterable product catalog
│   └── register.html                     # User registration with live validation checklist
├── .env.example                          # Example environment variables
├── .gitignore                            # Comprehensive Git ignore rules
├── requirements.txt                      # Root requirements file
├── run_project.bat                       # Windows one-click local launcher
└── README.md                             # Project documentation
```

---

## How to Run Locally

Follow these step-by-step instructions to set up and run the project locally on a Windows system.

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd "code alpha"
```

### Step 2: Open Backend Directory & Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Seed Demo Products & Accounts
```bash
python manage.py seed_data
```

### Step 7: Start the Django Backend Server
```bash
python manage.py runserver 127.0.0.1:8000
```

> **Backend API Base URL**: `http://127.0.0.1:8000/`

---

### Step 8: Open the Frontend

You can run the frontend in either of the two standard ways:

#### Option A: Using VS Code Live Server (Recommended for Frontend Dev)
1. Open the project folder in **Visual Studio Code**.
2. Right-click on `frontend/index.html` (or `login.html`).
3. Click **"Open with Live Server"** (usually serves at `http://127.0.0.1:5500/frontend/index.html`).
4. The frontend will automatically connect to the running Django backend API at `http://127.0.0.1:8000/api`.

#### Option B: Direct Django Hosting
1. Open Google Chrome or any browser.
2. Navigate directly to **`http://127.0.0.1:8000/`** (or `http://127.0.0.1:8000/login.html`).

---

## Demo Credentials (Development Testing)

> [!NOTE]
> The following accounts are pre-configured test accounts generated automatically by the `seed_data` command. They comply with the strict password complexity rules.

| Role | Username | Email | Password | Access / Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Demo Customer** | `customer` | `customer@store.com` | `Customer@123` | Storefront browsing, Cart, Checkout, Order Tracking |
| **Demo Administrator** | `admin` | `admin@store.com` | `Admin@123` | Storefront + Admin Dashboard, Product CRUD, Stock & Order Management |

> **Quick Autofill:** On the `login.html` page, you can click the **"Customer Demo"** or **"Admin Demo"** buttons to automatically fill credentials.

---

## Automated Test Suite

To run all automated unit and integration tests covering Authentication, Validation, Cart, Orders, Stock Deduction, and Admin Permissions:

```bash
cd backend
python manage.py test users products cart orders ecommerce.test_api
```

---

## REST API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/register/` | Register new user with strict email & password validation | No |
| `POST` | `/api/login/` | Authenticate user via username/email & return Auth Token | No |
| `POST` | `/api/logout/` | Invalidate token and log out | Yes |
| `GET` | `/api/users/profile/` | Fetch current user details and role | Yes |
| `GET` | `/api/products/` | Filter, search, and list products | No |
| `GET` | `/api/products/{id}/` | Get single product details | No |
| `POST` | `/api/products/` | Create a new product | Admin |
| `PUT` | `/api/products/{id}/` | Update product details & stock level | Admin |
| `DELETE` | `/api/products/{id}/` | Remove a product | Admin |
| `GET` | `/api/categories/` | List categories with product count | No |
| `GET` | `/api/cart/` | Fetch current user's cart and calculated totals | Yes |
| `POST` | `/api/cart/` | Add product to cart with quantity | Yes |
| `PUT` | `/api/cart/{id}/` | Update cart item quantity | Yes |
| `DELETE` | `/api/cart/{id}/` | Remove item from cart | Yes |
| `DELETE` | `/api/cart/clear/` | Clear all items from cart | Yes |
| `POST` | `/api/orders/` | Place atomic order and reduce stock | Yes |
| `GET` | `/api/orders/` | Get user order history | Yes |
| `GET` | `/api/orders/{id}/` | Get detailed order summary & status | Yes |
| `GET` | `/api/admin/orders/` | List all customer orders for dispatch | Admin |
| `PUT` | `/api/admin/orders/{id}/status/` | Update order fulfillment status | Admin |
| `GET` | `/api/admin/stats/` | Fetch dashboard KPI revenue & stock alerts | Admin |

---

## License & Internship Submission
This project is developed as part of the **CodeAlpha Full Stack Development Internship**.
All rights reserved © 2026 AuraStore.
