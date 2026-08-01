// Team Update Tool — Complete Client-side JavaScript (Bootstrap 5)

frappe.provide("team_update_tool");

// ==============================
// Bootstrap 5 Navbar (JS-injected)
// ==============================

function tutRenderNavbar() {
	if (document.querySelector('.tut-navbar')) return;

	var html = '' +
	'<nav class="tut-navbar navbar navbar-expand-lg" data-bs-theme="light">' +
	'<div class="container-fluid">' +
	'<button class="btn btn-sm btn-outline-secondary me-2 d-lg-none" id="sidebarToggle" type="button" aria-label="Toggle sidebar">' +
	'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>' +
	'</button>' +
	'<a class="navbar-brand" href="/team_update_tool">' +
	'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' +
	'<span>Team Update Tool</span></a>' +
	'<button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu" aria-controls="navMenu" aria-expanded="false" aria-label="Toggle navigation">' +
	'<span class="navbar-toggler-icon"></span></button>' +
	'<div class="collapse navbar-collapse" id="navMenu">' +
	'<ul class="navbar-nav me-auto mb-2 mb-lg-0">' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool">Home</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/dashboard">Dashboard</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/projects">Projects</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/repositories">Repositories</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/gallery">Gallery</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/documents">Documents</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/kanban">Kanban</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/gantt">Gantt</a></li>' +
	'<li class="nav-item"><a class="nav-link" href="/team_update_tool/reports">Reports</a></li>' +
	'</ul>' +
	'<ul class="navbar-nav" id="navUserSection">' +
	'<li class="nav-item" id="navGuest"><a class="nav-link" href="/team_update_tool/login">Sign In</a></li>' +
	'<li class="nav-item" id="navGuest2"><a class="nav-link" href="/team_update_tool/signup">Sign Up</a></li>' +
	'<li class="nav-item dropdown" id="navUserDropdown" style="display:none;">' +
	'<a class="nav-link dropdown-toggle d-flex align-items-center gap-1" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">' +
	'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' +
	'</a>' +
	'<ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 rounded-3 mt-2" style="min-width:180px;">' +
	'<li><a class="dropdown-item" href="/team_update_tool/profile"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>Profile</a></li>' +
	'<li><a class="dropdown-item" href="/team_update_tool/notifications"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>Notifications</a></li>' +
	'<li><a class="dropdown-item" href="/team_update_tool/settings"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>Settings</a></li>' +
	'<li><hr class="dropdown-divider"></li>' +
	'<li><a class="dropdown-item text-danger" href="/team_update_tool/logout"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>Sign Out</a></li>' +
	'</ul></li></ul></div></div></nav>';

	// Inject at top of page
	var target = document.querySelector('.page-content') || document.querySelector('.container:first-child') || document.body;
	target.insertAdjacentHTML('afterbegin', html);

	// Auth check
	fetch('/api/method/team_update_tool.api.auth.get_current_user')
		.then(function(r) { return r.json(); })
		.then(function(d) {
			if (d.message && !d.message.guest) {
				var drop = document.getElementById('navUserDropdown');
				var guest = document.getElementById('navGuest');
				var guest2 = document.getElementById('navGuest2');
				if (drop) drop.style.display = 'block';
				if (guest) guest.style.display = 'none';
				if (guest2) guest2.style.display = 'none';
			}
		})
		.catch(function() {});

	// Active nav link
	var path = window.location.pathname;
	document.querySelectorAll('.tut-navbar .nav-link').forEach(function(link) {
		var href = link.getAttribute('href');
		if (href && path.startsWith(href) && href !== '/team_update_tool') {
			link.classList.add('active');
		} else if (href === '/team_update_tool' && path === '/team_update_tool') {
			link.classList.add('active');
		}
	});
}

// ==============================
// Bootstrap 5 Left Sidebar (JS-injected)
// ==============================

function tutRenderSidebar() {
	if (document.querySelector('.tut-sidebar')) return;

	var html = '' +
	'<div class="tut-sidebar offcanvas offcanvas-start" tabindex="-1" id="tutSidebar" aria-labelledby="tutSidebarLabel">' +
	'<div class="offcanvas-header border-bottom">' +
	'<h5 class="offcanvas-title fw-bold" id="tutSidebarLabel">Navigation</h5>' +
	'<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>' +
	'</div>' +
	'<div class="offcanvas-body p-0 pt-2">' +
	'<div class="sidebar-section">Main</div>' +
	'<a class="nav-link" href="/team_update_tool/dashboard"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>Dashboard</a>' +
	'<a class="nav-link" href="/team_update_tool/projects"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>Projects</a>' +
	'<a class="nav-link" href="/team_update_tool/my_projects"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>My Projects</a>' +
	'<a class="nav-link" href="/team_update_tool/create_project"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>New Project</a>' +
	'<a class="nav-link" href="/team_update_tool/kanban"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>Kanban Board</a>' +
	'<a class="nav-link" href="/team_update_tool/gantt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/><path d="M12 21V9"/><path d="M15 21V9"/></svg>Gantt Chart</a>' +
	'<div class="sidebar-section">Browse</div>' +
	'<a class="nav-link" href="/team_update_tool/repositories"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>Repositories</a>' +
	'<a class="nav-link" href="/team_update_tool/gallery"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>Gallery</a>' +
	'<a class="nav-link" href="/team_update_tool/documents"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>Documents</a>' +
	'<a class="nav-link" href="/team_update_tool/reports"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>Reports</a>' +
	'<div class="sidebar-section">Account</div>' +
	'<a class="nav-link" href="/team_update_tool/notifications"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>Notifications</a>' +
	'<a class="nav-link" href="/team_update_tool/profile"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>Profile</a>' +
	'<a class="nav-link" href="/team_update_tool/settings"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>Settings</a>' +
	'<div class="tut-sidebar-divider"></div>' +
	'<a class="nav-link text-danger" href="/team_update_tool/logout"><svg viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>Sign Out</a>' +
	'</div></div>';

	// Inject sidebar after navbar
	var navbar = document.querySelector('.tut-navbar');
	if (navbar) {
		navbar.insertAdjacentHTML('afterend', html);
	}

	// Active sidebar link
	var path = window.location.pathname;
	setTimeout(function() {
		document.querySelectorAll('.tut-sidebar .nav-link').forEach(function(link) {
			var href = link.getAttribute('href');
			if (href && (path === href || (path.startsWith(href) && href !== '/team_update_tool' && href !== '/team_update_tool/projects'))) {
				link.classList.add('active');
			}
		});
		// Special case for projects sub-routes
		if (path.startsWith('/team_update_tool/project/')) {
			var pl = document.querySelector('.tut-sidebar a[href="/team_update_tool/projects"]');
			if (pl) pl.classList.add('active');
		}
	}, 50);

	// Sidebar toggle on mobile
	var sidebarToggle = document.getElementById('sidebarToggle');
	if (sidebarToggle) {
		sidebarToggle.addEventListener('click', function() {
			var sidebar = document.getElementById('tutSidebar');
			if (sidebar) {
				var bsOffcanvas = bootstrap.Offcanvas.getInstance(sidebar) || new bootstrap.Offcanvas(sidebar);
				bsOffcanvas.toggle();
			}
		});
	}
}

// ==============================
// Toast Notifications
// ==============================

function tutToast(message, type) {
	if (typeof type === 'undefined') type = 'info';
	var container = document.querySelector('.tut-toast-container');
	if (!container) {
		container = document.createElement('div');
		container.className = 'tut-toast-container';
		document.body.appendChild(container);
	}
	var colors = { info: '#2563eb', success: '#16a34a', error: '#dc2626', warning: '#f59e0b' };
	var bg = colors[type] || '#2563eb';
	var toast = document.createElement('div');
	toast.style.cssText = 'background:#fff;border-left:4px solid ' + bg + ';border-radius:0.5rem;padding:12px 16px;box-shadow:0 4px 16px rgba(0,0,0,0.08);font-size:0.88rem;color:#1e293b;max-width:340px;animation:tutToastIn 0.25s ease;';
	toast.textContent = message;
	container.appendChild(toast);
	setTimeout(function() {
		toast.style.transition = 'all 0.25s ease';
		toast.style.opacity = '0';
		toast.style.transform = 'translateX(40px)';
		setTimeout(function() { toast.remove(); }, 300);
	}, 4000);
}

// ==============================
// Confirm Dialog
// ==============================

function tutConfirm(message, title) {
	if (typeof title === 'undefined') title = 'Confirm';
	return new Promise(function(resolve) {
		var overlay = document.createElement('div');
		overlay.className = 'tut-modal-overlay';
		overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9999;display:flex;align-items:center;justify-content:center;';
		overlay.innerHTML =
			'<div style="background:#fff;border-radius:1rem;padding:1.75rem;max-width:400px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.12);">' +
			'<h5 class="fw-bold mb-2">' + escHtml(title) + '</h5>' +
			'<p class="mb-3" style="color:#64748b;font-size:0.9rem;">' + escHtml(message) + '</p>' +
			'<div class="d-flex gap-2 justify-content-end">' +
			'<button class="btn btn-outline-secondary btn-sm" id="tutConfirmNo">Cancel</button>' +
			'<button class="btn btn-primary btn-sm" id="tutConfirmYes">Confirm</button>' +
			'</div></div>';
		document.body.appendChild(overlay);
		document.getElementById('tutConfirmYes').addEventListener('click', function() { overlay.remove(); resolve(true); });
		document.getElementById('tutConfirmNo').addEventListener('click', function() { overlay.remove(); resolve(false); });
		overlay.addEventListener('click', function(e) { if (e.target === overlay) { overlay.remove(); resolve(false); } });
	});
}

// ==============================
// Utility Functions
// ==============================

function escHtml(s) {
	if (!s) return '';
	return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');
}

function formatDate(d) {
	if (!d) return '';
	return d.substring(0,10);
}

// ==============================
// Init — Render Navbar + Sidebar
// ==============================

// Check if frappe.ready is available (only in website/desk context)
if (typeof frappe !== 'undefined' && typeof frappe.ready === 'function') {
	frappe.ready(function() {
		tutRenderNavbar();

		// Only render sidebar on authenticated pages (not login, signup, or home)
		var path = window.location.pathname;
		var noSidebar = ['/team_update_tool/login', '/team_update_tool/signup', '/team_update_tool/logout', '/team_update_tool'];
		var shouldShowSidebar = !noSidebar.includes(path) && path.startsWith('/team_update_tool');

		if (shouldShowSidebar && typeof bootstrap !== 'undefined') {
			tutRenderSidebar();
		}
	});
}
