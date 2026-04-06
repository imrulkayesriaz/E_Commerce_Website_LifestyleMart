from app import app, db, Product

def fix_product_images():
    with app.app_context():
        # Map product names to high-quality, verified working Unsplash URLs
        updates = {
            "Yellow Men's Polo Shirt": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&q=80&w=800",
            "Classic Denim Jeans": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&q=80&w=800",
            "Women's Saree": "/static/uploads/womens_saree.png",
            "Leather Handbag": "/static/uploads/leather_handbag.png",
            "Decorative Cushion": "https://images.unsplash.com/photo-1567016432779-094069958ea5?auto=format&fit=crop&q=80&w=800",
            "Wall Art": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?auto=format&fit=crop&w=800&q=80"
        }
        
        for name, url in updates.items():
            # Update all products matching the name (handles duplicates)
            products = Product.query.filter_by(name=name).all()
            if products:
                for p in products:
                    p.image = url
                    print(f"✅ Updated image for: {name}")
            else:
                # Try simple like match for fuzzy naming
                products = Product.query.filter(Product.name.ilike(f'%{name}%')).all()
                if products:
                    for p in products:
                        p.image = url
                        print(f"✅ Updated image (fuzzy) for: {p.name}")
                else:
                    print(f"❓ Could not find product: {name}")
        
        db.session.commit()
        print("\n[OK] All images updated successfully!")

if __name__ == "__main__":
    fix_product_images()
