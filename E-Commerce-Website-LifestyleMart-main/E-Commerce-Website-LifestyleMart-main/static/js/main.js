// ============================================================
//  LIFESTYLE MART — main.js
//  Professional AJAX cart + UI interactions
// ============================================================

// ── CART NOTIFICATION TOAST ─────────────────────────────────
function showCartToast(productName, productImage, cartCount) {
    // Remove any existing toast
    document.querySelectorAll('.lm-cart-toast').forEach(el => el.remove());

    const toast = document.createElement('div');
    toast.className = 'lm-cart-toast';
    toast.innerHTML = `
        <div class="lm-cart-toast-inner">
            <div class="lm-cart-toast-header">
                <i class="fas fa-check-circle"></i>
                <span>Added to Cart!</span>
                <button class="lm-toast-close" onclick="this.closest('.lm-cart-toast').remove()">✕</button>
            </div>
            <div class="lm-cart-toast-body">
                ${productImage ? `<img src="${productImage}" alt="${productName}" class="lm-toast-img">` : '<div class="lm-toast-img-placeholder"><i class="fas fa-box"></i></div>'}
                <div class="lm-toast-product">
                    <div class="lm-toast-product-name">${productName}</div>
                    <div class="lm-toast-product-info">
                        <i class="fas fa-shopping-cart me-1"></i>${cartCount} item${cartCount !== 1 ? 's' : ''} in cart
                    </div>
                </div>
            </div>
            <div class="lm-cart-toast-actions">
                <a href="/cart" class="lm-toast-btn lm-toast-btn-primary">
                    <i class="fas fa-shopping-cart me-1"></i> View Cart
                </a>
                <a href="/checkout" class="lm-toast-btn lm-toast-btn-secondary">
                    <i class="fas fa-bolt me-1"></i> Checkout
                </a>
            </div>
            <div class="lm-toast-progress"><div class="lm-toast-progress-bar"></div></div>
        </div>
    `;

    // Inject styles if not already present
    if (!document.getElementById('lm-toast-styles')) {
        const style = document.createElement('style');
        style.id = 'lm-toast-styles';
        style.textContent = `
            .lm-cart-toast {
                position: fixed;
                top: 90px;
                right: 20px;
                z-index: 99999;
                width: 320px;
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 12px 40px rgba(0,0,0,0.2);
                animation: lm-slide-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
                font-family: 'Poppins', sans-serif;
            }
            .lm-cart-toast.lm-hiding {
                animation: lm-slide-out 0.35s ease forwards;
            }
            @keyframes lm-slide-in {
                from { transform: translateX(120%); opacity: 0; }
                to   { transform: translateX(0);    opacity: 1; }
            }
            @keyframes lm-slide-out {
                to { transform: translateX(120%); opacity: 0; }
            }
            .lm-cart-toast-inner {
                background: #fff;
            }
            .lm-cart-toast-header {
                background: linear-gradient(135deg, #28a745, #20c997);
                color: #fff;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 700;
                font-size: 0.9rem;
            }
            .lm-cart-toast-header i {
                font-size: 1.1rem;
            }
            .lm-cart-toast-header span { flex: 1; }
            .lm-toast-close {
                background: none;
                border: none;
                color: rgba(255,255,255,0.8);
                font-size: 1rem;
                cursor: pointer;
                padding: 0 4px;
                line-height: 1;
            }
            .lm-toast-close:hover { color: #fff; }
            .lm-cart-toast-body {
                padding: 14px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            .lm-toast-img {
                width: 56px;
                height: 56px;
                object-fit: cover;
                border-radius: 8px;
                border: 1px solid #eee;
                flex-shrink: 0;
            }
            .lm-toast-img-placeholder {
                width: 56px;
                height: 56px;
                background: #f5f5f5;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #bbb;
                font-size: 1.4rem;
                flex-shrink: 0;
            }
            .lm-toast-product { flex: 1; min-width: 0; }
            .lm-toast-product-name {
                font-size: 0.88rem;
                font-weight: 600;
                color: #222;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-bottom: 4px;
            }
            .lm-toast-product-info {
                font-size: 0.78rem;
                color: #f57224;
                font-weight: 500;
            }
            .lm-cart-toast-actions {
                display: flex;
                gap: 8px;
                padding: 12px 16px;
            }
            .lm-toast-btn {
                flex: 1;
                padding: 9px 12px;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 700;
                text-align: center;
                text-decoration: none;
                transition: all 0.2s;
            }
            .lm-toast-btn-primary {
                background: linear-gradient(135deg, #f57224, #ff9900);
                color: #fff;
            }
            .lm-toast-btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(245,114,36,0.4);
                color: #fff;
            }
            .lm-toast-btn-secondary {
                background: #f5f5f5;
                color: #333;
                border: 1px solid #e0e0e0;
            }
            .lm-toast-btn-secondary:hover {
                background: #e9ecef;
                color: #333;
            }
            .lm-toast-progress {
                height: 3px;
                background: #f0f0f0;
            }
            .lm-toast-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #f57224, #ff9900);
                animation: lm-shrink 3.5s linear forwards;
            }
            @keyframes lm-shrink { from { width: 100%; } to { width: 0%; } }

            /* Pulsing cart icon in header when item added */
            @keyframes lm-cart-pulse {
                0%   { transform: scale(1); }
                30%  { transform: scale(1.35); }
                60%  { transform: scale(0.9); }
                100% { transform: scale(1); }
            }
            .lm-cart-pulse { animation: lm-cart-pulse 0.5s ease; }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
        toast.classList.add('lm-hiding');
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// ── ADD TO CART (AJAX) ──────────────────────────────────────
function addToCart(productId, quantity = 1, productName = 'Product', productImage = null) {
    const btnEl = document.querySelector(`[data-product-id="${productId}"]`);
    if (btnEl) {
        btnEl.disabled = true;
        btnEl.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Adding...';
    }

    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            updateCartHeader(data.cart_count);
            showCartToast(productName, productImage, data.cart_count);
        } else {
            showSimpleNotification(data.message || 'Could not add to cart', 'danger');
        }
    })
    .catch(() => showSimpleNotification('Network error. Please try again.', 'danger'))
    .finally(() => {
        if (btnEl) {
            setTimeout(() => {
                btnEl.disabled = false;
                btnEl.innerHTML = '<i class="fas fa-check me-1"></i> Added!';
                setTimeout(() => {
                    btnEl.innerHTML = btnEl.dataset.originalText || '<i class="fas fa-cart-plus me-1"></i> Add to Cart';
                }, 1200);
            }, 400);
        }
    });
}

function updateQuantity(productId, change) {
    const form = document.querySelector(`form input[name="product_id"][value="${productId}"]`).closest('form');
    const input = form.querySelector('input[name="quantity"]');
    let newVal = parseInt(input.value) + change;
    if (newVal < 1) return;
    input.value = newVal;
    form.submit();
}


// ── INTERCEPT ALL ADD-TO-CART FORMS ─────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    // Handle any form with action="/add_to_cart"
    document.querySelectorAll('form[action="/add_to_cart"]').forEach(form => {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.dataset.originalText = btn.innerHTML;
            btn.dataset.productId = form.querySelector('[name="product_id"]')?.value;
            btn.setAttribute('data-product-id', form.querySelector('[name="product_id"]')?.value);
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const productId = form.querySelector('[name="product_id"]')?.value;
            const quantity  = parseInt(form.querySelector('[name="quantity"]')?.value) || 1;
            // Try to get product name/image from nearby DOM
            const card = form.closest('[class*="card"], [class*="product"], li');
            const productName  = card?.querySelector('h6, h5, .daraz-product-title, .product-title')?.textContent?.trim() || 'Product';
            const productImage = card?.querySelector('img')?.src || null;
            addToCart(productId, quantity, productName, productImage);
        });
    });

    // ── UPDATE HEADER CART COUNT ─────────────────────────────
    // Fetch live count from server on page load
    fetch('/cart_count').then(r => r.json()).then(d => updateCartHeader(d.count)).catch(() => {});

    // ── BACK TO TOP ──────────────────────────────────────────
    const backToTopBtn = document.getElementById('backToTop');
    window.addEventListener('scroll', function () {
        if (backToTopBtn) {
            backToTopBtn.style.display = window.pageYOffset > 300 ? 'flex' : 'none';
        }
    });
    backToTopBtn?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    // ── AUTO-HIDE FLASH ALERTS ───────────────────────────────
    setTimeout(() => {
        document.querySelectorAll('.alert-dismissible').forEach(alert => {
            try { new bootstrap.Alert(alert).close(); } catch (_) {}
        });
    }, 6000);

    // ── TOOLTIPS ─────────────────────────────────────────────
    [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        .forEach(el => new bootstrap.Tooltip(el));
});

// ── UPDATE CART BADGE IN HEADER ──────────────────────────────
function updateCartHeader(count) {
    const badges = document.querySelectorAll('.cart-count');
    badges.forEach(b => {
        b.textContent = count;
        b.classList.add('lm-cart-pulse');
        b.addEventListener('animationend', () => b.classList.remove('lm-cart-pulse'), { once: true });
    });
}

// ── SIMPLE NOTIFICATION (NON-CART) ──────────────────────────
function showSimpleNotification(message, type = 'success') {
    const el = document.createElement('div');
    el.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    el.style.cssText = 'top: 90px; right: 20px; z-index: 9999; min-width: 280px; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);';
    el.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'times-circle'} me-2"></i>${message}
        <button type="button" class="btn-close ms-2" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 400); }, 3500);
}

// ── WISHLIST AJAX ────────────────────────────────────────────
function toggleWishlist(productId, btn) {
    fetch('/add_to_wishlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `product_id=${productId}`
    })
    .then(r => r.json())
    .then(d => {
        showSimpleNotification(d.message, d.success ? 'success' : 'warning');
        if (d.success && btn) {
            btn.classList.add('text-danger');
            btn.querySelector('i')?.classList.replace('far', 'fas');
        }
    })
    .catch(() => showSimpleNotification('Please log in to save items.', 'warning'));
}
