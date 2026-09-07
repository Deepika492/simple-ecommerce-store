/**
 * AURASTORE - ADMINISTRATOR DASHBOARD & MANAGEMENT
 */

const Admin = {
  categories: [],

  async initDashboard() {
    if (!Auth.requireAdmin('login.html')) return;

    await this.loadStats();
    await this.loadCategories();
    await this.loadProducts();
    await this.loadOrders();
    this.setupModals();
  },

  // 1. Dashboard Statistics
  async loadStats() {
    try {
      const res = await ApiClient.get('/admin/stats/');
      if (res.success && res.data) {
        const s = res.data;
        document.getElementById('stat-revenue').textContent = '₹' + Number(s.total_revenue).toLocaleString('en-IN');
        document.getElementById('stat-orders').textContent = s.total_orders;
        document.getElementById('stat-products').textContent = s.total_products;
        document.getElementById('stat-low-stock').textContent = (s.low_stock_products + s.out_of_stock_products);
      }
    } catch (err) {
      console.error("Failed to load stats", err);
    }
  },

  // 2. Load Categories
  async loadCategories() {
    try {
      const res = await ApiClient.get('/categories/');
      if (res.success && res.data) {
        this.categories = res.data;
        const select = document.getElementById('prod_category');
        if (select) {
          select.innerHTML = `
            <option value="">Select Category</option>
            ${this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
          `;
        }
      }
    } catch (e) {
      console.error("Categories error", e);
    }
  },

  // 3. Load Products Table
  async loadProducts() {
    const tbody = document.getElementById('admin-products-tbody');
    if (!tbody) return;

    try {
      const res = await ApiClient.get('/products/');
      if (res.success && res.data) {
        const products = res.data;

        if (products.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:3rem; color:var(--text-muted);">No products currently in inventory.</td></tr>`;
          return;
        }

        tbody.innerHTML = products.map(p => {
          let stockClass = 'badge-stock-in';
          if (p.stock === 0) stockClass = 'badge-stock-out';
          else if (p.stock <= 5) stockClass = 'badge-stock-low';

          return `
            <tr>
              <td><span style="font-weight:700; color:var(--text-light);">#${p.id}</span></td>
              <td>
                <div style="display:flex; align-items:center; gap:0.85rem;">
                  <img src="${p.image_url}" style="width:48px; height:48px; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border-color);" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
                  <div>
                    <strong style="color:var(--text-main); font-size:0.95rem;">${p.name}</strong>
                    <div style="font-size:0.8rem; color:var(--text-muted);">${p.category_name || 'No Category'}</div>
                  </div>
                </div>
              </td>
              <td><strong style="font-family:var(--font-heading); font-size:1.05rem;">₹${Number(p.price).toLocaleString('en-IN')}</strong></td>
              <td>
                <div style="display:flex; align-items:center; gap:0.5rem;">
                  <input 
                    type="number" 
                    value="${p.stock}" 
                    min="0" 
                    style="width:70px; padding:5px 8px; border:1px solid var(--border-color); border-radius:var(--radius-sm); font-weight:700; text-align:center;" 
                    id="stock-input-${p.id}"
                  >
                  <button onclick="Admin.updateStock(${p.id})" class="btn btn-sm btn-secondary" title="Save Stock">
                    <i class="fas fa-save"></i>
                  </button>
                </div>
              </td>
              <td><span class="badge ${stockClass}">${p.availability_status}</span></td>
              <td>${p.is_featured ? '<span style="color:var(--warning); font-weight:700;"><i class="fas fa-star"></i> Featured</span>' : '<span style="color:var(--text-light);">Standard</span>'}</td>
              <td>
                <div style="display:flex; gap:0.4rem;">
                  <button onclick="Admin.openEditProductModal(${JSON.stringify(p).replace(/"/g, '&quot;')})" class="btn btn-sm btn-secondary" title="Edit Product">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button onclick="Admin.deleteProduct(${p.id}, '${p.name.replace(/'/g, "\\'")}')" class="btn btn-sm btn-secondary" style="color:var(--danger);" title="Delete Product">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          `;
        }).join('');
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-danger" style="text-align:center; padding:2rem;">Failed to load products: ${err.message}</td></tr>`;
    }
  },

  // Quick Stock Update
  async updateStock(productId) {
    const input = document.getElementById(`stock-input-${productId}`);
    if (!input) return;
    const stockVal = parseInt(input.value);

    try {
      const res = await ApiClient.put(`/products/${productId}/`, { stock: stockVal });
      if (res.success) {
        showToast('Stock quantity updated successfully.', 'success');
        this.loadProducts();
        this.loadStats();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // 4. Load Customer Orders Table
  async loadOrders() {
    const tbody = document.getElementById('admin-orders-tbody');
    if (!tbody) return;

    try {
      const res = await ApiClient.get('/admin/orders/');
      if (res.success && res.data) {
        const orders = res.data;

        if (orders.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:3rem; color:var(--text-muted);">No customer orders placed yet.</td></tr>`;
          return;
        }

        tbody.innerHTML = orders.map(o => {
          const dateStr = new Date(o.created_at).toLocaleDateString('en-IN', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
          });

          return `
            <tr>
              <td><strong style="color:var(--primary);">#${o.id}</strong></td>
              <td>
                <div><strong style="color:var(--text-main);">${o.shipping_name || o.user_details.username}</strong></div>
                <div style="font-size:0.78rem; color:var(--text-muted);"><i class="fas fa-phone fa-xs"></i> ${o.phone}</div>
              </td>
              <td style="font-size:0.88rem; color:var(--text-muted);">${dateStr}</td>
              <td><span class="badge" style="background:var(--bg-subtle); color:var(--text-main);">${o.total_items} item${o.total_items > 1 ? 's' : ''}</span></td>
              <td><strong style="font-family:var(--font-heading); font-size:1.05rem;">₹${Number(o.total_amount).toLocaleString('en-IN')}</strong></td>
              <td>
                <select 
                  onchange="Admin.updateOrderStatus(${o.id}, this.value)" 
                  class="form-control" 
                  style="font-size:0.82rem; padding:4px 10px; width:auto; font-weight:800; border-radius:var(--radius-sm);"
                >
                  <option value="PLACED" ${o.status === 'PLACED' ? 'selected' : ''}>PLACED</option>
                  <option value="CONFIRMED" ${o.status === 'CONFIRMED' ? 'selected' : ''}>CONFIRMED</option>
                  <option value="PROCESSING" ${o.status === 'PROCESSING' ? 'selected' : ''}>PROCESSING</option>
                  <option value="SHIPPED" ${o.status === 'SHIPPED' ? 'selected' : ''}>SHIPPED</option>
                  <option value="DELIVERED" ${o.status === 'DELIVERED' ? 'selected' : ''}>DELIVERED</option>
                  <option value="CANCELLED" ${o.status === 'CANCELLED' ? 'selected' : ''}>CANCELLED</option>
                </select>
              </td>
              <td>
                <button onclick="Admin.viewOrderDetails(${JSON.stringify(o).replace(/"/g, '&quot;')})" class="btn btn-sm btn-secondary">
                  <i class="fas fa-eye"></i> Details
                </button>
              </td>
            </tr>
          `;
        }).join('');
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-danger" style="text-align:center; padding:2rem;">Failed to load orders: ${err.message}</td></tr>`;
    }
  },

  // Update Order Status
  async updateOrderStatus(orderId, newStatus) {
    try {
      const res = await ApiClient.put(`/admin/orders/${orderId}/status/`, { status: newStatus });
      if (res.success) {
        showToast(res.message || `Order #${orderId} status updated to ${newStatus}`, 'success');
        this.loadStats();
      }
    } catch (err) {
      showToast(err.message, 'error');
      this.loadOrders();
    }
  },

  // 5. Modals & Product CRUD
  setupModals() {
    const form = document.getElementById('product-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prodId = document.getElementById('prod_id').value;
        const payload = {
          name: document.getElementById('prod_name').value.trim(),
          category: document.getElementById('prod_category').value || null,
          price: parseFloat(document.getElementById('prod_price').value),
          stock: parseInt(document.getElementById('prod_stock').value),
          image_url: document.getElementById('prod_image').value.trim() || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800',
          description: document.getElementById('prod_desc').value.trim(),
          is_featured: document.getElementById('prod_featured').checked
        };

        try {
          let res;
          if (prodId) {
            res = await ApiClient.put(`/products/${prodId}/`, payload);
          } else {
            res = await ApiClient.post('/products/', payload);
          }

          if (res.success) {
            showToast(res.message || 'Product saved successfully!', 'success');
            this.closeModal('product-modal');
            this.loadProducts();
            this.loadStats();
          }
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    // Category modal form
    const catForm = document.getElementById('category-form');
    if (catForm) {
      catForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          name: document.getElementById('cat_name').value.trim(),
          description: document.getElementById('cat_desc').value.trim(),
          icon: document.getElementById('cat_icon').value.trim() || 'fas fa-box'
        };

        try {
          const res = await ApiClient.post('/categories/', payload);
          if (res.success) {
            showToast('Category created successfully!', 'success');
            this.closeModal('category-modal');
            this.loadCategories();
          }
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }
  },

  openAddProductModal() {
    document.getElementById('product-form').reset();
    document.getElementById('prod_id').value = '';
    document.getElementById('product-modal-title').textContent = 'Add New Product';
    this.openModal('product-modal');
  },

  openEditProductModal(p) {
    document.getElementById('prod_id').value = p.id;
    document.getElementById('prod_name').value = p.name;
    document.getElementById('prod_category').value = p.category || '';
    document.getElementById('prod_price').value = p.price;
    document.getElementById('prod_stock').value = p.stock;
    document.getElementById('prod_image').value = p.image_url;
    document.getElementById('prod_desc').value = p.description || '';
    document.getElementById('prod_featured').checked = !!p.is_featured;
    document.getElementById('product-modal-title').textContent = `Edit Product #${p.id}`;
    this.openModal('product-modal');
  },

  async deleteProduct(productId, name) {
    if (!confirm(`Are you sure you want to delete '${name}'? This action cannot be undone.`)) return;

    try {
      const res = await ApiClient.delete(`/products/${productId}/`);
      if (res.success) {
        showToast('Product deleted from inventory.', 'info');
        this.loadProducts();
        this.loadStats();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  viewOrderDetails(order) {
    const modal = document.getElementById('order-detail-modal');
    if (!modal) return;

    document.getElementById('modal-order-id').textContent = `#${order.id}`;
    document.getElementById('modal-order-customer').textContent = `${order.shipping_name || order.user_details.username} (${order.user_details.email || 'No email'})`;
    document.getElementById('modal-order-address').textContent = `${order.shipping_address} | Phone: ${order.phone}`;
    document.getElementById('modal-order-total').textContent = '₹' + Number(order.total_amount).toLocaleString('en-IN');
    
    const itemsList = document.getElementById('modal-order-items');
    itemsList.innerHTML = order.items.map(item => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:0.75rem 0; border-bottom:1px solid var(--border-color);">
        <div style="display:flex; align-items:center; gap:0.75rem;">
          <img src="${item.product_image}" style="width:44px; height:44px; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border-color);" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
          <div>
            <strong style="color:var(--text-main); font-size:0.92rem;">${item.product_name}</strong>
            <div style="font-size:0.8rem; color:var(--text-muted);">Qty: ${item.quantity} × ₹${Number(item.price).toLocaleString('en-IN')}</div>
          </div>
        </div>
        <strong style="font-size:0.95rem; color:var(--text-main);">₹${Number(item.item_total).toLocaleString('en-IN')}</strong>
      </div>
    `).join('');

    this.openModal('order-detail-modal');
  },

  openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('open');
  },

  closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('open');
  }
};
