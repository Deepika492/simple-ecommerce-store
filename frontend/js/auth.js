/**
 * AURASTORE - AUTHENTICATION & USER SESSION MANAGER
 */

const Auth = {
  isLoggedIn() {
    return !!ApiClient.getToken();
  },

  getCurrentUser() {
    return ApiClient.getUser();
  },

  isAdmin() {
    const user = this.getCurrentUser();
    return !!(user && (user.is_staff || user.is_superuser));
  },

  async login(username, password) {
    try {
      const res = await ApiClient.post('/login/', { username, password });
      if (res.success && res.data) {
        ApiClient.setAuth(res.data.token, res.data.user);
        showToast(`Welcome back, ${res.data.user.username}!`, 'success');
        return res.data;
      }
      throw new Error(res.message || 'Login failed');
    } catch (err) {
      showToast(err.message, 'error');
      throw err;
    }
  },

  async register(username, email, password, confirmPassword) {
    try {
      const res = await ApiClient.post('/register/', {
        username,
        email,
        password,
        confirm_password: confirmPassword
      });
      if (res.success && res.data) {
        ApiClient.setAuth(res.data.token, res.data.user);
        showToast('Registration successful! Welcome to AuraStore.', 'success');
        return res.data;
      }
      throw new Error(res.message || 'Registration failed');
    } catch (err) {
      showToast(err.message, 'error');
      throw err;
    }
  },

  async logout() {
    try {
      if (this.isLoggedIn()) {
        await ApiClient.post('/logout/').catch(() => {});
      }
    } finally {
      ApiClient.clearAuth();
      showToast('Logged out successfully.', 'info');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 400);
    }
  },

  // Navbar dynamic updater (Desktop & Mobile)
  updateNavbar() {
    const authContainer = document.getElementById('nav-auth-container');
    const mobileAuthContainer = document.getElementById('mobile-auth-container');

    const renderAuth = (isMobile = false) => {
      if (this.isLoggedIn()) {
        const user = this.getCurrentUser();
        const adminLink = this.isAdmin() 
          ? `<a href="admin.html" class="btn btn-sm btn-primary" style="font-weight:700;"><i class="fas fa-crown"></i> Admin</a>` 
          : '';

        return `
          <div class="user-menu" style="${isMobile ? 'flex-direction:column; align-items:stretch;' : ''}">
            ${adminLink}
            <div class="user-chip">
              <i class="fas fa-user-circle"></i>
              <span>${user.username}</span>
              ${user.is_staff ? '<span class="role-tag">Admin</span>' : ''}
            </div>
            <button onclick="Auth.logout()" class="btn btn-sm btn-secondary" title="Logout">
              <i class="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        `;
      } else {
        return `
          <div style="display:flex; gap:0.5rem; ${isMobile ? 'flex-direction:column;' : ''}">
            <a href="login.html" class="btn btn-sm btn-secondary">
              <i class="fas fa-sign-in-alt"></i> Login
            </a>
            <a href="register.html" class="btn btn-sm btn-primary">
              <i class="fas fa-user-plus"></i> Register
            </a>
          </div>
        `;
      }
    };

    if (authContainer) authContainer.innerHTML = renderAuth(false);
    if (mobileAuthContainer) mobileAuthContainer.innerHTML = renderAuth(true);
  },

  // Require auth guard
  requireAuth(redirectTo = 'login.html') {
    if (!this.isLoggedIn()) {
      showToast('Please sign in to proceed.', 'warning');
      setTimeout(() => {
        window.location.href = `${redirectTo}?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
      }, 500);
      return false;
    }
    return true;
  },

  // Require admin guard
  requireAdmin(redirectTo = 'index.html') {
    if (!this.isLoggedIn()) {
      window.location.href = `login.html?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`;
      return false;
    }
    if (!this.isAdmin()) {
      showToast('Access denied. Administrator privileges required.', 'error');
      setTimeout(() => {
        window.location.href = redirectTo;
      }, 800);
      return false;
    }
    return true;
  }
};

// Mobile drawer toggle helper
function toggleMobileNav() {
  const drawer = document.getElementById('mobile-nav-drawer');
  if (drawer) {
    drawer.classList.toggle('open');
  }
}

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  Auth.updateNavbar();
  if (typeof updateCartCount === 'function') {
    updateCartCount();
  }
});
