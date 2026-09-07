/**
 * AURASTORE - ORDERS & CHECKOUT MANAGER
 */

const Orders = {
  // Initialize Checkout Page (`checkout.html`)
  async initCheckoutPage() {
    if (!Auth.requireAuth('login.html')) return;

    const summaryContainer = document.getElementById('checkout-items-summary');
    const totalsContainer = document.getElementById('checkout-totals');
    const form = document.getElementById('checkout-form');

    // Auto-fill user information if available
    const user = Auth.getCurrentUser();
    if (user) {
      const nameInput = document.getElementById('shipping_name');
      if (nameInput && !nameInput.value) nameInput.value = user.username;
    }

    try {
      const res = await ApiClient.get('/cart/');
      if (res.success && res.data) {
        const cart = res.data;
        const items = cart.items || [];

        if (items.length === 0) {
          showToast('Your cart is empty. Please add items before checking out.', 'warning');
          setTimeout(() => window.location.href = 'products.html', 1000);
          return;
        }

        if (summaryContainer) {
          summaryContainer.innerHTML = items.map(item => `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; font-size:0.92rem;">
              <div style="display:flex; align-items:center; gap:0.85rem;">
                <img src="${item.product.image_url}" style="width:48px; height:48px; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border-color);" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
                <div>
                  <strong style="color:var(--text-main); font-size:0.95rem;">${item.product.name}</strong>
                  <div style="font-size:0.8rem; color:var(--text-muted);">Qty: ${item.quantity} × ₹${Number(item.product.price).toLocaleString('en-IN')}</div>
                </div>
              </div>
              <div style="font-weight:700; color:var(--text-main);">₹${Number(item.item_total).toLocaleString('en-IN')}</div>
            </div>
          `).join('');
        }

        if (totalsContainer) {
          const isFreeShipping = Number(cart.shipping) === 0;
          totalsContainer.innerHTML = `
            <div class="summary-row">
              <span>Subtotal</span>
              <span>₹${Number(cart.subtotal).toLocaleString('en-IN')}</span>
            </div>
            <div class="summary-row">
              <span>GST (5%)</span>
              <span>₹${Number(cart.tax).toLocaleString('en-IN')}</span>
            </div>
            <div class="summary-row">
              <span>Shipping</span>
              <span>${isFreeShipping ? '<strong style="color:var(--success)">FREE</strong>' : '₹' + Number(cart.shipping).toLocaleString('en-IN')}</span>
            </div>
            <div class="summary-row total">
              <span>Grand Total</span>
              <span>₹${Number(cart.grand_total).toLocaleString('en-IN')}</span>
            </div>
          `;
        }
      }
    } catch (err) {
      showToast('Failed to load cart summary: ' + err.message, 'error');
    }

    // Handle Form Submit
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        const payload = {
          shipping_name: document.getElementById('shipping_name').value.trim(),
          shipping_address: document.getElementById('shipping_address').value.trim(),
          phone: document.getElementById('phone').value.trim(),
          payment_method: document.querySelector('input[name="payment_method"]:checked')?.value || 'COD'
        };

        if (!payload.shipping_name || !payload.shipping_address || !payload.phone) {
          showToast('Please fill out all required shipping fields.', 'warning');
          return;
        }

        try {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing Order...`;

          const res = await ApiClient.post('/orders/', payload);
          if (res.success && res.data) {
            showToast('Your order has been placed successfully!', 'success', 5000);
            CartManager.updateBadge();
            setTimeout(() => {
              window.location.href = `orders.html?placed=${res.data.id}`;
            }, 600);
          }
        } catch (err) {
          showToast(err.message, 'error');
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      });
    }
  },

  // Helper for Order Status Timeline
  renderStatusTimeline(status) {
    const steps = ['PLACED', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED'];
    const statusIndex = steps.indexOf(status);

    if (status === 'CANCELLED') {
      return `
        <div style="background:var(--danger-light); color:var(--danger-dark); padding:1rem 1.25rem; border-radius:var(--radius-md); font-weight:700; text-align:center; display:flex; align-items:center; justify-content:center; gap:0.5rem;">
          <i class="fas fa-ban fa-lg"></i> This order has been CANCELLED
        </div>
      `;
    }

    return `
      <div class="status-timeline">
        ${steps.map((step, idx) => {
          let stepClass = '';
          if (idx < statusIndex) stepClass = 'completed';
          else if (idx === statusIndex) stepClass = 'active';

          return `
            <div class="timeline-step ${stepClass}">
              <div class="step-circle">
                ${idx < statusIndex ? '<i class="fas fa-check"></i>' : (idx + 1)}
              </div>
              <div class="step-label">${step}</div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  },

  // Helper for Status Badge Class
  getStatusBadgeClass(status) {
    switch (status) {
      case 'PLACED': return 'badge-status-placed';
      case 'CONFIRMED': return 'badge-status-confirmed';
      case 'PROCESSING': return 'badge-status-processing';
      case 'SHIPPED': return 'badge-status-shipped';
      case 'DELIVERED': return 'badge-status-delivered';
      case 'CANCELLED': return 'badge-status-cancelled';
      default: return 'badge-status-placed';
    }
  },

  // Initialize Order History Page (`orders.html`)
  async initOrdersPage() {
    if (!Auth.requireAuth('login.html')) return;

    const container = document.getElementById('orders-list-container');
    if (!container) return;

    const urlParams = new URLSearchParams(window.location.search);
    const justPlacedId = urlParams.get('placed');
    if (justPlacedId) {
      showToast(`Order #${justPlacedId} was confirmed! Thank you for shopping with AuraStore.`, 'success', 6000);
    }

    try {
      const res = await ApiClient.get('/orders/');
      if (res.success && res.data) {
        const orders = res.data;

        if (orders.length === 0) {
          container.innerHTML = `
            <div style="text-align:center; padding: 4.5rem 2rem; background:white; border-radius:var(--radius-xl); border:1px dashed var(--border-color); box-shadow:var(--shadow-sm);">
              <div style="width:72px; height:72px; border-radius:var(--radius-full); background:var(--bg-subtle); color:var(--text-light); display:grid; place-items:center; margin:0 auto 1.25rem; font-size:1.8rem;">
                <i class="fas fa-box-open"></i>
              </div>
              <h3 style="font-size:1.4rem; font-weight:800;">No orders found</h3>
              <p style="color:var(--text-muted); margin-top:0.4rem; max-width:420px; margin-left:auto; margin-right:auto;">You haven't placed any orders yet. Discover our latest collections and shop your favorites!</p>
              <a href="products.html" class="btn btn-primary btn-lg" style="margin-top:1.5rem;"><i class="fas fa-shopping-bag"></i> Start Shopping</a>
            </div>
          `;
          return;
        }

        container.innerHTML = orders.map(order => {
          const orderDate = new Date(order.created_at).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });

          return `
            <div class="order-card" id="order-${order.id}">
              <div class="order-card-header">
                <div>
                  <div style="font-size:1.15rem; font-weight:800; display:flex; align-items:center; gap:0.6rem;">
                    <span>Order #${order.id}</span>
                    <span class="badge badge-status ${this.getStatusBadgeClass(order.status)}">${order.status}</span>
                  </div>
                  <div style="font-size:0.84rem; color:var(--text-muted); margin-top:0.25rem;">
                    <i class="far fa-calendar-alt"></i> Placed on ${orderDate}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:1.35rem; font-weight:900; color:var(--primary);">₹${Number(order.total_amount).toLocaleString('en-IN')}</div>
                  <div style="font-size:0.82rem; color:var(--text-muted); font-weight:600;">
                    <i class="fas ${order.payment_method === 'COD' ? 'fa-money-bill-wave' : 'fa-credit-card'}"></i>
                    ${order.payment_method === 'COD' ? 'Cash on Delivery' : 'Instant Demo Payment'}
                  </div>
                </div>
              </div>

              <div class="order-card-body">
                <!-- Timeline Tracker -->
                ${this.renderStatusTimeline(order.status)}

                <!-- Items Breakdown -->
                <div style="margin-top:1.75rem;">
                  <h4 style="font-size:1rem; font-weight:700; margin-bottom:1rem; color:var(--text-main);">Ordered Items (${order.total_items})</h4>
                  <div style="display:flex; flex-direction:column; gap:0.85rem;">
                    ${order.items.map(item => `
                      <div style="display:flex; justify-content:space-between; align-items:center; padding:0.75rem 0; border-bottom:1px solid var(--border-color);">
                        <div style="display:flex; align-items:center; gap:1rem;">
                          <img src="${item.product_image}" style="width:52px; height:52px; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border-color);" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
                          <div>
                            <div style="font-weight:700; font-size:0.95rem; color:var(--text-main);">${item.product_name}</div>
                            <div style="font-size:0.82rem; color:var(--text-muted);">Qty: ${item.quantity} × ₹${Number(item.price).toLocaleString('en-IN')}</div>
                          </div>
                        </div>
                        <div style="font-weight:800; font-size:1.05rem; color:var(--text-main);">
                          ₹${Number(item.item_total).toLocaleString('en-IN')}
                        </div>
                      </div>
                    `).join('')}
                  </div>
                </div>

                <!-- Shipping Details & Subtotals -->
                <div style="margin-top:1.5rem; padding:1.25rem; background:var(--bg-subtle); border-radius:var(--radius-lg); font-size:0.88rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:1.25rem;">
                  <div>
                    <strong style="color:var(--text-main);"><i class="fas fa-map-marker-alt" style="color:var(--primary);"></i> Shipping Destination:</strong>
                    <div style="color:var(--text-body); margin-top:0.25rem;"><strong>${order.shipping_name}</strong> (${order.phone})</div>
                    <div style="color:var(--text-muted);">${order.shipping_address}</div>
                  </div>
                  <div style="text-align:right;">
                    <div>Subtotal: ₹${Number(order.subtotal).toLocaleString('en-IN')} | Tax: ₹${Number(order.tax).toLocaleString('en-IN')} | Shipping: ₹${Number(order.shipping).toLocaleString('en-IN')}</div>
                    <div style="font-weight:800; margin-top:0.3rem; color:var(--primary);">Paid Total: ₹${Number(order.total_amount).toLocaleString('en-IN')}</div>
                  </div>
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    } catch (err) {
      container.innerHTML = `<p class="text-danger" style="text-align:center; padding:3rem;">Failed to load orders: ${err.message}</p>`;
    }
  }
};
