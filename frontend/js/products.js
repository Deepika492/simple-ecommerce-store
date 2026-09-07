/**
 * AURASTORE - PRODUCTS & CATALOG MANAGER
 */

const Products = {
  // Wishlist toggle helper using localStorage
  toggleWishlist(productId, btnElement) {
    let wishlist = [];
    try {
      wishlist = JSON.parse(localStorage.getItem('user_wishlist') || '[]');
    } catch(e) { wishlist = []; }

    const idx = wishlist.indexOf(productId);
    if (idx > -1) {
      wishlist.splice(idx, 1);
      btnElement.classList.remove('active');
      showToast('Removed from your wishlist.', 'info');
    } else {
      wishlist.push(productId);
      btnElement.classList.add('active');
      showToast('Added to your wishlist!', 'success');
    }
    localStorage.setItem('user_wishlist', JSON.stringify(wishlist));
  },

  isWishlisted(productId) {
    try {
      const wishlist = JSON.parse(localStorage.getItem('user_wishlist') || '[]');
      return wishlist.includes(productId);
    } catch(e) { return false; }
  },

  // Generate modern product card HTML
  renderProductCard(product) {
    let stockBadge = '';
    const isOutOfStock = product.stock <= 0;

    if (isOutOfStock) {
      stockBadge = `<span class="badge badge-stock-out"><i class="fas fa-times-circle"></i> Out of Stock</span>`;
    } else if (product.stock <= 5) {
      stockBadge = `<span class="badge badge-stock-low"><i class="fas fa-bolt"></i> Only ${product.stock} Left</span>`;
    } else {
      stockBadge = `<span class="badge badge-stock-in"><i class="fas fa-check-circle"></i> In Stock</span>`;
    }

    const featuredBadge = product.is_featured 
      ? `<span class="badge badge-featured"><i class="fas fa-sparkles"></i> Featured</span>` 
      : '';

    const wishlisted = this.isWishlisted(product.id);
    const ratingScore = (4.5 + ((product.id * 3) % 5) * 0.1).toFixed(1);
    const reviewCount = (24 + (product.id * 17) % 80);

    return `
      <div class="product-card" data-id="${product.id}">
        <div class="product-img-wrapper">
          <div class="product-badge-group">
            ${featuredBadge}
            ${stockBadge}
          </div>
          <button 
            type="button" 
            class="product-wishlist-btn ${wishlisted ? 'active' : ''}" 
            title="Add to Wishlist"
            onclick="Products.toggleWishlist(${product.id}, this)"
          >
            <i class="fas fa-heart"></i>
          </button>
          <a href="product-details.html?id=${product.id}">
            <img src="${product.image_url}" alt="${product.name}" class="product-img" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
          </a>
        </div>
        <div class="product-body">
          <div class="product-category">${product.category_name || 'Electronics'}</div>
          <h3 class="product-title">
            <a href="product-details.html?id=${product.id}" title="${product.name}">${product.name}</a>
          </h3>
          <div class="product-rating">
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="fas fa-star"></i>
            <i class="fas fa-star-half-alt"></i>
            <span style="font-weight:700; color:var(--text-main); margin-left:2px;">${ratingScore}</span>
            <span class="rating-count">(${reviewCount})</span>
          </div>
          <p class="product-desc-snippet">${product.description || ''}</p>
          <div class="product-footer">
            <div class="product-price">
              <span class="currency">₹</span>${Number(product.price).toLocaleString('en-IN')}
            </div>
            <div class="product-card-actions">
              <a href="product-details.html?id=${product.id}" class="btn btn-sm btn-secondary" title="Quick View">
                <i class="fas fa-eye"></i>
              </a>
              <button 
                onclick="CartManager.addItem(${product.id}, 1)" 
                class="btn btn-sm btn-primary" 
                ${isOutOfStock ? 'disabled title="Out of Stock"' : 'title="Add to Cart"'}
              >
                <i class="fas fa-shopping-bag"></i> Add
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  // Load Homepage Featured Products & Categories
  async initHomePage() {
    const featuredContainer = document.getElementById('featured-products-grid');
    const categoriesContainer = document.getElementById('home-categories-grid');

    if (categoriesContainer) {
      try {
        const res = await ApiClient.get('/categories/');
        if (res.success && res.data) {
          categoriesContainer.innerHTML = res.data.map(cat => `
            <a href="products.html?category=${cat.id}" class="category-card">
              <div class="cat-icon"><i class="${cat.icon || 'fas fa-box'}"></i></div>
              <div class="cat-name">${cat.name}</div>
              <span class="cat-count">${cat.product_count} Products</span>
            </a>
          `).join('');
        }
      } catch (err) {
        categoriesContainer.innerHTML = `<p class="text-muted" style="grid-column:1/-1; text-align:center;">Could not load categories.</p>`;
      }
    }

    if (featuredContainer) {
      try {
        const res = await ApiClient.get('/products/', { featured: 'true' });
        if (res.success && res.data) {
          if (res.data.length === 0) {
            featuredContainer.innerHTML = `<p class="text-muted" style="grid-column:1/-1; text-align:center;">No featured products available.</p>`;
          } else {
            featuredContainer.innerHTML = res.data.map(p => this.renderProductCard(p)).join('');
          }
        }
      } catch (err) {
        featuredContainer.innerHTML = `<p class="text-muted" style="grid-column:1/-1; text-align:center;">Could not load featured products.</p>`;
      }
    }
  },

  // Load Full Catalog Page with live filters
  async initCatalogPage() {
    const productGrid = document.getElementById('catalog-products-grid');
    const categoryList = document.getElementById('filter-category-list');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceDisplay = document.getElementById('price-display');
    const inStockCheckbox = document.getElementById('in-stock-only');
    const resultCount = document.getElementById('result-count');

    // Parse URL params
    const urlParams = new URLSearchParams(window.location.search);
    let currentCategory = urlParams.get('category') || '';
    let currentSearch = urlParams.get('search') || '';

    if (searchInput && currentSearch) {
      searchInput.value = currentSearch;
    }

    // Load categories for filter
    if (categoryList) {
      try {
        const catRes = await ApiClient.get('/categories/');
        if (catRes.success && catRes.data) {
          categoryList.innerHTML = `
            <li class="filter-item ${!currentCategory ? 'active' : ''}" data-category="">
              <span><i class="fas fa-th-large" style="margin-right:6px; font-size:0.85rem;"></i> All Categories</span>
              <span class="cat-count">All</span>
            </li>
            ${catRes.data.map(c => `
              <li class="filter-item ${currentCategory == c.id ? 'active' : ''}" data-category="${c.id}">
                <span><i class="${c.icon || 'fas fa-box'}" style="margin-right:6px; font-size:0.85rem;"></i> ${c.name}</span>
                <span class="cat-count">${c.product_count}</span>
              </li>
            `).join('')}
          `;

          categoryList.querySelectorAll('.filter-item').forEach(item => {
            item.addEventListener('click', () => {
              categoryList.querySelectorAll('.filter-item').forEach(i => i.classList.remove('active'));
              item.classList.add('active');
              currentCategory = item.dataset.category;
              fetchFilteredProducts();
            });
          });
        }
      } catch (e) {
        console.error("Error loading categories", e);
      }
    }

    const fetchFilteredProducts = async () => {
      if (!productGrid) return;
      productGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding: 4rem;">
          <i class="fas fa-spinner fa-spin fa-2x" style="color:var(--primary)"></i>
          <p style="margin-top:1rem; color:var(--text-muted); font-weight:600;">Searching products...</p>
        </div>
      `;

      const params = {};
      if (currentSearch) params.search = currentSearch;
      if (currentCategory) params.category = currentCategory;
      if (minPriceInput && minPriceInput.value) params.min_price = minPriceInput.value;
      if (maxPriceInput && maxPriceInput.value) params.max_price = maxPriceInput.value;
      if (inStockCheckbox && inStockCheckbox.checked) params.in_stock = 'true';
      if (sortSelect) params.sort = sortSelect.value;

      try {
        const res = await ApiClient.get('/products/', params);
        if (res.success && res.data) {
          if (resultCount) {
            resultCount.textContent = `Showing ${res.data.length} product${res.data.length === 1 ? '' : 's'}`;
          }

          if (res.data.length === 0) {
            productGrid.innerHTML = `
              <div style="grid-column: 1/-1; text-align:center; padding: 4.5rem 2rem; background:white; border-radius:var(--radius-xl); border:1px dashed var(--border-color); box-shadow:var(--shadow-sm);">
                <div style="width:70px; height:70px; border-radius:var(--radius-full); background:var(--bg-subtle); display:grid; place-items:center; margin:0 auto 1.25rem;">
                  <i class="fas fa-box-open fa-2x" style="color:var(--text-light);"></i>
                </div>
                <h3 style="font-size:1.35rem; font-weight:800;">No products match your criteria</h3>
                <p style="color:var(--text-muted); margin-top:0.4rem; max-width:400px; margin-left:auto; margin-right:auto;">Try adjusting your search query, increasing your price limit, or clearing filters.</p>
                <button onclick="window.location.href='products.html'" class="btn btn-primary" style="margin-top:1.5rem;">
                  <i class="fas fa-rotate-left"></i> Reset All Filters
                </button>
              </div>
            `;
          } else {
            productGrid.innerHTML = res.data.map(p => this.renderProductCard(p)).join('');
          }
        }
      } catch (err) {
        productGrid.innerHTML = `<p class="text-danger" style="grid-column:1/-1; text-align:center;">Failed to load products: ${err.message}</p>`;
      }
    };

    // Event listeners
    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          currentSearch = e.target.value.trim();
          fetchFilteredProducts();
        }, 300);
      });
    }

    if (sortSelect) {
      sortSelect.addEventListener('change', fetchFilteredProducts);
    }

    if (inStockCheckbox) {
      inStockCheckbox.addEventListener('change', fetchFilteredProducts);
    }

    if (maxPriceInput) {
      maxPriceInput.addEventListener('input', (e) => {
        if (priceDisplay) priceDisplay.textContent = `Up to ₹${Number(e.target.value).toLocaleString('en-IN')}`;
      });
      maxPriceInput.addEventListener('change', fetchFilteredProducts);
    }

    // Initial load
    fetchFilteredProducts();
  },

  // Load Single Product Details
  async initDetailsPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    const container = document.getElementById('product-details-container');
    const breadcrumbTitle = document.getElementById('breadcrumb-title');

    if (!productId || !container) {
      if (container) container.innerHTML = `<p class="text-danger" style="text-align:center; padding:3rem;">Product ID is missing in the URL.</p>`;
      return;
    }

    try {
      const res = await ApiClient.get(`/products/${productId}/`);
      if (res.success && res.data) {
        const product = res.data;
        document.title = `${product.name} | AuraStore`;
        if (breadcrumbTitle) breadcrumbTitle.textContent = product.name;

        let stockStatusHtml = '';
        const isOutOfStock = product.stock <= 0;

        if (isOutOfStock) {
          stockStatusHtml = `<span class="badge badge-stock-out" style="font-size:0.85rem;"><i class="fas fa-times-circle"></i> Out of Stock</span>`;
        } else if (product.stock <= 5) {
          stockStatusHtml = `<span class="badge badge-stock-low" style="font-size:0.85rem;"><i class="fas fa-bolt"></i> Low Stock - Only ${product.stock} items left!</span>`;
        } else {
          stockStatusHtml = `<span class="badge badge-stock-in" style="font-size:0.85rem;"><i class="fas fa-check-circle"></i> In Stock (${product.stock} units available)</span>`;
        }

        container.innerHTML = `
          <div class="product-detail-card">
            <div class="product-detail-grid">
              <div class="product-detail-gallery">
                <img src="${product.image_url}" alt="${product.name}" class="gallery-main-img" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'">
              </div>
              <div class="product-detail-info">
                <div class="product-detail-category">${product.category_name || 'Electronics'}</div>
                <h1 class="product-detail-title">${product.name}</h1>
                
                <div class="product-rating" style="font-size:0.95rem; margin:0;">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star-half-alt"></i>
                  <span style="font-weight:700; color:var(--text-main); margin-left:4px;">4.8</span>
                  <span class="rating-count" style="font-size:0.85rem;">(128 verified customer ratings)</span>
                </div>

                <div class="product-detail-price">
                  <span class="currency" style="font-size:1.6rem; color:var(--text-muted)">₹</span>${Number(product.price).toLocaleString('en-IN')}
                </div>

                <div>
                  ${stockStatusHtml}
                </div>

                <div class="product-detail-desc">
                  ${product.description || 'Experience premium performance, contemporary aesthetics, and durable quality with this essential.'}
                </div>

                <div style="display:flex; align-items:center; gap:1.5rem; margin-top:1.5rem; flex-wrap:wrap;">
                  <div>
                    <label class="form-label">Quantity</label>
                    <div class="quantity-stepper">
                      <button type="button" onclick="Products.changeDetailQty(-1)" ${isOutOfStock ? 'disabled' : ''}>-</button>
                      <input type="number" id="detail-qty-input" value="1" min="1" max="${product.stock}" readonly>
                      <button type="button" onclick="Products.changeDetailQty(1, ${product.stock})" ${isOutOfStock ? 'disabled' : ''}>+</button>
                    </div>
                  </div>

                  <div style="flex:1; min-width:220px; padding-top:1.4rem; display:flex; gap:0.75rem; flex-wrap:wrap;">
                    <button 
                      onclick="Products.addDetailToCart(${product.id})" 
                      class="btn btn-lg btn-primary"
                      style="flex:1;"
                      ${isOutOfStock ? 'disabled' : ''}
                    >
                      <i class="fas fa-shopping-bag"></i> ${isOutOfStock ? 'Out of Stock' : 'Add to Cart'}
                    </button>
                    <button 
                      onclick="Products.buyNow(${product.id})" 
                      class="btn btn-lg btn-success"
                      style="flex:1;"
                      ${isOutOfStock ? 'disabled' : ''}
                    >
                      <i class="fas fa-bolt"></i> Buy Now
                    </button>
                  </div>
                </div>

                <div style="margin-top:2.5rem; padding-top:1.75rem; border-top:1px solid var(--border-color); display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:1.25rem;">
                  <div style="display:flex; align-items:center; gap:0.85rem;">
                    <div style="width:42px; height:42px; border-radius:var(--radius-md); background:var(--primary-light); color:var(--primary); display:grid; place-items:center; font-size:1.2rem;">
                      <i class="fas fa-truck-fast"></i>
                    </div>
                    <div style="font-size:0.85rem;">
                      <strong>Free Delivery</strong>
                      <div style="color:var(--text-muted)">On all orders over ₹1,000</div>
                    </div>
                  </div>
                  <div style="display:flex; align-items:center; gap:0.85rem;">
                    <div style="width:42px; height:42px; border-radius:var(--radius-md); background:var(--success-light); color:var(--success-dark); display:grid; place-items:center; font-size:1.2rem;">
                      <i class="fas fa-shield-halved"></i>
                    </div>
                    <div style="font-size:0.85rem;">
                      <strong>100% Authentic</strong>
                      <div style="color:var(--text-muted)">Direct from brand makers</div>
                    </div>
                  </div>
                  <div style="display:flex; align-items:center; gap:0.85rem;">
                    <div style="width:42px; height:42px; border-radius:var(--radius-md); background:var(--secondary-light); color:var(--secondary); display:grid; place-items:center; font-size:1.2rem;">
                      <i class="fas fa-rotate-left"></i>
                    </div>
                    <div style="font-size:0.85rem;">
                      <strong>30-Day Returns</strong>
                      <div style="color:var(--text-muted)">Hassle-free guarantee</div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        `;
      }
    } catch (err) {
      container.innerHTML = `<p class="text-danger" style="text-align:center; padding:3rem;">Failed to load product details: ${err.message}</p>`;
    }
  },

  changeDetailQty(delta, maxStock = 999) {
    const input = document.getElementById('detail-qty-input');
    if (!input) return;
    let val = parseInt(input.value) + delta;
    if (val < 1) val = 1;
    if (val > maxStock) {
      val = maxStock;
      showToast(`Only ${maxStock} items available in stock.`, 'warning');
    }
    input.value = val;
  },

  async addDetailToCart(productId) {
    const input = document.getElementById('detail-qty-input');
    const qty = input ? parseInt(input.value) : 1;
    await CartManager.addItem(productId, qty);
  },

  async buyNow(productId) {
    const input = document.getElementById('detail-qty-input');
    const qty = input ? parseInt(input.value) : 1;
    await CartManager.addItem(productId, qty);
    setTimeout(() => {
      window.location.href = 'checkout.html';
    }, 400);
  }
};
