/**
 * Leadex Admin Navigation
 * Unified sidebar navigation for all admin pages
 */

// Navigation configuration
const ADMIN_NAV = {
    pages: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊', url: '/admin-dashboard.html' },
        { id: 'leads', label: 'Lead Management', icon: '📋', url: '/admin-leads.html' },
        { id: 'clients', label: 'Client Management', icon: '👥', url: '/admin-clients.html' },
        { id: 'analytics', label: 'Analytics', icon: '📈', url: '/admin-analytics.html' },
        { id: 'reports', label: 'Reports & Export', icon: '📄', url: '/admin-reports.html' },
        { id: 'webhooks', label: 'Webhooks', icon: '🔗', url: '/admin-webhooks.html' },
        { id: 'imports', label: 'Bulk Imports', icon: '📥', url: '/admin-imports.html' },
        { id: 'notifications', label: 'Notifications', icon: '🔔', url: '/admin-notifications.html' },
        { id: 'advanced', label: 'Advanced', icon: '⚙️', url: '/admin-advanced.html' }
    ]
};

// Inject navigation styles
function injectNavStyles() {
    const styles = `
        <style id="admin-nav-styles">
            body {
                margin: 0;
                display: flex;
                min-height: 100vh;
                background: #f5f7fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            .admin-sidebar {
                width: 260px;
                background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                flex-direction: column;
                position: fixed;
                height: 100vh;
                left: 0;
                top: 0;
                z-index: 1000;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            }

            .sidebar-header {
                padding: 25px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }

            .sidebar-logo {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .sidebar-subtitle {
                font-size: 12px;
                opacity: 0.8;
            }

            .sidebar-nav {
                flex: 1;
                overflow-y: auto;
                padding: 10px 0;
            }

            .nav-item {
                display: flex;
                align-items: center;
                padding: 12px 20px;
                color: white;
                text-decoration: none;
                transition: all 0.3s;
                border-left: 3px solid transparent;
            }

            .nav-item:hover {
                background: rgba(255,255,255,0.1);
                border-left-color: white;
            }

            .nav-item.active {
                background: rgba(255,255,255,0.2);
                border-left-color: white;
                font-weight: 600;
            }

            .nav-item-icon {
                font-size: 18px;
                margin-right: 12px;
                width: 24px;
                text-align: center;
            }

            .nav-item-label {
                font-size: 14px;
            }

            .sidebar-footer {
                padding: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
            }

            .user-info {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                padding: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }

            .user-icon {
                width: 40px;
                height: 40px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                margin-right: 10px;
            }

            .user-details {
                flex: 1;
            }

            .user-email {
                font-size: 12px;
                opacity: 0.9;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .user-role {
                font-size: 10px;
                opacity: 0.7;
                text-transform: uppercase;
            }

            .btn-logout {
                width: 100%;
                padding: 10px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }

            .btn-logout:hover {
                background: rgba(255,255,255,0.3);
            }

            .main-content {
                margin-left: 260px;
                flex: 1;
                min-height: 100vh;
                padding: 0;
            }

            .content-header {
                background: white;
                padding: 20px 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }

            .content-header h1 {
                color: #333;
                font-size: 28px;
                margin-bottom: 5px;
            }

            .content-header .breadcrumb {
                color: #666;
                font-size: 14px;
            }

            .content-body {
                padding: 20px 30px;
            }

            /* Auto-refresh indicator */
            .refresh-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(102, 126, 234, 0.9);
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 999;
                display: none;
                animation: fadeIn 0.3s;
            }

            .refresh-indicator.show {
                display: block;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .admin-sidebar {
                    width: 200px;
                }
                .main-content {
                    margin-left: 200px;
                }
            }
        </style>
    `;
    document.head.insertAdjacentHTML('beforeend', styles);
}

// Get current page
function getCurrentPage() {
    const path = window.location.pathname;
    const page = ADMIN_NAV.pages.find(p => path.includes(p.url.replace('.html', '')));
    return page ? page.id : 'dashboard';
}

// Get user info from localStorage
function getUserInfo() {
    return {
        email: localStorage.getItem('admin_email') || 'admin@leadex.com',
        role: localStorage.getItem('admin_role') || 'Admin'
    };
}

// Logout function
function adminLogout() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_email');
    localStorage.removeItem('admin_role');
    window.location.href = '/admin-login.html';
}

// Build navigation HTML
function buildNavigation() {
    const currentPage = getCurrentPage();
    const userInfo = getUserInfo();

    const navItems = ADMIN_NAV.pages.map(page => `
        <a href="${page.url}" class="nav-item ${page.id === currentPage ? 'active' : ''}">
            <span class="nav-item-icon">${page.icon}</span>
            <span class="nav-item-label">${page.label}</span>
        </a>
    `).join('');

    return `
        <div class="admin-sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">🚀 Leadex</div>
                <div class="sidebar-subtitle">Admin Dashboard</div>
            </div>

            <nav class="sidebar-nav">
                ${navItems}
            </nav>

            <div class="sidebar-footer">
                <div class="user-info">
                    <div class="user-icon">👤</div>
                    <div class="user-details">
                        <div class="user-email" title="${userInfo.email}">${userInfo.email}</div>
                        <div class="user-role">${userInfo.role}</div>
                    </div>
                </div>
                <button class="btn-logout" onclick="adminLogout()">Logout</button>
            </div>
        </div>

        <div class="refresh-indicator" id="refreshIndicator">
            <span id="refreshText">Refreshing...</span>
        </div>
    `;
}

// Initialize navigation
function initAdminNav() {
    // Inject styles
    injectNavStyles();

    // Insert navigation
    const nav = buildNavigation();
    document.body.insertAdjacentHTML('afterbegin', nav);

    // Wrap existing content
    const existingContent = Array.from(document.body.children).filter(
        el => !el.classList.contains('admin-sidebar') && !el.classList.contains('refresh-indicator')
    );

    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';

    existingContent.forEach(el => {
        mainContent.appendChild(el);
    });

    document.body.appendChild(mainContent);
}

// Auto-refresh function
let autoRefreshInterval = null;

function startAutoRefresh(refreshFunction, interval = 20000) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    autoRefreshInterval = setInterval(async () => {
        const indicator = document.getElementById('refreshIndicator');
        if (indicator) {
            indicator.classList.add('show');
            indicator.querySelector('#refreshText').textContent = 'Refreshing...';
        }

        try {
            await refreshFunction();
            if (indicator) {
                indicator.querySelector('#refreshText').textContent = 'Updated!';
            }
        } catch (error) {
            console.error('Refresh error:', error);
            if (indicator) {
                indicator.querySelector('#refreshText').textContent = 'Refresh failed';
            }
        }

        setTimeout(() => {
            if (indicator) {
                indicator.classList.remove('show');
            }
        }, 2000);
    }, interval);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdminNav);
} else {
    initAdminNav();
}

// Export functions for global use
window.adminLogout = adminLogout;
window.startAutoRefresh = startAutoRefresh;
window.stopAutoRefresh = stopAutoRefresh;

