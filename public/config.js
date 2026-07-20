/**
 * Leadex API Configuration
 * Automatically detects the correct API base URL
 */

// Detect if we're running on localhost or a remote server
const hostname = window.location.hostname;
const protocol = window.location.protocol;
const port = window.location.port || (protocol === 'https:' ? '443' : '80');

// Determine API base URL
let API_BASE;

if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Local development
    API_BASE = `http://127.0.0.1:8000/api/admin`;
} else {
    // Production server - use same host and port
    const apiPort = port === '80' || port === '443' ? '' : `:${port}`;
    API_BASE = `${protocol}//${hostname}${apiPort}/api/admin`;
}

// Export for use in other scripts
window.LEADEX_CONFIG = {
    API_BASE: API_BASE,
    API_ROOT: API_BASE.replace('/api/admin', ''),
    API_CLIENT: API_BASE.replace('/admin', '/client'),
    API_LANDING: API_BASE.replace('/admin', '/landing')
};

console.log('Leadex Config:', window.LEADEX_CONFIG);
