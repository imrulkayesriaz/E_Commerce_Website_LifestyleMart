from app import app, db, Product
def update_image():
    with app.app_context():
        p = Product.query.filter_by(name="Leather Handbag").first()
        if p:
            p.image = '/static/uploads/leather_handbag.png'
            db.session.commit()
            print("Successfully updated Leather Handbag image!")
        else:
            print("Product not found.")

if __name__ == '__main__':
    update_image()
