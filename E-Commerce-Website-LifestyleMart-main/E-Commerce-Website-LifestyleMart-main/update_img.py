from app import app, db, Product
def update_image():
    with app.app_context():
        p = Product.query.filter_by(name="Women's Saree").first()
        if p:
            p.image = '/static/uploads/womens_saree.png'
            db.session.commit()
            print("Successfully updated image!")
        else:
            print("Product not found.")

if __name__ == '__main__':
    update_image()
