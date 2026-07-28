/**
 * Returns a stable session ID for this browser tab.
 * Persisted in localStorage so it survives page refreshes.
 * Each new tab/browser gets its own ID → per-user isolation.
 */
export function getSessionId() {
  let id = localStorage.getItem('lexguard_session_id');
  if (!id) {
    id = 'sess_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 9);
    localStorage.setItem('lexguard_session_id', id);
  }
  return id;
}