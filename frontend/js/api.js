/**
 * AURASTORE - CENTRAL API CLIENT & UTILITIES
 */

const API_BASE_URL = (window.location.port === '8000' || window.location.origin.includes('127.0.0.1:8000') || window.location.origin.includes('localhost:8000'))
  ? `${window.location.origin}/api`
  : 'http://127.0.0.1:8000/api';

class ApiClient {
  static getToken() {
    return localStorage.getItem('auth_token');
  }

  static setAuth(token, user) {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }

  static clearAuth() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }

  static getUser() {
    const raw = localStorage.getItem('auth_user');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  static async request(endpoint, options = {}) {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}/${cleanEndpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        let errorMsg = data.message || `Request failed with status ${response.status}`;
        if (data.errors) {
          if (typeof data.errors === 'string') {
            errorMsg = data.errors;
          } else if (typeof data.errors === 'object') {
            const firstKey = Object.keys(data.errors)[0];
            const val = data.errors[firstKey];
            errorMsg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`;
          }
        }
        const err = new Error(errorMsg);
        err.data = data;
        err.status = response.status;
        throw err;
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  static get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = query ? `${endpoint}?${query}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  static post(endpoint, body = {}) {
    return this.request(endpoint, { method: 'POST', body });
  }

  static put(endpoint, body = {}) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  static delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Toast Notification Manager
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'fa-info-circle';
  if (type === 'success') icon = 'fa-check-circle';
  if (type === 'error') icon = 'fa-exclamation-circle';
  if (type === 'warning') icon = 'fa-exclamation-triangle';

  toast.innerHTML = `
    <i class="fas ${icon}" style="font-size:1.15rem;"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Format Currency Utility
function formatCurrency(amount) {
  return '₹' + Number(amount || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}
