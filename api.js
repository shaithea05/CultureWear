// api.js
/* global fetch, localStorage, window */
(function () {
  const DEFAULT_BASE = 'http://127.0.0.1:8000';

  function getBase() {
    // Allow override via window.API_BASE or localStorage('API_BASE')
    return window.API_BASE || localStorage.getItem('API_BASE') || DEFAULT_BASE;
  }

  async function api(path, { method = 'GET', body, headers } = {}) {
    const res = await fetch(`${getBase()}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', ...(headers || {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      let txt = '';
      try { txt = await res.text(); } catch {}
      throw new Error(`API ${method} ${path} failed: ${res.status} ${txt}`);
    }
    return res.json();
  }

  // Simple helpers for auth/session (stored in localStorage)
  function saveCurrentUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
  }
  function getCurrentUser() {
    try { return JSON.parse(localStorage.getItem('currentUser') || '{}'); }
    catch { return {}; }
  }
  function requireUserEmail() {
    const u = getCurrentUser();
    if (!u.email) throw new Error('No user email in session. Please Sign In.');
    return u.email;
  }

  // Expose to global scope for non-module pages
  window.api = api;
  window.saveCurrentUser = saveCurrentUser;
  window.getCurrentUser = getCurrentUser;
  window.requireUserEmail = requireUserEmail;
})();