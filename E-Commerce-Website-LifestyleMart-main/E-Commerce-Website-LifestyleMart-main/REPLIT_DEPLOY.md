# Deploy to Replit - Complete Guide

## Step 1: Create Replit Account
1. Go to https://replit.com
2. Sign up with GitHub or email
3. Verify your account

## Step 2: Import Your Project
1. Click **"Create"** (blue button top right)
2. Select **"Import from GitHub"**
3. Paste your repository URL:
   ```
   https://github.com/foysalpranto121/E-Commerce-Website-LifestyleMart
   ```
4. Click **"Import from GitHub"**
5. Wait for import to complete (1-2 minutes)

## Step 3: Configure Replit
1. **Select Template**: Choose "Python" template
2. **Set Run Command**: In the `.replit` file (create if not exists):
   ```
   run = "python app.py"
   ```

## Step 4: Install Dependencies
Open Shell (bottom panel) and run:
```bash
pip install -r requirements.txt
```

## Step 5: Initialize Database
In the same shell, run:
```bash
python database_setup.py
```

You should see output like:
```
[INFO] Created 42 products
[INFO] Created 4 flash deals
[INFO] Created 3 offers
[INFO] Created 3 gift cards
[INFO] Created 3 users
[OK] Database setup completed successfully!
```

## Step 6: Run the Application
1. Click the **"Run"** button (big green button at top)
2. Wait for server to start
3. Click the URL that appears (like `https://lifestylemart.yourname.repl.co`)

## Step 7: Test Both User & Admin

### Admin Login:
- URL: `https://your-app.repl.co/admin`
- Email: `admin@lifestylemart.com`
- Password: `admin123`

### User Login:
- URL: `https://your-app.repl.co/login`
- Email: `john@example.com` or `jane@example.com`
- Password: `password123`

## Step 8: Test All Features

### User Features:
1. ✅ Register new account
2. ✅ Browse 42 products with images
3. ✅ Add to cart (shows product image & price)
4. ✅ Apply promo codes (WELCOME10, SUMMER500, FASHION20)
5. ✅ View flash deals (4 active deals)
6. ✅ Gift cards (purchase & redeem)
7. ✅ Place order (checkout with address)
8. ✅ View order history
9. ✅ Write product reviews

### Admin Features:
1. ✅ Dashboard with statistics
2. ✅ Manage 42 products (add/edit/delete)
3. ✅ Manage 6 categories
4. ✅ View all orders & update status
5. ✅ Manage users
6. ✅ Manage reviews (approve/reject)
7. ✅ Create flash deals
8. ✅ Create offers/promo codes
9. ✅ View gift cards

## Step 9: Share with Your Teacher
Copy the Replit URL and share:
```
https://lifestylemart.yourname.repl.co
```

## Troubleshooting

### If "Module not found" error:
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug
```

### If database error:
```bash
rm -f ecommerce.db instance/ecommerce.db
python database_setup.py
```

### If port already in use:
The app uses port 5000 by default. Replit automatically assigns ports.

### To restart fresh:
1. Click "Stop" button
2. Run: `python database_setup.py`
3. Click "Run" button again

## Features Ready to Show:
- 📱 Responsive design (works on mobile/desktop)
- 🛍️ 42 products with real images
- 💰 Price range: 450 - 5500 BDT
- 🏷️ 6 categories
- 🎁 Flash deals with countdown
- 🎟️ Promo codes at checkout
- 🎫 Gift card system
- 🛒 Cart with product images
- 📦 Order placement & tracking
- 👤 User dashboard
- ⚙️ Admin panel
- ⭐ Product reviews

## Default Login Credentials:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@lifestylemart.com | admin123 |
| User 1 | john@example.com | password123 |
| User 2 | jane@example.com | password123 |
| User 3 | test@example.com | password123 |

---

**Your eCommerce app is ready for your teacher!** 🎉
