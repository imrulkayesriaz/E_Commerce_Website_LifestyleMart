"""
LIFESTYLE MART - Python eCommerce Platform
Main Flask application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FloatField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv
from functools import wraps
from payment_gateway import SSLCommerzGateway
try:
    import openai
except ImportError:
    openai = None

load_dotenv()
payment_gateway = SSLCommerzGateway()

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    # Use local SQLite for development, environment variable for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecommerce.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# OpenAI Configuration
if openai:
    openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.Enum('user', 'admin', 'seller'), default='user')
    shop_name = db.Column(db.String(100))
    shop_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    products = db.relationship('Product', backref='seller', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    brand = db.Column(db.String(100))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_featured = db.Column(db.Boolean, default=False)
    is_eco_friendly = db.Column(db.Boolean, default=False)
    eco_description = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled'), default='pending')
    payment_method = db.Column(db.Enum('cod', 'bkash', 'nagad', 'card', 'gift_card'), default='cod')
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed'), default='pending')
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # New fields for enhanced features
    delivery_type = db.Column(db.Enum('standard', 'express'), default='standard')
    gift_card_code = db.Column(db.String(50))
    gift_card_amount = db.Column(db.Float, default=0)
    tracking_number = db.Column(db.String(100))
    courier_name = db.Column(db.String(100))
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    delivery_notes = db.Column(db.Text)
    order_review = db.Column(db.Text)
    order_rating = db.Column(db.Integer)  # 1-5 stars for overall order experience
    is_gift = db.Column(db.Boolean, default=False)
    gift_message = db.Column(db.Text)
    gift_wrap = db.Column(db.Boolean, default=False)
    
    # Payment Gateway fields
    transaction_id = db.Column(db.String(100), unique=True)
    val_id = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    status = db.Column(db.Enum('approved', 'pending', 'rejected'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FlashDeal(db.Model):
    __tablename__ = 'flash_deals'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)  # e.g., 20 for 20% off
    original_price = db.Column(db.Float, nullable=False)
    deal_price = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    product = db.relationship('Product', backref='flash_deals')

class Offer(db.Model):
    __tablename__ = 'offers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.Enum('percentage', 'fixed'), default='percentage')
    discount_value = db.Column(db.Float, nullable=False)  # percentage or fixed amount
    min_purchase = db.Column(db.Float, default=0)  # minimum purchase amount
    max_discount = db.Column(db.Float, nullable=True)  # maximum discount cap
    code = db.Column(db.String(50), unique=True)  # promo code
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GiftCard(db.Model):
    __tablename__ = 'gift_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # who bought it
    recipient_email = db.Column(db.String(100))  # email of recipient
    message = db.Column(db.Text)
    is_redeemed = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    purchaser = db.relationship('User', foreign_keys=[purchaser_id], backref='purchased_gift_cards')

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='wishlist_items', lazy=True)
    product = db.relationship('Product', backref='wishlisted_by', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    product = db.relationship('Product', backref='related_messages')

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone Number')
    address = TextAreaField('Address')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    brand = StringField('Brand')
    image = StringField('Image URL')
    is_featured = BooleanField('Featured Product')
    is_eco_friendly = BooleanField('Eco-Friendly Product')
    eco_description = TextAreaField('Eco Description (Why is it sustainable?)')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', 
                         choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
                         coerce=int, validators=[DataRequired()])
    review_text = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=500)])

class PaymentForm(FlaskForm):
    payment_method = SelectField('Payment Method',
                                choices=[('cod', 'Cash on Delivery'),
                                        ('bkash', 'bKash'),
                                        ('nagad', 'Nagad'),
                                        ('card', 'Credit/Debit Card'),
                                        ('gift_card', 'Gift Card')],
                                validators=[DataRequired()])
    phone_number = StringField('Phone Number')  # optional - pulled from user profile
    transaction_id = StringField('Transaction ID (for bKash/Nagad)')
    card_number = StringField('Card Number')
    card_expiry = StringField('Expiry Date (MM/YY)')
    card_cvv = StringField('CVV')
    gift_card_code = StringField('Gift Card Code')

class OrderTrackingForm(FlaskForm):
    tracking_number = StringField('Tracking Number', validators=[DataRequired()])
    courier_name = SelectField('Courier Service',
                               choices=[('pathao', 'Pathao'),
                                       ('redx', 'RedX'),
                                       ('steadfast', 'Steadfast'),
                                       ('ecourier', 'eCourier'),
                                       ('other', 'Other')],
                               validators=[DataRequired()])
    estimated_delivery = DateField('Estimated Delivery', format='%Y-%m-%d')
    delivery_notes = TextAreaField('Delivery Notes')

class OrderReviewForm(FlaskForm):
    order_rating = SelectField('Order Rating',
                               choices=[(5, '5 Stars - Excellent'),
                                       (4, '4 Stars - Very Good'),
                                       (3, '3 Stars - Good'),
                                       (2, '2 Stars - Fair'),
                                       (1, '1 Star - Poor')],
                               coerce=int, validators=[DataRequired()])
    order_review = TextAreaField('Order Review', validators=[DataRequired(), Length(min=10, max=500)])

class GiftCardForm(FlaskForm):
    gift_card_code = StringField('Gift Card Code', validators=[DataRequired(), Length(min=8, max=50)])
    gift_message = TextAreaField('Gift Message')
    gift_wrap = BooleanField('Gift Wrapping (+৳50)')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['seller', 'admin']:
            flash('Seller access required. Please register as a seller to access this page.', 'warning')
            return redirect(url_for('profile'))
        return f(*args, **kwargs)
    return decorated_function

def generate_order_number():
    return f"LSM{datetime.now().strftime('%Y%m%d')}{secrets.randbelow(10000):04d}"

# Routes
@app.route('/')
def index():
    products = Product.query.filter_by(is_featured=True, status='active').limit(8).all()
    categories = Category.query.all()
    # Get active flash deals
    flash_deals = FlashDeal.query.filter_by(is_active=True).filter(
        FlashDeal.end_time > datetime.utcnow()
    ).order_by(FlashDeal.end_time.asc()).limit(4).all()
    
    # Get brand seller IDs for direct messaging
    brand_emails = {
        'Aarong': 'aarong@seller.bd',
        'Apex': 'apex@seller.bd',
        'Yellow': 'yellow@seller.bd',
        'Walton': 'walton@seller.bd'
    }
    brand_seller_ids = {}
    for brand_name, email in brand_emails.items():
        seller = User.query.filter_by(email=email).first()
        if seller:
            brand_seller_ids[brand_name] = seller.id
            
    # Get eco-friendly products for Green Choice spotlight (newest first)
    eco_products = Product.query.filter_by(is_eco_friendly=True, status='active').order_by(Product.id.desc()).limit(4).all()
    
    return render_template('index.html', 
                          products=products, 
                          categories=categories, 
                          flash_deals=flash_deals,
                          brand_seller_ids=brand_seller_ids,
                          eco_products=eco_products)

@app.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    brand = request.args.get('brand', '')
    search = request.args.get('search', '')
    # Handle both '1' (from links) and 'on' (from checkbox form submission)
    eco_friendly_raw = request.args.get('eco_friendly', '')
    eco_friendly = bool(eco_friendly_raw and eco_friendly_raw not in ('0', 'false', ''))
    sort = request.args.get('sort', 'name')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Product.query.filter_by(status='active')
    
    if eco_friendly:
        query = query.filter_by(is_eco_friendly=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if brand:
        query = query.filter_by(brand=brand)
    
    if search:
        query = query.filter(Product.name.contains(search) | Product.description.contains(search) | Product.brand.contains(search))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.name.asc())
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    # Get unique brand names for the filter
    brands = db.session.query(Product.brand).filter(Product.status == 'active', Product.brand != None).distinct().all()
    brands = [b[0] for b in brands if b[0]]
    
    return render_template('shop.html', products=products, categories=categories, brands=brands,
                         category_id=category_id, brand=brand, search=search, sort=sort,
                         min_price=min_price, max_price=max_price, eco_friendly=eco_friendly)



@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    if product.status != 'active':
        return redirect(url_for('shop'))
    
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'active'
    ).limit(4).all()
    
    reviews = Review.query.filter_by(product_id=id, status='approved').order_by(Review.created_at.desc()).all()
    
    return render_template('product.html', product=product, related_products=related_products, reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists', 'danger')
            return render_template('signup.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Get user's orders
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(10).all()
    return render_template('profile.html', orders=orders)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    shop_name = request.form.get('shop_name')
    shop_description = request.form.get('shop_description')
    
    if name:
        current_user.name = name
    if phone:
        current_user.phone = phone
    if address:
        current_user.address = address
    if shop_name:
        current_user.shop_name = shop_name
    if shop_description:
        current_user.shop_description = shop_description
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/become_seller', methods=['GET', 'POST'])
@login_required
def become_seller():
    if current_user.role == 'seller':
        return redirect(url_for('seller_dashboard'))
    
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        shop_description = request.form.get('shop_description')
        
        if not shop_name:
            flash('Shop name is required.', 'danger')
            return render_template('become_seller.html')
        
        current_user.role = 'seller'
        current_user.shop_name = shop_name
        current_user.shop_description = shop_description
        db.session.commit()
        
        flash('Congratulations! You are now a registered seller on Lifestyle Mart.', 'success')
        return redirect(url_for('seller_dashboard'))
        
    return render_template('become_seller.html')

# Seller Routes
@app.route('/seller/dashboard')
@seller_required
def seller_dashboard():
    products_count = Product.query.filter_by(seller_id=current_user.id).count()
    # Simplified: Get all orders that contain products from this seller
    # In a more complex system, we would have a separate SellerOrder model
    seller_products = Product.query.filter_by(seller_id=current_user.id).all()
    product_ids = [p.id for p in seller_products]
    
    # Get recent order items for this seller's products
    recent_sales = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).order_by(OrderItem.id.desc()).limit(10).all()
    
    total_sales = sum(item.total for item in OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all())
    
    return render_template('seller/dashboard.html', 
                         products_count=products_count,
                         recent_sales=recent_sales,
                         total_sales=total_sales)

@app.route('/seller/products')
@seller_required
def seller_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('seller/products.html', products=products)

@app.route('/seller/products/add', methods=['GET', 'POST'])
@seller_required
def seller_add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            category_id=form.category_id.data,
            price=form.price.data,
            stock=form.stock.data,
            brand=form.brand.data,
            image=form.image.data,
            is_featured=form.is_featured.data,
            is_eco_friendly=form.is_eco_friendly.data,
            eco_description=form.eco_description.data,
            seller_id=current_user.id,
            status='active'
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product listed successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    return render_template('seller/product_form.html', form=form, title='Add New Product')

@app.route('/seller/products/edit/<int:id>', methods=['GET', 'POST'])
@seller_required
def seller_edit_product(id):
    product = Product.query.get_or_404(id)
    # Security check: ensure the product belongs to this seller
    if product.seller_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_products'))
        
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.brand = form.brand.data
        product.image = form.image.data
        product.is_featured = form.is_featured.data
        product.is_eco_friendly = form.is_eco_friendly.data
        product.eco_description = form.eco_description.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    return render_template('seller/product_form.html', form=form, title='Edit Product')

@app.route('/seller/products/delete/<int:id>')
@seller_required
def seller_delete_product(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('seller_products'))
        
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('seller_products'))

# Messaging Routes
@app.route('/inbox')
@login_required
def inbox():
    # Get all users the current user has messaged or received messages from
    sent_to = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received_from = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    
    # Combine and get unique user IDs
    user_ids = [uid[0] for uid in sent_to.union(received_from).all()]
    
    # Fetch user objects for these IDs
    conversations = []
    for uid in set(user_ids):
        user = User.query.get(uid)
        if user:
            # Get the last message in this conversation
            last_msg = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == uid)) |
                ((Message.sender_id == uid) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            
            conversations.append({
                'user': user,
                'last_message': last_msg
            })
            
    # Sort conversations by last message time
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)
    
    return render_template('chat.html', conversations=conversations, active_chat=None)

@app.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)
    
    # Mark messages from this user to me as read
    Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    # Get all messages in this conversation
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Also get all conversations for the sidebar
    sent_to = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received_from = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    u_ids = [uid[0] for uid in sent_to.union(received_from).all()]
    if user_id not in u_ids: u_ids.append(user_id) # ensure current chat is in list
    
    conversations = []
    for uid in set(u_ids):
        user = User.query.get(uid)
        if user:
            last_msg = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == uid)) |
                ((Message.sender_id == uid) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            conversations.append({'user': user, 'last_message': last_msg})
    
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)
    
    return render_template('chat.html', conversations=conversations, active_chat=other_user, messages=messages)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    receiver_id = request.form.get('receiver_id', type=int)
    content = request.form.get('content')
    product_id = request.form.get('product_id', type=int)
    
    if not receiver_id or not content:
        flash('Invalid message data.', 'danger')
        return redirect(request.referrer or url_for('inbox'))
    
    receiver = User.query.get_or_404(receiver_id)
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        product_id=product_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('chat', user_id=receiver_id))

@app.context_processor
def inject_unread_messages_count():
    if current_user.is_authenticated:
        count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        return dict(unread_messages_count=count)
    return dict(unread_messages_count=0)

@app.route('/api/assistant', methods=['POST'])
def assistant():
    import json as _json
    data = request.json
    user_query = data.get('query', '').strip()
    history = data.get('history', [])

    if not user_query:
        return jsonify({'response': "I didn't catch that. How can I help you today? 😊"})

    q = user_query.lower()

    # ── SMART INTENT-BASED FALLBACK (works without OpenAI) ──────────────────
    def smart_fallback(query):
        q = query.lower()

        # ── Greeting / Hello ────────────────────────────────────────────────
        if any(w in q for w in ['hello', 'hi', 'hey', 'salam', 'assalam', 'good morning', 'good afternoon', 'good evening', 'how are you']):
            return {
                'response': "Hello! 👋 I'm your **Lifestyle Mart Shopping Assistant**. I can help you:\n\n• 🌿 Find eco-friendly products\n• 👟 Search for specific items\n• 📦 Track your orders\n• 📋 Answer store policy questions\n\nWhat can I help you with today?",
                'products': []
            }

        # ── Return / Refund Policy ───────────────────────────────────────────
        if any(w in q for w in ['return', 'refund', 'exchange', 'send back', 'money back', 'policy']):
            return {
                'response': "♻️ **Our Return & Refund Policy:**\n\n✅ **7-Day Free Returns** on most items\n✅ Items must be unused and in original packaging\n✅ Refunds are processed within **3–5 business days**\n✅ Exchange available for size/colour issues\n\n❌ Non-returnable items: Innerwear, perishables, and custom orders.\n\nTo initiate a return, go to **My Orders** → Select Order → Request Return.",
                'products': []
            }

        # ── Delivery / Shipping ──────────────────────────────────────────────
        if any(w in q for w in ['delivery', 'shipping', 'ship', 'how long', 'arrive', 'dispatch', 'courier', 'express', 'fast deliver']):
            return {
                'response': "🚚 **Delivery Information:**\n\n📦 **Standard Delivery** — 3–5 business days\n⚡ **Express Delivery** — 1–2 business days (+৳100)\n🎁 **Free Shipping** on orders over ৳5,000\n\n**Courier Partners:** Pathao, RedX, Steadfast, eCourier\n\nYou can track your order anytime using the **Track Order** link at the top of the page! 📍",
                'products': []
            }

        # ── Payment Methods ──────────────────────────────────────────────────
        if any(w in q for w in ['payment', 'pay', 'bkash', 'nagad', 'card', 'cash', 'cod', 'online pay', 'method', 'how to pay']):
            return {
                'response': "💳 **We accept the following payment methods:**\n\n💵 **Cash on Delivery (COD)** — Pay when delivered\n📱 **bKash** — Mobile banking\n📱 **Nagad** — Mobile banking\n💳 **Credit/Debit Card** — Visa, Mastercard, Amex\n🎁 **Gift Cards** — Lifestyle Mart gift cards\n\nAll online transactions are **100% secure** and encrypted. 🔒",
                'products': []
            }

        # ── Gift Cards ───────────────────────────────────────────────────────
        if any(w in q for w in ['gift card', 'gift', 'voucher', 'coupon', 'promo', 'discount code', 'redeem']):
            return {
                'response': "🎁 **Gift Cards & Promo Codes:**\n\n🎄 You can **purchase Gift Cards** from your profile page and send them to anyone via email.\n\n💰 To **apply a promo code**: Add items to your cart → Enter code at checkout → Discount is applied automatically!\n\n🌟 **Current Offer:** Use code **LIFESTYLE50** for **50% off** select BD Brand products!",
                'products': []
            }

        # ── Order Tracking ───────────────────────────────────────────────────
        if any(w in q for w in ['track', 'where is my order', 'my order', 'order status', 'package', 'parcel']):
            return {
                'response': "📍 **Order Tracking:**\n\nYou can track your order in **2 ways:**\n\n1️⃣ Click **\"Track Order\"** in the top navigation bar and enter your order number.\n2️⃣ Go to **My Account → My Orders** and click on any order to see its live status.\n\n📞 Need help? Call our hotline: **16263** (Sat–Thu, 10AM–10PM)",
                'products': []
            }

        # ── Eco-friendly / Sustainable ───────────────────────────────────────
        if any(w in q for w in ['eco', 'green', 'sustainable', 'environment', 'natural', 'organic', 'bamboo', 'jute', 'biodegradable', 'planet']):
            eco_products = Product.query.filter_by(is_eco_friendly=True, status='active').limit(4).all()
            product_list = [{
                'id': p.id, 'name': p.name,
                'price': f'৳{p.price:.0f}', 'image': p.image,
                'url': url_for('product_detail', id=p.id)
            } for p in eco_products]
            msg = ("🌿 **Green Choice Collection — Our Eco-Friendly Products:**\n\n"
                   "We're committed to sustainability! Here are products that are ethically sourced and environmentally friendly. "
                   "Each carries our **🌱 Eco Badge** of approval.\n\n"
                   "➡️ [View all eco-friendly products](/shop?eco_friendly=1)")
            if not eco_products:
                msg = "🌿 We're expanding our eco-friendly range! Check back soon for sustainably sourced products."
            return {'response': msg, 'products': product_list}

        # ── Shoes / Footwear ─────────────────────────────────────────────────
        if any(w in q for w in ['shoe', 'shoes', 'footwear', 'sneaker', 'sandal', 'loafer', 'boot', 'heels', 'oxford', 'slipper']):
            products = Product.query.filter(
                db.or_(Product.name.ilike('%shoe%'), Product.name.ilike('%sneaker%'),
                       Product.name.ilike('%footwear%'), Product.name.ilike('%oxford%'),
                       Product.name.ilike('%sandal%'), Product.name.ilike('%boot%'),
                       Product.category.has(name='Shoes'))
            ).filter_by(status='active').limit(4).all()
            product_list = [{'id': p.id, 'name': p.name, 'price': f'৳{p.price:.0f}', 'image': p.image, 'url': url_for('product_detail', id=p.id)} for p in products]
            msg = "👟 **Footwear Collection:**\n\nHere are some great shoes from our collection!" if products else "👟 We have a great footwear collection! Try searching the shop for 'shoes' to see all options."
            return {'response': msg, 'products': product_list}

        # ── Seller / Sell on Platform ────────────────────────────────────────
        if any(w in q for w in ['sell', 'seller', 'vendor', 'become seller', 'my shop', 'open shop']):
            return {
                'response': "🏪 **Sell on Lifestyle Mart:**\n\nBecome a seller and reach thousands of customers!\n\n✅ Easy product listing\n✅ Manage orders from your dashboard\n✅ Integrated payment collection\n\n👉 Click **\"Sell on Lifestyle Mart\"** at the top of the page to get started!",
                'products': []
            }

        # ── Contact / Support ────────────────────────────────────────────────
        if any(w in q for w in ['contact', 'support', 'help', 'phone', 'hotline', 'email', 'call', 'complaint']):
            return {
                'response': "📞 **Contact & Support:**\n\n📱 **Hotline:** 16263 (Sat–Thu, 10AM–10PM)\n📧 **Email:** support@lifestylemart.bd\n📍 **Address:** 123 Fashion Street, Dhanmondi, Dhaka-1205\n\nYou can also **message any seller directly** from a product page using the 💬 Message button!",
                'products': []
            }

        # ── Generic Product Search ───────────────────────────────────────────
        stop_words = {'i', 'want', 'need', 'buy', 'find', 'show', 'me', 'some', 'a', 'an', 'the', 'please', 'can', 'you', 'get', 'looking', 'for', 'suggest', 'recommend'}
        search_terms = [w for w in q.split() if w not in stop_words and len(w) > 2]

        if search_terms:
            products = Product.query.filter(
                db.or_(
                    *[Product.name.ilike(f'%{t}%') for t in search_terms],
                    *[Product.description.ilike(f'%{t}%') for t in search_terms],
                    *[Product.brand.ilike(f'%{t}%') for t in search_terms]
                )
            ).filter_by(status='active').limit(4).all()

            if products:
                product_list = [{'id': p.id, 'name': p.name, 'price': f'৳{p.price:.0f}', 'image': p.image, 'url': url_for('product_detail', id=p.id)} for p in products]
                return {'response': f"🛍️ Here are some products matching **\"{user_query}\"**:", 'products': product_list}

        # ── No match ─────────────────────────────────────────────────────────
        return {
            'response': ("🤖 I'm not sure about that, but I can help you with:\n\n"
                         "• 🌿 **Eco-friendly products** — ask \"show eco products\"\n"
                         "• 👟 **Finding items** — ask \"find shoes\" or any product\n"
                         "• 📦 **Order tracking** — ask \"track my order\"\n"
                         "• 📋 **Policies** — ask \"return policy\" or \"delivery times\"\n"
                         "• 💳 **Payments** — ask \"payment methods\"\n\n"
                         "What can I help you with? 😊"),
            'products': []
        }
    # ── END SMART FALLBACK ───────────────────────────────────────────────────

    # Try OpenAI if configured; otherwise use smart fallback
    if not openai or not openai.api_key:
        result = smart_fallback(user_query)
        return jsonify(result)

    try:
        # Get all active products to provide context to AI
        available_products = Product.query.filter_by(status='active').limit(30).all()
        product_context = "\n".join([f"- {p.name} (Price: ৳{p.price}, Eco-friendly: {'Yes' if p.is_eco_friendly else 'No'})" for p in available_products])

        system_prompt = f"""You are the friendly and helpful Lifestyle Mart Shopping Assistant.
        Your goal is to help users find products, answer questions, and provide excellent customer service.

        Store Policies & Info:
        - Free shipping on orders over ৳5000.
        - Delivery time: Standard is 3-5 days, Express is 1-2 days (+৳100).
        - Return policy: 7 days free returns for most items.
        - Payment options: Cash on Delivery, bKash, Nagad, Credit/Debit cards, Gift Cards.
        - Promo code: LIFESTYLE50 for 50% off select BD Brand products.
        - For order tracking, direct users to the 'Track Order' link in the top navigation.

        Available Products Context:
        {product_context}

        Based on the user's request and previous messages, provide a helpful and conversational response.
        If the user asks for "eco-friendly" or "sustainable", explicitly prioritize products marked as Eco-friendly.
        Identify up to 3 most relevant product names from the list if applicable to their query.

        Respond ONLY in valid JSON format exactly as follows, with no extra markdown or text outside the JSON:
        {{
            "message": "A friendly, conversational response to the user. Keep it concise but helpful.",
            "suggested_product_names": ["Name 1", "Name 2"]
        }}"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add limited history (last 4 messages) to maintain context without overloading tokens
        for msg in history[-4:]:
            messages.append({"role": msg['role'], "content": msg['content']})

        messages.append({"role": "user", "content": user_query})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        raw_message = response.choices[0].message.content.strip()
        # Clean up potential markdown formatting that OpenAI sometimes adds
        if raw_message.startswith("```json"):
            raw_message = raw_message[7:]
        if raw_message.endswith("```"):
            raw_message = raw_message[:-3]

        ai_response = _json.loads(raw_message.strip())

        suggested_names = ai_response.get('suggested_product_names', [])
        found_products = Product.query.filter(Product.name.in_(suggested_names)).all()

        product_list = [{
            'id': p.id, 'name': p.name,
            'price': f'৳{p.price:.0f}', 'image': p.image,
            'url': url_for('product_detail', id=p.id)
        } for p in found_products]

        return jsonify({
            'response': ai_response.get('message'),
            'products': product_list
        })

    except Exception as e:
        print(f"OpenAI Error: {e} — falling back to smart fallback")
        result = smart_fallback(user_query)
        return jsonify(result)



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        product = Product.query.get(int(product_id))
        if product and product.status == 'active':
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('cart.html', products=products, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({'success': False, 'message': 'Not enough stock available'})
    
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    
    cart_count = sum(cart.values())
    
    # Return JSON for AJAX/fetch requests (main.js sends X-Requested-With header)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True, 
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count
        })
    
    # Regular form submissions (non-JS fallback)
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart_count')
def cart_count_api():
    """Return the current cart item count as JSON for the header badge."""
    cart = session.get('cart', {})
    count = sum(cart.values())
    return jsonify({'count': count})


@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    
    cart = session.get('cart', {})
    
    if quantity > 0:
        product = Product.query.get(product_id)
        if product and product.stock >= quantity:
            cart[product_id] = quantity
        else:
            if request.headers.get('Accept') and 'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': False, 'message': 'Not enough stock available'})
            flash('Not enough stock available', 'warning')
            return redirect(url_for('cart'))
    else:
        cart.pop(product_id, None)
    
    session['cart'] = cart
    
    if request.headers.get('Accept') and 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'success': True,
            'cart_count': sum(cart.values())
        })
    return redirect(url_for('cart'))

@app.route('/apply_promo', methods=['POST'])
def apply_promo():
    code = request.form.get('promo_code', '').strip().upper()
    offer = Offer.query.filter_by(code=code, is_active=True).first()
    
    if not offer:
        flash('Invalid or expired promo code.', 'danger')
        return redirect(url_for('cart'))
        
    if offer.end_date < datetime.utcnow():
        flash('This promo code has expired.', 'danger')
        return redirect(url_for('cart'))
        
    # Calculate cart total
    cart_items = session.get('cart', {})
    total = 0
    for pid, qty in cart_items.items():
        product = Product.query.get(pid)
        if product:
            total += product.price * qty
            
    if total < offer.min_purchase:
        flash(f'Minimum purchase of ৳{offer.min_purchase} required for this promo.', 'warning')
        return redirect(url_for('cart'))
        
    # Calculate discount
    discount = 0
    if offer.discount_type == 'percentage':
        discount = total * (offer.discount_value / 100)
        if offer.max_discount:
            discount = min(discount, offer.max_discount)
    else:
        discount = min(offer.discount_value, total)
        
    session['promo_code'] = code
    session['promo_discount'] = discount
    flash(f'Promo code applied successfully!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_promo')
def remove_promo():
    session.pop('promo_code', None)
    session.pop('promo_discount', None)
    flash('Promo code removed.', 'info')
    return redirect(url_for('cart'))

@app.route('/cart_count')
def cart_count():
    cart = session.get('cart', {})
    return jsonify({'count': sum(cart.values())})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart
    
    if request.headers.get('Accept') and 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'success': True,
            'cart_count': sum(cart.values())
        })
    flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    product_id = request.form.get('product_id')
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Product already in wishlist'})
    
    wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Added to wishlist',
        'wishlist_count': Wishlist.query.filter_by(user_id=current_user.id).count()
    })

@app.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    product_id = request.form.get('product_id')
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Removed from wishlist',
            'wishlist_count': Wishlist.query.filter_by(user_id=current_user.id).count()
        })
    
    return jsonify({'success': False, 'message': 'Item not found'})

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))
    
    form = PaymentForm()
    
    if request.method == 'POST':
        form = PaymentForm(request.form)
        if form.validate_on_submit():
            # Process order
            order_number = generate_order_number()
            total_amount = 0
            order_items = []
            
            for product_id, quantity in cart.items():
                product = Product.query.get(product_id)
                if product and product.stock >= quantity:
                    subtotal = product.price * quantity
                    total_amount += subtotal
                    order_items.append({
                        'product_id': product_id,
                        'quantity': quantity,
                        'price': product.price,
                        'total': subtotal
                    })
                    # Update stock
                    product.stock -= quantity
            
            if not order_items:
                flash('No valid products in cart', 'danger')
                return redirect(url_for('cart'))
            
            # Create order with enhanced features
            delivery_type = request.form.get('delivery_type', 'standard')
            is_gift = request.form.get('is_gift') == 'on'
            gift_wrap = request.form.get('gift_wrap') == 'on'
            
            # Calculate gift card discount
            gift_card_amount = 0
            if form.payment_method.data == 'gift_card' and form.gift_card_code.data:
                # Simple gift card validation (in real app, this would check against database)
                gift_card_amount = min(500, total_amount * 0.1)  # 10% discount up to ৳500
            
            # Calculate delivery cost
            delivery_cost = 0
            if delivery_type == 'express':
                delivery_cost = 100  # Express delivery fee
            elif is_gift and gift_wrap:
                delivery_cost += 50   # Gift wrapping fee
            
            tax = total_amount * 0.15
            promo_discount = session.get('promo_discount', 0)
            
            final_total = total_amount + tax - promo_discount - gift_card_amount + delivery_cost
            
            notes = request.form.get('notes', '')
            if session.get('promo_code'):
                notes += f" [Promo Code Applied: {session.get('promo_code')}]"

            order = Order(
                user_id=current_user.id,
                order_number=order_number,
                total_amount=final_total,
                shipping_address=request.form.get('shipping_address'),
                billing_address=request.form.get('billing_address') or request.form.get('shipping_address'),
                payment_method=form.payment_method.data,
                payment_status='pending', # Always pending until gateway callback
                notes=notes,
                delivery_type=delivery_type,
                gift_card_code=form.gift_card_code.data,
                gift_card_amount=gift_card_amount,
                is_gift=is_gift,
                gift_message=request.form.get('gift_message'),
                gift_wrap=gift_wrap,
                estimated_delivery=datetime.utcnow() + (timedelta(days=1) if delivery_type == 'express' else timedelta(days=3))
            )
            db.session.add(order)
            db.session.flush()
            
            # Add order items
            for item in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=item['price'],
                    total=item['total']
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            # Clear cart
            session['cart'] = {}
            
            # If not COD, redirect to payment gateway
            if form.payment_method.data != 'cod':
                host_url = request.host_url.rstrip('/')
                gateway_url = payment_gateway.initiate_payment(order, current_user, host_url)
                
                if gateway_url:
                    return redirect(gateway_url)
                else:
                    flash('Failed to connect to payment gateway. Your order is placed as "Pending Payment".', 'warning')
            
            flash(f'Order {order_number} placed successfully!', 'success')
            return redirect(url_for('order_confirmation', id=order.id))
    
    # Calculate total for display
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if product:
            total += product.price * quantity
    
    return render_template('checkout.html', form=form, total=total, cart_items=len(cart))

# Payment Gateway Callback Routes
@app.route('/payment/success', methods=['POST'])
def payment_success():
    # SSLCommerz sends data via POST
    data = request.form
    tran_id = data.get('tran_id')
    val_id = data.get('val_id')
    
    order = Order.query.filter_by(order_number=tran_id).first_or_404()
    
    # Validate payment with SSLCommerz server
    if payment_gateway.validate_payment(val_id):
        order.payment_status = 'paid'
        order.val_id = val_id
        db.session.commit()
        flash(f'Payment successful for order {tran_id}!', 'success')
    else:
        flash(f'Payment validation failed for order {tran_id}.', 'danger')
        
    return redirect(url_for('order_confirmation', id=order.id))

@app.route('/payment/fail', methods=['POST'])
def payment_fail():
    tran_id = request.form.get('tran_id')
    order = Order.query.filter_by(order_number=tran_id).first()
    if order:
        order.payment_status = 'failed'
        db.session.commit()
        flash(f'Payment failed for order {tran_id}. Please try again.', 'danger')
    return redirect(url_for('cart'))

@app.route('/payment/cancel', methods=['POST'])
def payment_cancel():
    tran_id = request.form.get('tran_id')
    flash(f'Payment cancelled for order {tran_id}.', 'warning')
    return redirect(url_for('cart'))

@app.route('/payment/ipn', methods=['POST'])
def payment_ipn():
    # Instant Payment Notification (Asynchronous)
    data = request.form
    tran_id = data.get('tran_id')
    val_id = data.get('val_id')
    status = data.get('status')
    
    order = Order.query.filter_by(order_number=tran_id).first()
    if order and status == 'VALID':
        if payment_gateway.validate_payment(val_id):
            order.payment_status = 'paid'
            order.val_id = val_id
            db.session.commit()
            
    return jsonify({'status': 'received'})

@app.route('/payment/simulate/<order_number>')
@login_required
def simulate_payment(order_number):
    """A simple page to simulate the SSLCommerz gateway UI."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != current_user.id:
        return redirect(url_for('index'))
        
    return render_template('simulate_payment.html', order=order)

@app.route('/payment/process_simulation', methods=['POST'])
@login_required
def process_simulation():
    """Handles the form submission from the simulation page."""
    order_number = request.form.get('order_number')
    status = request.form.get('status')
    
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    if status == 'success':
        # Mocking the POST data SSLCommerz would send
        from werkzeug.datastructures import ImmutableMultiDict
        mock_data = ImmutableMultiDict([
            ('tran_id', order_number),
            ('val_id', f'VAL-{secrets.token_hex(8)}'),
            ('status', 'VALID')
        ])
        
        # We can't easily redirect with a POST method to our own route from here
        # so we'll just handle the logic directly or simulate a client-side form POST.
        # For simplicity in this demo, let's just update the order directly.
        order.payment_status = 'paid'
        order.val_id = f'MOCK-VAL-{secrets.token_hex(4)}'
        db.session.commit()
        flash(f'Payment successful (Simulated)!', 'success')
        return redirect(url_for('order_confirmation', id=order.id))
    else:
        flash(f'Payment failed (Simulated).', 'danger')
        return redirect(url_for('cart'))

@app.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm(request.form)
    
    if form.validate_on_submit():
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this product', 'warning')
            return redirect(url_for('product_detail', id=product_id))
        
        review = Review(
            product_id=product_id,
            user_id=current_user.id,
            rating=form.rating.data,
            review_text=form.review_text.data,
            status='approved'  # Auto-approve for demo
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
    
    return redirect(url_for('product_detail', id=product_id))

@app.route('/order_confirmation/<int:id>')
@login_required
def order_confirmation(id):
    order = Order.query.get_or_404(id)
    if order.user_id != current_user.id:
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/products.html', products=products, search=search)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            category_id=form.category_id.data,
            price=form.price.data,
            stock=form.stock.data,
            brand=form.brand.data,
            image=form.image.data,
            is_featured=form.is_featured.data
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, title='Add Product')

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.brand = form.brand.data
        product.image = form.image.data
        product.is_featured = form.is_featured.data
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, product=product, title='Edit Product')

@app.route('/admin/products/delete/<int:id>')
@admin_required
def admin_delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Order.query
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html', orders=orders, status=status)

@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/update_status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        
        # Set actual delivery time if delivered
        if new_status == 'delivered':
            order.actual_delivery = datetime.utcnow()
        
        db.session.commit()
        
        flash('Order status updated successfully!', 'success')
    else:
        flash('Invalid status!', 'danger')
    
    return redirect(url_for('admin_order_detail', id=id))

@app.route('/admin/orders/<int:id>/tracking', methods=['GET', 'POST'])
@admin_required
def admin_order_tracking(id):
    order = Order.query.get_or_404(id)
    form = OrderTrackingForm(obj=order)
    
    if form.validate_on_submit():
        order.tracking_number = form.tracking_number.data
        order.courier_name = form.courier_name.data
        order.estimated_delivery = form.estimated_delivery.data
        order.delivery_notes = form.delivery_notes.data
        
        db.session.commit()
        flash('Tracking information updated successfully!', 'success')
        return redirect(url_for('admin_order_detail', id=id))
    
    return render_template('admin/order_tracking.html', order=order, form=form)

@app.route('/admin/orders/<int:id>/review', methods=['GET', 'POST'])
@admin_required
def admin_order_review(id):
    order = Order.query.get_or_404(id)
    form = OrderReviewForm(obj=order)
    
    if form.validate_on_submit():
        order.order_rating = form.order_rating.data
        order.order_review = form.order_review.data
        
        db.session.commit()
        flash('Order review added successfully!', 'success')
        return redirect(url_for('admin_order_detail', id=id))
    
    return render_template('admin/order_review.html', order=order, form=form)

@app.route('/track-order')
def track_order():
    tracking_number = request.args.get('tracking_number')
    order = None
    
    if tracking_number:
        order = Order.query.filter_by(tracking_number=tracking_number).first()
    
    return render_template('track_order.html', order=order, tracking_number=tracking_number)

@app.route('/admin/users')
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.name.contains(search) | User.email.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@app.route('/admin/users/<int:id>')
@admin_required
def admin_user_detail(id):
    user = User.query.get_or_404(id)
    return render_template('admin/user_detail.html', user=user)

@app.route('/admin/users/<int:id>/toggle_role', methods=['POST'])
@admin_required
def admin_toggle_user_role(id):
    user = User.query.get_or_404(id)
    
    # Prevent changing own role
    if user.id == current_user.id:
        flash('You cannot change your own role!', 'danger')
        return redirect(url_for('admin_users'))
    
    new_role = request.form.get('role')
    if new_role in ['admin', 'user', 'seller']:
        user.role = new_role
        db.session.commit()
        
        flash(f'User role changed to {new_role} successfully!', 'success')
    else:
        flash('Invalid role!', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if name:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin_categories'))
        else:
            flash('Category name is required!', 'danger')
    
    return render_template('admin/category_form.html', title='Add Category')

@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if name:
            category.name = name
            category.description = description
            db.session.commit()
            
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin_categories'))
        else:
            flash('Category name is required!', 'danger')
    
    return render_template('admin/category_form.html', category=category, title='Edit Category')

@app.route('/admin/categories/delete/<int:id>')
@admin_required
def admin_delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has products
    if category.products:
        flash('Cannot delete category with products!', 'danger')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Review.query
    if status:
        query = query.filter(Review.status == status)
    
    reviews = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/reviews.html', reviews=reviews, status=status)

@app.route('/admin/reviews/approve/<int:id>')
@admin_required
def admin_approve_review(id):
    review = Review.query.get_or_404(id)
    review.status = 'approved'
    db.session.commit()
    
    flash('Review approved successfully!', 'success')
    return redirect(url_for('admin_reviews'))

@app.route('/admin/reviews/reject/<int:id>')
@admin_required
def admin_reject_review(id):
    review = Review.query.get_or_404(id)
    review.status = 'rejected'
    db.session.commit()
    
    flash('Review rejected successfully!', 'success')
    return redirect(url_for('admin_reviews'))

@app.route('/apply-promo', methods=['POST'])
@login_required
def apply_promo_old():
    code = request.form.get('promo_code', '').upper()
    order_id = request.form.get('order_id', type=int)
    
    if not code:
        flash('Please enter a promo code', 'danger')
        return redirect(url_for('checkout'))
    
    # Find active offer
    offer = Offer.query.filter_by(code=code, is_active=True).first()
    
    if not offer:
        flash('Invalid promo code', 'danger')
        return redirect(url_for('checkout'))
    
    # Check if offer is expired
    if offer.end_date < datetime.utcnow():
        flash('This promo code has expired', 'danger')
        return redirect(url_for('checkout'))
    
    # Get cart total
    cart = session.get('cart', {})
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Check minimum purchase
    if cart_total < offer.min_purchase:
        flash(f'Minimum purchase of ৳{offer.min_purchase:.0f} required for this code', 'danger')
        return redirect(url_for('checkout'))
    
    # Calculate discount
    if offer.discount_type == 'percentage':
        discount = cart_total * (offer.discount_value / 100)
        if offer.max_discount and discount > offer.max_discount:
            discount = offer.max_discount
    else:
        discount = offer.discount_value
    
    # Store promo in session
    session['promo_code'] = code
    session['promo_discount'] = float(discount)
    
    flash(f'Promo code applied! You saved ৳{discount:.0f}', 'success')
    return redirect(url_for('checkout'))

@app.route('/remove-promo')
@login_required
def remove_promo_old():
    session.pop('promo_code', None)
    session.pop('promo_discount', None)
    flash('Promo code removed', 'info')
    return redirect(url_for('checkout'))

@app.route('/apply-gift-card', methods=['POST'])
@login_required
def apply_gift_card():
    code = request.form.get('gift_card_code', '').upper()
    
    if not code:
        flash('Please enter a gift card code', 'danger')
        return redirect(url_for('checkout'))
    
    # Find gift card
    gift_card = GiftCard.query.filter_by(code=code).first()
    
    if not gift_card:
        flash('Invalid gift card code', 'danger')
        return redirect(url_for('checkout'))
    
    if gift_card.is_redeemed:
        flash('This gift card has already been redeemed', 'danger')
        return redirect(url_for('checkout'))
    
    if gift_card.expiry_date and gift_card.expiry_date < datetime.utcnow():
        flash('This gift card has expired', 'danger')
        return redirect(url_for('checkout'))
    
    if gift_card.balance <= 0:
        flash('This gift card has no remaining balance', 'danger')
        return redirect(url_for('checkout'))
    
    # Store gift card in session
    session['gift_card_code'] = code
    session['gift_card_balance'] = float(gift_card.balance)
    
    flash(f'Gift card applied! Balance: ৳{gift_card.balance:.0f}', 'success')
    return redirect(url_for('checkout'))

@app.route('/remove-gift-card')
@login_required
def remove_gift_card():
    session.pop('gift_card_code', None)
    session.pop('gift_card_balance', None)
    flash('Gift card removed', 'info')
    return redirect(url_for('checkout'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Create database tables
created = False

@app.before_request
def create_tables():
    global created
    if not created:
        db.create_all()
        created = True

@app.errorhandler(404)
def not_found(e):
    return render_template('500.html'), 404

@app.errorhandler(500)
def server_error(e):
    import traceback
    traceback.print_exc()
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
