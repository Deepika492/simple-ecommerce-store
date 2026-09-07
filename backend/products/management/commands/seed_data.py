from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from products.models import Category, Product
from users.models import UserProfile
from cart.models import Cart

class Command(BaseCommand):
    help = 'Seeds database with sample categories, realistic products, admin and demo customer.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding database..."))

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@store.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'phone': '9876543210', 'address': 'Admin HQ, Tech Park'})
        Token.objects.get_or_create(user=admin_user)
        Cart.objects.get_or_create(user=admin_user)
        self.stdout.write(self.style.SUCCESS("[OK] Admin user ready: 'admin' / 'Admin@123'"))

        # 2. Demo Customer User
        customer_user, created = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@store.com',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        customer_user.set_password('Customer@123')
        customer_user.is_staff = False
        customer_user.save()
        UserProfile.objects.get_or_create(user=customer_user, defaults={'phone': '9123456780', 'address': '123 Baker Street, Apt 4B, City Center'})
        Token.objects.get_or_create(user=customer_user)
        Cart.objects.get_or_create(user=customer_user)
        self.stdout.write(self.style.SUCCESS("[OK] Demo Customer ready: 'customer' / 'Customer@123'"))

        # 3. Categories
        categories_data = [
            {
                "name": "Electronics",
                "slug": "electronics",
                "description": "High performance computing, monitors, and gadgets for modern life.",
                "icon": "fas fa-laptop"
            },
            {
                "name": "Audio & Sound",
                "slug": "audio-sound",
                "description": "Immersive studio-grade sound, active noise-cancelling headphones and gear.",
                "icon": "fas fa-headphones"
            },
            {
                "name": "Smart Home",
                "slug": "smart-home",
                "description": "Intelligent automated ambient lighting, IoT speakers, and home essentials.",
                "icon": "fas fa-home"
            },
            {
                "name": "Fashion & Apparel",
                "slug": "fashion-apparel",
                "description": "Contemporary everyday apparel, streetwear, and durable commuter gear.",
                "icon": "fas fa-tshirt"
            },
            {
                "name": "Accessories",
                "slug": "accessories",
                "description": "Premium watches, leather wallets, and everyday carry essentials.",
                "icon": "fas fa-gem"
            }
        ]

        category_map = {}
        for cat in categories_data:
            c, _ = Category.objects.update_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'description': cat['description'],
                    'icon': cat['icon']
                }
            )
            category_map[cat['slug']] = c
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(category_map)} Categories created/updated"))

        # 4. Products
        products_data = [
            {
                "name": "Sony WH-1000XM5 Noise Cancelling Headphones",
                "category": category_map["audio-sound"],
                "price": 2499.00,
                "stock": 15,
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
                "description": "Industry-leading noise canceling with Auto NC Optimizer. Crystal clear hands-free calling with 4 beamforming microphones. Up to 30-hour battery life with quick charging."
            },
            {
                "name": "Ultra-Wide 4K IPS Pro Display 32\"",
                "category": category_map["electronics"],
                "price": 18499.00,
                "stock": 8,
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
                "description": "True-to-life 4K UHD resolution with 99% sRGB color gamut. Ultra-thin bezel design with USB-C 90W power delivery and ergonomic height-adjustable stand."
            },
            {
                "name": "Custom Mechanical RGB Keyboard (Gateron Brown)",
                "category": category_map["electronics"],
                "price": 3299.00,
                "stock": 12,
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
                "description": "Hot-swappable tactile mechanical switches with custom PBT dye-sub keycaps, sound dampening silicone foam, and south-facing RGB per-key backlighting."
            },
            {
                "name": "Ergonomic Precision Wireless Mouse",
                "category": category_map["electronics"],
                "price": 1299.00,
                "stock": 25,
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
                "description": "Crafted for comfort with sculpted thumb rest, hyper-fast electromagnetic scrolling, and dual Bluetooth / 2.4GHz USB wireless connectivity."
            },
            {
                "name": "Minimalist Sapphire Chronograph Watch",
                "category": category_map["accessories"],
                "price": 4999.00,
                "stock": 3, # LOW STOCK
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
                "description": "Handcrafted Japanese quartz movement encased in 316L stainless steel with scratch-resistant sapphire crystal glass and genuine Italian calfskin leather strap."
            },
            {
                "name": "Slim RFID-Blocking Carbon Leather Wallet",
                "category": category_map["accessories"],
                "price": 799.00,
                "stock": 20,
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&auto=format&fit=crop&q=80",
                "description": "Ultra-compact bifold wallet featuring aerospace carbon weave, RFID shield protection for up to 8 cards, and a quick-access cash clip."
            },
            {
                "name": "Echo Dot Smart Ambient Home Speaker",
                "category": category_map["smart-home"],
                "price": 2899.00,
                "stock": 10,
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=800&auto=format&fit=crop&q=80",
                "description": "Voice-controlled high-fidelity smart speaker with deep bass, temperature sensors, and seamless smart lighting automation integrations."
            },
            {
                "name": "Smart App-Controlled RGB Neon Light Strip 5M",
                "category": category_map["smart-home"],
                "price": 1499.00,
                "stock": 4, # LOW STOCK
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
                "description": "Flexible bendable silicone neon strip with 16 million colors, dynamic music sync modes, and Wi-Fi voice control support."
            },
            {
                "name": "Heavyweight French Terry Streetwear Hoodie",
                "category": category_map["fashion-apparel"],
                "price": 1899.00,
                "stock": 14,
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
                "description": "450GSM organic combed cotton with relaxed drop-shoulder cut, double-layered hood, and ribbed hems designed for lasting warmth."
            },
            {
                "name": "Weatherproof Modular Commuter Backpack 25L",
                "category": category_map["fashion-apparel"],
                "price": 2499.00,
                "stock": 0, # OUT OF STOCK
                "is_featured": True,
                "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
                "description": "Constructed from 1000D Cordura ballistic nylon with dedicated 16-inch fleece laptop compartment, luggage pass-through, and waterproof YKK zippers."
            },
            {
                "name": "Fast Power Delivery 20000mAh Power Bank 65W",
                "category": category_map["electronics"],
                "price": 1699.00,
                "stock": 18,
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1609592424368-2432ec484666?w=800&auto=format&fit=crop&q=80",
                "description": "High-capacity portable battery capable of charging laptops, phones, and tablets simultaneously with digital LED percentage display."
            },
            {
                "name": "Studio USB-C Condenser Podcasting Mic",
                "category": category_map["audio-sound"],
                "price": 3899.00,
                "stock": 7,
                "is_featured": False,
                "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&auto=format&fit=crop&q=80",
                "description": "Studio-grade 24-bit/96kHz audio resolution with cardioid pickup pattern, built-in pop filter, headphone zero-latency monitoring, and tap-to-mute button."
            }
        ]

        for p_data in products_data:
            Product.objects.update_or_create(
                name=p_data['name'],
                defaults=p_data
            )
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(products_data)} Products created/updated"))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
