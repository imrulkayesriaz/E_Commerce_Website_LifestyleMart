"""
Database setup script for LIFESTYLE MART Python eCommerce Platform
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Category, Product, Order, OrderItem, Review, FlashDeal, Offer, GiftCard, Message
from werkzeug.security import generate_password_hash
import random
import string

def generate_code(length=10):
    """Generate random code for gift cards and offers"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_sample_data():
    """Create sample data for the eCommerce platform"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@lifestylemart.com').first()
        if existing_admin:
            print("[OK] Database already initialized!")
            print(f"[INFO] Current data: {Category.query.count()} categories, {Product.query.count()} products, {User.query.count()} users")
            return
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@lifestylemart.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            shop_name='Lifestyle Mart Official',
            shop_description='The official store of Lifestyle Mart Bangladesh.'
        )
        db.session.add(admin)
        
        # Create official brand sellers
        brand_sellers = {
            'Bata': User(
                name='Bata Official', email='bata@seller.bd', password_hash=generate_password_hash('seller123'),
                role='seller', shop_name='Bata Official Store',
                shop_description='Step into comfort with Bata, the leading footwear brand in Bangladesh.'
            ),
            'Aarong': User(
                name='Aarong Official', email='aarong@seller.bd', password_hash=generate_password_hash('seller123'),
                role='seller', shop_name='Aarong Official Store',
                shop_description='Aarong is Bangladesh\'s leading lifestyle brand.'
            ),
            'Apex': User(
                name='Apex Official', email='apex@seller.bd', password_hash=generate_password_hash('seller123'),
                role='seller', shop_name='Apex Official Store',
                shop_description='Apex is a leading footwear brand in Bangladesh.'
            ),
            'Yellow': User(
                name='Yellow Official', email='yellow@seller.bd', password_hash=generate_password_hash('seller123'),
                role='seller', shop_name='Yellow Official Store',
                shop_description='Yellow is a leading fashion brand in Bangladesh.'
            ),
            'Walton': User(
                name='Walton Official', email='walton@seller.bd', password_hash=generate_password_hash('seller123'),
                role='seller', shop_name='Walton Official Store',
                shop_description='Walton is a leading electronics brand in Bangladesh.'
            )
        }
        
        for s in brand_sellers.values():
            db.session.add(s)
        
        db.session.commit()
        
        # Create sample categories
        categories = [
            Category(name='Men\'s Fashion', description='Trendy clothing and accessories for men'),
            Category(name='Women\'s Fashion', description='Stylish clothing and accessories for women'),
            Category(name='Shoes', description='Footwear collection for all occasions'),
            Category(name='Accessories', description='Fashion accessories to complete your look'),
            Category(name='Beauty & Personal Care', description='Beauty products and personal care items'),
            Category(name='Home & Living', description='Home decor and lifestyle products')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create sample products (expanded with more products)
        products = [
            # Men's Fashion (Category 1) - 8 products
            {
                'name': 'Yellow Men\'s Polo Shirt',
                'description': 'Premium quality cotton polo shirt from Yellow. Features a comfortable fit, breathable fabric, and durable stitching. Perfect for casual and semi-formal wear.',
                'category_id': 1,
                'price': 1500,
                'stock': 50,
                'brand': 'Yellow',
                'image': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&q=80&w=800',
                'is_featured': True
            },
            {
                'name': 'Classic Denim Jeans',
                'description': 'Comfortable and stylish denim jeans made from premium quality cotton denim. Features a classic straight fit and five-pocket styling.',
                'category_id': 1,
                'price': 2500,
                'stock': 30,
                'brand': 'Denim Co',
                'image': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&q=80&w=800',
                'is_featured': True
            },
            {
                'name': 'Men\'s Formal Shirt',
                'description': 'Classic formal shirt perfect for business meetings. Made from premium cotton blend with wrinkle-resistant finish.',
                'category_id': 1,
                'price': 1800,
                'stock': 35,
                'brand': 'Executive Wear',
                'image': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Men\'s Polo Shirt',
                'description': 'Classic polo shirt with comfortable fit. Perfect for casual Fridays or weekend outings.',
                'category_id': 1,
                'price': 1500,
                'stock': 40,
                'brand': 'Polo Classic',
                'image': 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Men\'s Hoodie',
                'description': 'Comfortable cotton hoodie perfect for cooler weather. Features kangaroo pocket and drawstring hood.',
                'category_id': 1,
                'price': 2200,
                'stock': 25,
                'brand': 'Comfort Zone',
                'image': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Men\'s Chinos',
                'description': 'Versatile chino pants suitable for both casual and semi-formal occasions. Comfortable fit and durable fabric.',
                'category_id': 1,
                'price': 2000,
                'stock': 30,
                'brand': 'Smart Fit',
                'image': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Men\'s Leather Jacket',
                'description': 'Stylish leather jacket with premium quality finish. Perfect for adding edge to any outfit.',
                'category_id': 1,
                'price': 5500,
                'stock': 15,
                'brand': 'Leather Craft',
                'image': 'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Men\'s Shorts',
                'description': 'Comfortable casual shorts for summer days. Breathable fabric with multiple pockets.',
                'category_id': 1,
                'price': 950,
                'stock': 45,
                'brand': 'Summer Wear',
                'image': 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            
            # Women's Fashion (Category 2) - 8 products
            {
                'name': 'Elegant Summer Dress',
                'description': 'Light and breezy summer dress perfect for warm weather. Made from soft, breathable fabric.',
                'category_id': 2,
                'price': 1900,
                'stock': 25,
                'brand': 'Elegance',
                'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Women\'s Blazer',
                'description': 'Professional women\'s blazer for office and formal occasions. Made from premium fabric.',
                'category_id': 2,
                'price': 3500,
                'stock': 20,
                'brand': 'ProStyle',
                'image': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Maxi Dress',
                'description': 'Elegant maxi dress with flowing silhouette. Perfect for parties, weddings, and special occasions.',
                'category_id': 2,
                'price': 3200,
                'stock': 15,
                'brand': 'Glamour',
                'image': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Aarong Cotton Kurti',
                'description': 'Traditional Bangladeshi kurti from Aarong with modern design. Comfortable cotton fabric with beautiful embroidery and ethnic motifs.',
                'category_id': 2,
                'price': 2200,
                'stock': 40,
                'brand': 'Aarong',
                'image': 'https://images.unsplash.com/photo-1708534246055-d7b149acb731?q=80&w=800&auto=format&fit=crop',
                'is_featured': True,
                'is_eco_friendly': True,
                'eco_description': 'Made from 100% natural organic cotton, supporting local artisans and sustainable fashion.'
            },
            {
                'name': 'Women\'s Palazzo Pants',
                'description': 'Comfortable and stylish palazzo pants. Wide leg design perfect for any occasion.',
                'category_id': 2,
                'price': 1400,
                'stock': 35,
                'brand': 'Comfort Style',
                'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Le Reve Women\'s Top',
                'description': 'Trendy women\'s top from Le Reve. Made from premium rayon fabric with stylish print and comfortable fit.',
                'category_id': 2,
                'price': 1450,
                'stock': 50,
                'brand': 'Le Reve',
                'image': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Women\'s Saree',
                'description': 'Beautiful traditional saree with elegant design. Perfect for festivals and special occasions.',
                'category_id': 2,
                'price': 4500,
                'stock': 20,
                'brand': 'Ethnic Elegance',
                'image': '/static/uploads/womens_saree.png',
                'is_featured': True
            },
            {
                'name': 'Women\'s Jeans',
                'description': 'Stylish women\'s jeans with perfect fit. Available in various styles and washes.',
                'category_id': 2,
                'price': 2100,
                'stock': 30,
                'brand': 'Denim Diva',
                'image': 'https://images.unsplash.com/photo-1541099649107-f4adccb076d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            
            # Shoes (Category 3) - 6 products
            {
                'name': 'Red Running Shoes',
                'description': 'Professional running shoes with advanced cushioning technology. Perfect for daily runs.',
                'category_id': 3,
                'price': 3500,
                'stock': 40,
                'brand': 'SportMax',
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Casual Sneakers',
                'description': 'Comfortable casual sneakers for everyday wear. Features breathable canvas upper.',
                'category_id': 3,
                'price': 2000,
                'stock': 50,
                'brand': 'Urban Step',
                'image': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Women\'s Heels',
                'description': 'Elegant high heels for formal occasions. Comfortable design with stable heel.',
                'category_id': 3,
                'price': 2800,
                'stock': 25,
                'brand': 'Elegant Step',
                'image': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Apex Premium Leather Oxfords',
                'description': 'Premium leather formal shoes from Apex. Classic Oxford design with comfortable sole and elegant finish.',
                'category_id': 3,
                'price': 4500,
                'stock': 20,
                'brand': 'Apex',
                'image': 'https://images.unsplash.com/photo-1677203006929-fd0d9f4f350d?q=80&w=800&auto=format&fit=crop',
                'is_featured': False
            },
            {
                'name': 'Sandals',
                'description': 'Comfortable everyday sandals. Perfect for summer and casual wear.',
                'category_id': 3,
                'price': 1200,
                'stock': 60,
                'brand': 'Summer Comfort',
                'image': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Sports Shoes',
                'description': 'All-purpose sports shoes suitable for gym, running, and outdoor activities.',
                'category_id': 3,
                'price': 2800,
                'stock': 35,
                'brand': 'Athletic Pro',
                'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            
            # Accessories (Category 4) - 8 products
            {
                'name': 'Leather Handbag',
                'description': 'Genuine leather handbag with multiple compartments. Perfect for office and shopping.',
                'category_id': 4,
                'price': 4200,
                'stock': 20,
                'brand': 'Chic Style',
                'image': '/static/uploads/leather_handbag.png',
                'is_featured': True
            },
            {
                'name': 'Walton Tick Smartwatch',
                'description': 'Advanced smartwatch from Walton with fitness tracking, heart rate monitor, and long battery life. Sleek and modern design.',
                'category_id': 4,
                'price': 3200,
                'stock': 30,
                'brand': 'Walton',
                'image': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Designer Sunglasses',
                'description': 'Trendy designer sunglasses with UV400 protection. Lightweight frame.',
                'category_id': 4,
                'price': 1500,
                'stock': 45,
                'brand': 'Vision Style',
                'image': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Leather Wallet',
                'description': 'Genuine leather wallet with multiple card slots. RFID blocking technology.',
                'category_id': 4,
                'price': 900,
                'stock': 60,
                'brand': 'Lux Accessories',
                'image': 'https://images.unsplash.com/photo-1627123424574-724758594e93?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Women\'s Scarf',
                'description': 'Beautiful silk scarf with elegant print. Perfect accessory for any outfit.',
                'category_id': 4,
                'price': 650,
                'stock': 80,
                'brand': 'Silk Touch',
                'image': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Men\'s Belt',
                'description': 'Genuine leather belt with classic buckle. Available in multiple sizes.',
                'category_id': 4,
                'price': 750,
                'stock': 55,
                'brand': 'Leather Craft',
                'image': 'https://images.unsplash.com/photo-1624222247344-550fb60583dc?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Jewelry Set',
                'description': 'Elegant jewelry set including necklace and earrings. Perfect for special occasions.',
                'category_id': 4,
                'price': 2500,
                'stock': 25,
                'brand': 'Jewel Shine',
                'image': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Tote Bag',
                'description': 'Spacious tote bag perfect for shopping or daily use. Durable canvas material.',
                'category_id': 4,
                'price': 1100,
                'stock': 40,
                'brand': 'Carry All',
                'image': 'https://images.unsplash.com/photo-1559563458-527698bf5295?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            
            # Beauty & Personal Care (Category 5) - 6 products
            {
                'name': 'Face Cream',
                'description': 'Moisturizing face cream for all skin types. Keeps skin hydrated and glowing.',
                'category_id': 5,
                'price': 850,
                'stock': 70,
                'brand': 'Glow Beauty',
                'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Shampoo',
                'description': 'Nourishing shampoo for healthy hair. Natural ingredients for all hair types.',
                'category_id': 5,
                'price': 650,
                'stock': 100,
                'brand': 'Hair Care Pro',
                'image': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Perfume',
                'description': 'Long-lasting fragrance with elegant scent. Perfect for daily wear.',
                'category_id': 5,
                'price': 1800,
                'stock': 35,
                'brand': 'Fragrance World',
                'image': 'https://images.unsplash.com/photo-1541643600914-78b084683601?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Body Lotion',
                'description': 'Nourishing body lotion for soft and smooth skin. Quick absorbing formula.',
                'category_id': 5,
                'price': 550,
                'stock': 85,
                'brand': 'Skin Care',
                'image': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Makeup Kit',
                'description': 'Complete makeup kit with eyeshadow, lipstick, and more. Perfect for beginners.',
                'category_id': 5,
                'price': 2200,
                'stock': 30,
                'brand': 'Makeup Pro',
                'image': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Hair Oil',
                'description': 'Natural hair oil for strong and healthy hair. Traditional formula with modern benefits.',
                'category_id': 5,
                'price': 450,
                'stock': 90,
                'brand': 'Herbal Care',
                'image': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            
            # Home & Living (Category 6) - 6 products
            {
                'name': 'Decorative Cushion',
                'description': 'Beautiful decorative cushion for your living room. Soft fabric with elegant design.',
                'category_id': 6,
                'price': 750,
                'stock': 50,
                'brand': 'Home Comfort',
                'image': 'https://images.unsplash.com/photo-1567016432779-094069958ea5?auto=format&fit=crop&q=80&w=800',
                'is_featured': True
            },
            {
                'name': 'Table Lamp',
                'description': 'Elegant table lamp for bedroom or living room. Creates warm ambient lighting.',
                'category_id': 6,
                'price': 1600,
                'stock': 25,
                'brand': 'Light Decor',
                'image': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Wall Art',
                'description': 'Beautiful wall art to decorate your home. Modern design that fits any decor.',
                'category_id': 6,
                'price': 1200,
                'stock': 30,
                'brand': 'Art Decor',
                'image': 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            {
                'name': 'Curtains',
                'description': 'Elegant curtains for your windows. Light blocking fabric with beautiful design.',
                'category_id': 6,
                'price': 2200,
                'stock': 20,
                'brand': 'Window Dress',
                'image': 'https://images.unsplash.com/photo-1507089947368-19c1da9775ae?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Storage Basket',
                'description': 'Woven storage basket for organizing your home. Natural material and sturdy design.',
                'category_id': 6,
                'price': 850,
                'stock': 40,
                'brand': 'Organize Pro',
                'image': 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': False
            },
            {
                'name': 'Bed Sheets',
                'description': 'Comfortable cotton bed sheets. Soft fabric for a good night\'s sleep.',
                'category_id': 6,
                'price': 1400,
                'stock': 35,
                'brand': 'Sleep Well',
                'image': 'https://images.unsplash.com/photo-1631679706909-1844bbd07221?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True
            },
            
            # Eco-Friendly Uniques (Category 6 - Home & Living or 4 - Accessories)
            {
                'name': 'Sustainable Jute Tote Bag',
                'description': 'A beautiful, handcrafted tote bag made from 100% natural jute fiber. Durable, biodegradable, and perfect for eco-conscious shopping.',
                'category_id': 4,
                'price': 850,
                'stock': 100,
                'brand': 'EcoCraft',
                'image': 'https://images.unsplash.com/photo-1544816153-12ad5d714401?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True,
                'is_eco_friendly': True,
                'eco_description': 'Handcrafted from 100% biodegradable jute fiber. Supports rural women artisans.'
            },
            {
                'name': 'Natural Bamboo Water Bottle',
                'description': 'Stay hydrated with this stylish bamboo water bottle. Features a high-quality stainless steel interior and a genuine bamboo exterior.',
                'category_id': 6,
                'price': 1200,
                'stock': 50,
                'brand': 'GreenLife',
                'image': 'https://images.unsplash.com/photo-1602143352538-ff39385033a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'is_featured': True,
                'is_eco_friendly': True,
                'eco_description': 'Plastic-free construction using renewable bamboo and recyclable stainless steel.'
            },
        ]
        
        for product_data in products:
            # Map products to their brand sellers or default to admin
            brand_name = product_data.get('brand', '')
            product_seller = brand_sellers.get(brand_name, admin)
            
            product = Product(
                **product_data,
                seller_id=product_seller.id
            )
            db.session.add(product)
        
        db.session.commit()
        print(f"[INFO] Created {len(products)} products")
        
        # Create Flash Deals
        now = datetime.utcnow()
        flash_deals = [
            {
                'product_id': 1,  # T-Shirt
                'discount_percent': 30,
                'original_price': 1200,
                'deal_price': 840,
                'end_time': now + timedelta(days=3),
                'is_active': True
            },
            {
                'product_id': 5,  # Handbag
                'discount_percent': 25,
                'original_price': 4200,
                'deal_price': 3150,
                'end_time': now + timedelta(days=2),
                'is_active': True
            },
            {
                'product_id': 4,  # Running Shoes
                'discount_percent': 20,
                'original_price': 3500,
                'deal_price': 2800,
                'end_time': now + timedelta(days=5),
                'is_active': True
            },
            {
                'product_id': 28,  # Heels
                'discount_percent': 35,
                'original_price': 2800,
                'deal_price': 1820,
                'end_time': now + timedelta(days=1),
                'is_active': True
            },
        ]
        
        for deal_data in flash_deals:
            deal = FlashDeal(**deal_data)
            db.session.add(deal)
        
        db.session.commit()
        print(f"[INFO] Created {len(flash_deals)} flash deals")
        
        # Create Offers/Promo Codes
        offers = [
            {
                'title': 'Welcome Discount',
                'description': 'Get 10% off on your first order',
                'discount_type': 'percentage',
                'discount_value': 10,
                'min_purchase': 500,
                'max_discount': 500,
                'code': 'WELCOME10',
                'end_date': now + timedelta(days=30),
                'is_active': True
            },
            {
                'title': 'Summer Sale',
                'description': 'Flat 500 off on orders above 3000',
                'discount_type': 'fixed',
                'discount_value': 500,
                'min_purchase': 3000,
                'max_discount': 500,
                'code': 'SUMMER500',
                'end_date': now + timedelta(days=15),
                'is_active': True
            },
            {
                'title': 'Big Savings',
                'description': '20% off on all fashion items',
                'discount_type': 'percentage',
                'discount_value': 20,
                'min_purchase': 2000,
                'max_discount': 1000,
                'code': 'FASHION20',
                'end_date': now + timedelta(days=20),
                'is_active': True
            },
        ]
        
        for offer_data in offers:
            offer = Offer(**offer_data)
            db.session.add(offer)
        
        db.session.commit()
        print(f"[INFO] Created {len(offers)} offers")
        
        # Create Gift Cards
        gift_cards = [
            {
                'code': generate_code(),
                'amount': 1000,
                'balance': 1000,
                'purchaser_id': 2,
                'recipient_email': 'friend@example.com',
                'message': 'Happy Birthday! Enjoy shopping!',
                'is_redeemed': False,
                'expiry_date': now + timedelta(days=365)
            },
            {
                'code': generate_code(),
                'amount': 2000,
                'balance': 2000,
                'purchaser_id': 3,
                'recipient_email': 'family@example.com',
                'message': 'Gift for you!',
                'is_redeemed': False,
                'expiry_date': now + timedelta(days=365)
            },
            {
                'code': generate_code(),
                'amount': 500,
                'balance': 500,
                'purchaser_id': 2,
                'recipient_email': 'test@example.com',
                'message': 'Thank you for your support!',
                'is_redeemed': True,
                'expiry_date': now + timedelta(days=180)
            },
        ]
        
        for card_data in gift_cards:
            card = GiftCard(**card_data)
            db.session.add(card)
        
        db.session.commit()
        print(f"[INFO] Created {len(gift_cards)} gift cards")
        
        # Create sample users
        users = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'password_hash': generate_password_hash('password123'),
                'phone': '01712345678',
                'address': '123 Main St, Dhaka'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'password_hash': generate_password_hash('password123'),
                'phone': '01887654321',
                'address': '456 Park Ave, Dhaka'
            },
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'password_hash': generate_password_hash('password123'),
                'phone': '01987654321',
                'address': '789 Test Road, Dhaka'
            }
        ]
        
        for user_data in users:
            user = User(**user_data)
            db.session.add(user)
        
        db.session.commit()
        print(f"[INFO] Created {len(users)} users")
        
        # Create sample reviews
        products_for_reviews = Product.query.limit(10).all()
        users_for_reviews = User.query.all()
        review_count = 0
        
        for product in products_for_reviews:
            for user in users_for_reviews:
                if random.random() > 0.6:  # 40% chance of review
                    review = Review(
                        product_id=product.id,
                        user_id=user.id,
                        rating=random.randint(3, 5),
                        review_text=random.choice([
                            'Great product! Highly recommend.',
                            'Excellent quality for the price.',
                            'Love this product! Will buy again.',
                            'Good value for money.',
                            'Perfect! Exactly as described.',
                            'Very satisfied with my purchase.'
                        ]),
                        status='approved'
                    )
                    db.session.add(review)
                    review_count += 1
        
        db.session.commit()
        
        # Create sample messages
        john = User.query.filter_by(email='john@example.com').first()
        apex_seller = User.query.filter_by(email='apex@seller.bd').first()
        
        if john and apex_seller:
            messages = [
                {
                    'sender_id': john.id,
                    'receiver_id': apex_seller.id,
                    'content': 'Hello, do you have these leather oxfords in size 42?',
                    'is_read': False,
                    'created_at': now - timedelta(hours=5)
                },
                {
                    'sender_id': apex_seller.id,
                    'receiver_id': john.id,
                    'content': 'Yes, we have size 42 in stock! They are our best-sellers.',
                    'is_read': True,
                    'created_at': now - timedelta(hours=4)
                },
                {
                    'sender_id': john.id,
                    'receiver_id': apex_seller.id,
                    'content': 'Great! I will place an order now.',
                    'is_read': False,
                    'created_at': now - timedelta(hours=3)
                }
            ]
            
            for msg_data in messages:
                msg = Message(**msg_data)
                db.session.add(msg)
            
            db.session.commit()
            print(f"[INFO] Created {len(messages)} sample messages")
        
        print("\n" + "="*60)
        print("[OK] Database setup completed successfully!")
        print("="*60)
        print(f"[INFO] Categories: {Category.query.count()}")
        print(f"[INFO] Products: {Product.query.count()}")
        print(f"[INFO] Users: {User.query.count()}")
        print(f"[INFO] Reviews: {Review.query.count()}")
        print(f"[INFO] Flash Deals: {FlashDeal.query.count()}")
        print(f"[INFO] Offers: {Offer.query.count()}")
        print(f"[INFO] Gift Cards: {GiftCard.query.count()}")
        print("\n[LOGIN] Admin credentials:")
        print("   Email: admin@lifestylemart.com")
        print("   Password: admin123")
        print("\n[LOGIN] User credentials:")
        print("   Email: john@example.com / jane@example.com")
        print("   Password: password123")
        print("="*60)

if __name__ == '__main__':
    create_sample_data()
