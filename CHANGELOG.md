# Changelog

All notable changes to the Team Update Tool are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Kanban board view for project management
- Activity Feed with Comments for project collaboration
- Time Tracking features for project work logging
- `get_all_public_stats` and `get_projects` API endpoints for the projects listing page
- `create_project_update` API method
- `get_project_detail` API method
- `create_project`, `add_project_file`, `create_project_readme` API methods
- Comprehensive SOP documentation (v2.1)
- CI/CD configuration with GitHub Actions

### Fixed
- Use `get_all` instead of `count` for list filters in `get_projects`
- Migration patch to add parent columns to child tables
- Add `istable=1` to child table DocTypes missing parent column
- Workspace shortcuts type must match Workspace Shortcut doctype options
- Workspace synchronization (delete-and-recreate on update)

---

## [1.0.0] - 2026-07-17

### Added
- ERPNext declared as mandatory dependency in `hooks.py`
- `install.py` with `after_install()` hook for automatic setup
- Automatic creation of four roles: Team Update Admin, Team Update Team Leader, Team Update Team Member, Team Update Viewer
- `rename_roles` migration patch for upgrading from older versions
- Comprehensive API module (`api/projects.py`) with full project lifecycle endpoints
- Project creation, file upload, GitHub repository, and README management APIs
- Direct SQL and Frappe ORM support for data persistence
- Notifications system (in-app + email) for project lifecycle events
- Proper DocType fixtures and workspace synchronization

### Changed
- Complete role rename to `Team Update Admin`/`Team Update Team Leader`/`Team Update Team Member`/`Team Update Viewer`
- Simplified README installation instructions
- Child tables converted to standalone DocTypes with proper autoname/permissions/title_field
- Workspace JSON structure aligned with Frappe v15 standards
- Role-based permission query conditions for list views

### Fixed
- Workspace not showing in workspace list
- Dynamic Link validation errors during workspace sync
- Module path alignment between `modules.txt` and DocType JSON module names
- Child table `istable=1` flag and parent column addition
- Gunicorn `preload_app` compatibility
- Various Frappe v15 compatibility issues

---

## [0.9.0] - 2026-07-13

### Added
- Royal Professional Theme (Purple & Gold design) applied across all pages
- Professional UI redesign for dashboard, projects, project detail, and create project pages
- Gallery page with screenshot display
- Documents page with reference document download
- Notifications panel on dashboard
- Reports page with Project Status Summary
- Repositories page with GitHub repo listing
- Quick Links section for navigation
- Data seeding scripts and demo data support
- Comprehensive error handling and debugging

### Changed
- Complete Bootstrap 5 professional UI redesign with navbar, offcanvas sidebar, responsive templates
- Dashboard redesigned with ERPNext v15 professional layout
- Project creation form updated with multi-step workflow
- File upload and screenshot handling improvements
- Gallery API with full URL construction for file paths

### Fixed
- JavaScript syntax errors across multiple templates
- CSRF token handling for API calls
- Gallery showing "No screenshots" - switched to raw SQL queries
- Projects page showing "No Projects Found" - switched to raw SQL queries
- Screenshot and file 404 errors with full site URL prefix
- GitHub Repository duplicate entry errors
- Project naming series and autoname issues
- Child table loading and linking errors
- Notification creation error handling
- Missing `escHtml` function across multiple pages
- `set_value` usage in patches for Frappe compatibility

---

## [0.8.0] - 2026-07-10

### Added
- "Royal Professional" premium theme with Purple & Gold design
- Enhanced login page with premium styling
- Professional UI redesign for all pages
- Responsive card-based layouts
- Role badge system with permission info modals
- Improved empty state handling

### Changed
- Complete UI overhaul across the entire application
- Enhanced stat cards and dashboard layout
- Project detail page with ERPNext 15 professional style
- Reports page with professional styling

---

## [0.7.0] - 2026-07-09

### Added
- Standalone DocTypes for child tables (Team Member, Project Update, Project Files, Project Screenshots, Project Technology)
- Project Readme doctype with frontend and backend support
- `post_model_sync` patch to set `restrict_to_domain` on child tables
- Card Break entries to organize workspace links into Masters, Transactions, Reports cards
- Workspace shortcuts for sidebar quick links
- Auto-sync doctypes on install and setup
- Persistent navbar across all pages
- Data-driven website rebuild with dynamic JS-driven pages

### Changed
- Child tables converted to standalone DocTypes with proper autoname/permissions
- Module paths alignment with Frappe v15 directory standards
- Workspace content field format to use EditorJS data wrapper
- All DocTypes moved to correct module directories
- Permission system with 2 roles (Admin/View-Only User)

### Fixed
- Module paths in all DocTypes, Reports, and Notifications
- Workspace sync and link format for Frappe v15
- Double-nested module path in `hooks.py` `permission_query_conditions`
- Project naming with Autoincrement format (PRJ-.#####)
- Child table DocTypes hidden from Frappe module sidebar via `restrict_to_domain`
- Various `ModuleNotFoundError` issues during `bench migrate`

---

## [0.6.0] - 2026-07-08

### Added
- Complete portal overhaul with custom login, profile, settings, notifications, and logout pages
- Multi-step project creation with GitHub validation and screenshot preview
- 404 and 403 error pages
- Child table linking APIs for screenshots and files
- Frappe Desk dashboard at `/app/team-update-dashboard` with charts, stats, and sidebar
- Bootstrap 5 professional UI with navbar, offcanvas sidebar, and responsive templates
- Toast and confirm utility functions
- Website route rules for Vue 3 SPA frontend

### Changed
- Complete data-driven website rebuild with comprehensive APIs
- Dynamic dashboard, path-based project URLs, reports, and documents
- Login redirect to dashboard
- Optimized notifications performance
- Project creation flow with proper validation

### Fixed
- Navbar include path for Frappe v15
- Homepage Jinja variables rendering by moving to proper directory structure
- Sidebar margin and layout issues
- Dashboard console errors and undefined function issues
- Child table columns added to Project Update via patch

---

## [0.5.0] - 2026-07-07

### Added
- Initial Frappe v15 rebuild with 2 roles (Admin/View-Only User)
- 10 DocTypes: Team, Team Member, Technology, Project Category, Project Status, Project, Project Update, Project Files, Project Screenshots, Project Technology
- 4 Reports: Project Summary, Team Activity, Completed Projects, GitHub Repository
- 3 Notifications: New Project Uploaded, Project Approved, Project Status Updated
- Workspace with Card Breaks and Links
- Naming series for all DocTypes
- GitHub auto-fetch for repository metadata
- 3-layer security (DocType permissions, permission query conditions, has_permission)
- Vue 3 + Vite SPA architecture
- Complete role-based task management workflow with 4 roles
- Comprehensive SOP document
- Demo data seeding script
- Professional Frappe Desk dashboard

### Changed
- Restructured repo for `bench get-app` compatibility
- Cleaned up setup.py and requirements.txt for uv pip install compatibility
- Roles renamed to Project Admin/Contributor/Viewer
- DocType renamed to Project Submission

---

## [0.1.0] - 2026-07-07

### Added
- Initial commit with basic project structure
- Team Update Tool foundation files
- Project tracking with GitHub links and screenshots
- Role-based access (Admin/Viewer)
- Basic Frappe app setup

---

[Unreleased]: https://github.com/balaji-001-gif/team_update_tool/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/balaji-001-gif/team_update_tool/compare/v0.1.0...v0.5.0
[0.1.0]: https://github.com/balaji-001-gif/team_update_tool/releases/tag/v0.1.0
