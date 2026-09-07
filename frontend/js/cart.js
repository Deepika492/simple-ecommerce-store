/**
 * AURASTORE - CART & SHOPPING BAG MANAGER
 */

const CartManager = {
  // Update navbar cart badge counter
  async updateBadge() {
    const badge = document.getElementById('nav-cart-badge');
    const mobileBadge = document.getElementById('mobile-cart-badge');
    if (!badge && !mobileBadge) return;

    if (!Auth.isLoggedIn()) {
      if (badge) { badge.textContent = '0'; badge.style.display = 'none'; }
      if (mobileBadge) { mobileBadge.textContent = '0'; mobileBadge.style.display = 'none'; }
      return;
    }

    try {
      const res = await ApiClient.get('/cart/');
      if (res.success && res.data) {
        const count = res.data.total_items || 0;
        if (badge) {
          badge.textContent = count;
          badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
        if (mobileBadge) {
          mobileBadge.textContent = count;
          mobileBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }
      }
    } catch (e) {
      if (badge) badge.textContent = '0';
      if (mobileBadge) mobileBadge.textContent = '0';
    }
  },

  // Add Item
  async addItem(productId, quantity = 1) {
    if (!Auth.isLoggedIn()) {
      showToast('Please sign in to add products to your cart.', 'warning');
      setTimeout(() => {
        window.location.href = `login.html?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
      }, 500);
      return;
    }

    try {
      const res = await ApiClient.post('/cart/', {
        product_id: productId,
        quantity: quantity
      });
      if (res.success) {
        showToast(res.message || 'Item added to your shopping cart!', 'success');
        this.updateBadge();
        // If on cart page, re-render
        if (document.getElementById('cart-items-container')) {
          this.renderCartPage();
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // Update item quantity
  async updateQuantity(itemId, quantity) {
    if (quantity < 1) {
      this.removeItem(itemId);
      return;
    }

    try {
      const res = await ApiClient.put(`/cart/${itemId}/`, { quantity });
      if (res.success) {
        this.updateBadge();
        this.renderCartPage();
      }
    } catch (err) {
      showToast(err.message, 'error');
      this.renderCartPage();
    }
  },

  // Remove Item
  async removeItem(itemId) {
    try {
      const res = await ApiClient.delete(`/cart/${itemId}/`);
      if (res.success) {
        showToast('Item removed from cart.', 'info');
        this.updateBadge();
        this.renderCartPage();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // Clear Entire Cart
  async clearAll() {
    if (!confirm('Are you sure you want to clear your entire cart?')) return;
    try {
      const res = await ApiClient.delete('/cart/clear/');
      if (res.success) {
        showToast('Cart has been cleared.', 'info');
        this.updateBadge();
        this.renderCartPage();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // Render Cart Page (`cart.html`)
  async renderCartPage() {
    const container = document.getElementById('cart-items-container');
    const summaryContainer = document.getElementById('cart-summary-container');
    if (!container) return;

    if (!Auth.isLoggedIn()) {
      container.innerHTML = `
        <div style="text-align:center; padding: 4.5rem 2rem; background:white; border-radius:var(--radius-xl); border:1px dashed var(--border-color); box-shadow:var(--shadow-sm);">
          <div style="width:72px; height:72px; border-radius:var(--radius-full); background:var(--primary-light); color:var(--primary); display:grid; place-items:center; margin:0 auto 1.25rem; font-size:1.8rem;">
            <i class="fas fa-lock"></i>
          </div>
          <h3 style="font-size:1.4rem; font-weight:800;">Please sign in to view your cart</h3>
          <p style="color:var(--text-muted); margin-top:0.4rem; max-width:420px; margin-left:auto; margin-right:auto;">Sign in to access your saved items, checkout faster, and track orders.</p>
          <a href="login.html?redirect=cart.html" class="btn btn-primary btn-lg" style="margin-top:1.5rem;"><i class="fas fa-sign-in-alt"></i> Sign In Now</a>
        </div>
      `;
      if (summaryContainer) summaryContainer.style.display = 'none';
      return;
    }

    try {
      const res = await ApiClient.get('/cart/');
      if (res.success && res.data) {
        const cart = res.data;
        const items = cart.items || [];

        if (items.length === 0) {
          container.innerHTML = `
            <div style="text-align:center; padding: 4.5rem 2rem; background:white; border-radius:var(--radius-xl); border:1px dashed var(--border-color); box-shadow:var(--shadow-sm);">
              <div style="width:72px; height:72px; border-radius:var(--radius-full); background:var(--bg-subtle); color:var(--text-light); display:grid; place-items:center; margin:0 auto 1.25rem; font-size:1.8rem;">
                <i class="fas fa-shopping-bag"></i>
              </div>
              <h3 style="font-size:1.4rem; font-weight:800;">Your shopping cart is empty</h3>
              <p style="color:var(--text-muted); margin-top:0.4rem; max-width:420px; margin-left:auto; margin-right:auto;">Looks like you haven't added anything to your cart yet. Explore our curated catalog for top electronics and lifestyle essentials.</p>
              <a href="products.html" class="btn btn-primary btn-lg" style="margin-top:1.5rem;"><i class="fas fa-compass"></i> Explore Products</a>
            </div>
          `;
          if (summaryContainer) summaryContainer.style.display = 'none';
          return;
        }

        if (summaryContainer) summaryContainer.style.display = 'block';

        // Render Cart Items List
        container.innerHTML = `
          <div class="cart-items-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid var(--border-color);">
              <h2 style="font-size:1.3rem; font-weight:800;"><i class="fas fa-shopping-bag" style="color:var(--primary); margin-right:6px;"></i> Cart Items (${cart.total_items})</h2>
              <button onclick="CartManager.clearAll()" class="btn btn-sm btn-secondary" style="color:var(--danger)">
                <i class="fas fa-trash-alt"></i> Clear Cart
              </button>
            </div>
            ${items.map(item => `
              <div class="cart-item-row" data-id="${item.id}">
                <img src="${item.product.image_url}" alt="${item.product.name}" class="cart-item-thumb" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
                <div>
                  <h4 class="cart-item-title">
                    <a href="product-details.html?id=${item.product.id}">${item.product.name}</a>
                  </h4>
                  <div class="cart-item-meta">
                    Category: <strong>${item.product.category_name || 'General'}</strong> | Unit: ₹${Number(item.product.price).toLocaleString('en-IN')}
                  </div>
                </div>
                <div>
                  <div class="quantity-stepper">
                    <button type="button" onclick="CartManager.updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <input type="number" value="${item.quantity}" readonly>
                    <button type="button" onclick="CartManager.updateQuantity(${item.id}, ${item.quantity + 1})" ${item.quantity >= item.product.stock ? 'disabled' : ''}>+</button>
                  </div>
                </div>
                <div class="cart-item-subtotal">
                  ₹${Number(item.item_total).toLocaleString('en-IN')}
                </div>
                <div>
                  <button onclick="CartManager.removeItem(${item.id})" class="btn btn-sm btn-ghost" style="color:var(--danger);" title="Remove Item">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        `;

        // Render Summary
        if (summaryContainer) {
          const isFreeShipping = Number(cart.shipping) === 0;
          const remainingForFree = Math.max(0, 1000 - Number(cart.subtotal));

          summaryContainer.innerHTML = `
            <div class="cart-summary-card">
              <h3 class="summary-title">Order Summary</h3>
              <div class="summary-row">
                <span>Subtotal (${cart.total_items} items)</span>
                <span>₹${Number(cart.subtotal).toLocaleString('en-IN')}</span>
              </div>
              <div class="summary-row">
                <span>Estimated GST (5%)</span>
                <span>₹${Number(cart.tax).toLocaleString('en-IN')}</span>
              </div>
              <div class="summary-row">
                <span>Shipping Fee</span>
                <span>${isFreeShipping ? '<strong style="color:var(--success); font-weight:800;">FREE</strong>' : '₹' + Number(cart.shipping).toLocaleString('en-IN')}</span>
              </div>
              
              ${!isFreeShipping ? `
                <div style="background:var(--primary-light); color:var(--primary-deep); padding:0.75rem 1rem; border-radius:var(--radius-md); font-size:0.82rem; margin:1rem 0; font-weight:600;">
                  <i class="fas fa-truck-fast"></i> Add ₹${remainingForFree.toLocaleString('en-IN')} more to unlock <strong>FREE Shipping</strong>!
                </div>
              ` : `
                <div style="background:var(--success-light); color:var(--success-dark); padding:0.75rem 1rem; border-radius:var(--radius-md); font-size:0.82rem; margin:1rem 0; font-weight:700;">
                  <i class="fas fa-check-circle"></i> You've qualified for Free Express Delivery!
                </div>
              `}

              <div class="summary-row total">
                <span>Total Amount</span>
                <span>₹${Number(cart.grand_total).toLocaleString('en-IN')}</span>
              </div>

              <a href="checkout.html" class="btn btn-primary btn-block btn-lg">
                Proceed to Checkout <i class="fas fa-arrow-right"></i>
              </a>

              <div style="text-align:center; margin-top:1.25rem; font-size:0.82rem; color:var(--text-muted); display:flex; align-items:center; justify-content:center; gap:0.5rem;">
                <i class="fas fa-shield-halved" style="color:var(--success);"></i> 256-bit Encrypted Checkout
              </div>
            </div>
          `;
        }
      }
    } catch (err) {
      container.innerHTML = `<p class="text-danger" style="text-align:center; padding:3rem;">Failed to load cart: ${err.message}</p>`;
    }
  }
};

// Global helper for navbar badge
function updateCartCount() {
  CartManager.updateBadge();
}
