"""
Seed eco-friendly data into the existing database.
Marks some existing products as eco-friendly and adds new sustainable products.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Product, Category, User

with app.app_context():
    # 1. Mark some existing products as eco-friendly
    aarong_products = Product.query.filter(Product.brand == 'Aarong').all()
    for p in aarong_products:
        p.is_eco_friendly = True
        p.eco_description = 'Made from natural organic cotton, supporting local artisans and sustainable fashion.'
        print(f"  [UPDATED] {p.name} -> eco-friendly")

    # Also mark any product with "Cotton" or "organic" in name/description
    natural_products = Product.query.filter(
        db.or_(
            Product.name.ilike('%cotton%'),
            Product.name.ilike('%organic%'),
            Product.description.ilike('%organic%'),
            Product.description.ilike('%natural%'),
        )
    ).all()
    for p in natural_products:
        if not p.is_eco_friendly:
            p.is_eco_friendly = True
            p.eco_description = 'Made with natural, sustainably sourced materials.'
            print(f"  [UPDATED] {p.name} -> eco-friendly")

    db.session.commit()
    print("\n[OK] Existing products updated.")

    # 2. Add brand-new eco products if they don't exist
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("[ERROR] No admin user found!")
        exit(1)

    new_eco_products = [
        {
            'name': 'Sustainable Jute Tote Bag',
            'description': 'A beautiful, handcrafted tote bag made from 100% natural jute fiber. Durable, biodegradable, and perfect for eco-conscious shopping.',
            'category_id': 4,
            'price': 850,
            'stock': 100,
            'brand': 'EcoCraft',
            'image': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
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
            'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_eco_friendly': True,
            'eco_description': 'Plastic-free construction using renewable bamboo and recyclable stainless steel.'
        },
        {
            'name': 'Organic Cotton Face Towel Set',
            'description': 'Ultra-soft, chemical-free face towels made from 100% GOTS-certified organic cotton. Gentle on skin, kind to the planet.',
            'category_id': 6,
            'price': 650,
            'stock': 80,
            'brand': 'PureEarth',
            'image': 'https://images.unsplash.com/photo-1616627561950-9f746e330187?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_eco_friendly': True,
            'eco_description': 'GOTS-certified organic cotton. Zero harmful chemicals. Biodegradable packaging.'
        },
    ]

    added = 0
    for pdata in new_eco_products:
        exists = Product.query.filter_by(name=pdata['name']).first()
        if not exists:
            product = Product(**pdata, seller_id=admin.id, status='active')
            db.session.add(product)
            print(f"  [ADDED] {pdata['name']}")
            added += 1
        else:
            print(f"  [SKIP] {pdata['name']} already exists")

    db.session.commit()
    
    # Final count
    eco_count = Product.query.filter_by(is_eco_friendly=True).count()
    print(f"\n[SUCCESS] {added} new eco products added. Total eco-friendly products: {eco_count}")
