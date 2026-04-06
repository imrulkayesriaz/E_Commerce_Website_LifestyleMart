# LIFESTYLE MART - Python eCommerce Platform

A modern, full-featured eCommerce platform built with Python Flask, HTML, CSS, and JavaScript. Features SQLite database (no setup required), user authentication, shopping cart, admin panel, and order management.

## 🚀 Features

### Frontend Features
- **Modern UI/UX**: Clean, responsive design with Bootstrap 5
- **Product Catalog**: 12 products across 6 categories
- **Shopping Cart**: JavaScript-based cart management
- **User Authentication**: Secure login, registration
- **Order Management**: Complete order tracking and history
- **Product Reviews**: User rating and review system
- **Wishlist**: Save favorite products
- **Responsive Design**: Mobile-first approach

### Backend Features (Python Flask)
- **RESTful API**: Clean API endpoints for all operations
- **Database ORM**: SQLAlchemy with SQLite (no external DB needed)
- **User Management**: Role-based access control (admin, user)
- **Order Processing**: Complete order workflow
- **Admin Panel**: Dashboard with statistics, product/category management
- **Security**: Password hashing, CSRF protection, input validation

### Technical Features
- **Python Backend**: Flask framework with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (file-based, auto-created)
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF for form validation
- **Security**: Bcrypt, CSRF tokens, input sanitization

## 🛠️ Technology Stack

### Backend
- **Python 3.11**
- **Flask 2.3.3** - Web framework
- **SQLAlchemy 2.0.21** - Database ORM
- **Flask-Login 0.6.3** - User authentication
- **Flask-WTF 1.1.1** - Form handling
- **Werkzeug 2.3.7** - Security utilities
- **Gunicorn 21.2.0** - WSGI server

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with Bootstrap 5
- **JavaScript** - Interactive functionality
- **Bootstrap 5** - UI framework
- **Font Awesome** - Icons

### Database
- **SQLite** - File-based database (no setup required)

## 📋 Requirements

- Python 3.8 or higher
- Pip package manager

## 🚀 Quick Start (Local)

### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd lifestyle-mart-python
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python database_setup.py
```

### 5. Run the Application
```bash
python app.py
```

### 6. Access the Application
- **Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin

## 🌐 Deployment Options

### Option 1: Replit (Easiest - 2 minutes)
1. Go to https://replit.com
2. Click "Create" → "Import from GitHub"
3. Paste your repo URL
4. Click "Import & Run"
5. Run: `pip install -r requirements.txt && python database_setup.py`
6. Click "Run" button
7. Share the URL with your teacher!

### Option 2: Render (Free)
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Name:** lifestylemart
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python database_setup.py`
   - **Start Command:** `gunicorn app:app`
6. Click "Create Web Service"

### Option 3: Railway (Free)
1. Go to https://railway.app
2. Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-deploys!

## 👤 Default Accounts

### Admin Account
- **Email:** admin@lifestylemart.com
- **Password:** admin123

### Test User Accounts
- **Email:** john@example.com
- **Password:** password123

- **Email:** jane@example.com
- **Password:** password123

## 📁 Project Structure

```
lifestyle-mart-python/
├── app.py                  # Main Flask application
├── database_setup.py       # Database initialization
├── requirements.txt        # Python dependencies
├── Procfile               # Process file for deployment
├── runtime.txt            # Python version
├── railway.toml           # Railway config
├── .github/workflows/     # GitHub Actions
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── shop.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   └── admin/            # Admin templates
├── static/                # Static files
│   ├── css/
│   └── js/
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ecommerce.db
```

## 🎨 Customization

### Colors and Theme
Edit CSS variables in `static/css/style.css`:
```css
:root {
    --primary-color: #FF6B35;
    --secondary-color: #2C3E50;
    --accent-color: #E67E22;
}
```

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **CSRF Protection**: Flask-WTF provides CSRF tokens
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **Session Security**: Flask-Login handles secure sessions
- **XSS Protection**: Jinja2 auto-escaping prevents XSS attacks

## 📊 Admin Features

The admin panel provides:
- **Dashboard**: Sales statistics and overview
- **User Management**: View and manage customer accounts
- **Product Management**: Add, edit, delete products
- **Order Management**: View orders and update status
- **Category Management**: Organize product categories
- **Review Management**: Approve/reject product reviews

## 🛒 eCommerce Features

### Shopping Cart
- JavaScript-based cart management
- Add/remove items
- Update quantities
- Stock validation
- Persistent cart (session-based)

### Checkout Process
- Multi-step checkout
- Address management
- Payment method selection (Cash on Delivery)
- Order confirmation

### Order Management
- Order tracking
- Status updates
- Order history
- Admin order processing

## 📱 Responsive Design

The platform is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - SQLite is file-based, no external DB needed
   - Run `python database_setup.py` to initialize

2. **Import Errors**
   - Activate virtual environment
   - Install all dependencies: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`

## 🔄 Updates

Version 1.0.0 - Initial Release
- Complete eCommerce platform
- Python Flask backend
- Modern HTML/CSS/JS frontend
- Admin panel
- User authentication
- Shopping cart
- Order management

---

**LIFESTYLE MART** - Your Fashion Destination 🛍️
