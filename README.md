# Team Update Tool 🚀

A custom **ERPNext v15+ / Frappe Framework v15+** application for tracking completed team projects with GitHub integration, screenshot uploads, and role-based access control.

> **Note:** ERPNext v15+ is **required** to run this app. Install it on a bench with ERPNext before installing Team Update Tool.

## ✨ Features

- **Role-Based Access**: `Admin` (full CRUD) and `View-Only User` (read-only, server-enforced)
- **Master Data**: Project Categories, Teams, Technologies, Project Statuses
- **Project Management**: Track projects with GitHub repos, files, screenshots, and updates
- **GitHub Integration**: Auto-fetch repo metadata (commit SHA, languages, default branch)
- **File Upload**: Support for PNG, JPG, JPEG, PDF, DOCX formats
- **Notifications**: In-app alerts for new projects, approvals, and status changes
- **Reports**: Project Summary, Team Activity, Completed Projects, GitHub Repository

## 🔐 Login Types

The application supports two types of users:

### Admin Login
- Full access to all features
- Can create, edit, delete, approve, and reject projects
- Access to admin desk and settings
- Manage all team members and projects

### User Login (View-Only)
- Read-only access to approved projects
- Can view project details, screenshots, and documentation
- Cannot modify or delete any content
- Server-enforced permissions

## 🛠️ Prerequisites

- **Frappe Framework v15+** (comes with ERPNext)
- **ERPNext v15+** — required dependency

## 🛠️ Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/balaji-001-gif/team_update_tool.git
bench --site your-site.local install-app team_update_tool
bench --site your-site.local migrate
bench build --app team_update_tool
bench restart
```

> ERPNext is installed automatically as a dependency — the `required_apps` declaration in `hooks.py` ensures Frappe handles it for you.

## 👥 Roles & Permissions

| Role | Permissions | Access Level |
|------|-------------|--------------|
| **Admin** | Full CRUD on all DocTypes. Can create, edit, delete, approve, reject | Full Access |
| **View-Only User** | Read-only. Can view approved projects, GitHub repos, screenshots | Restricted |

### Permission Layers

Permissions are enforced in three layers:

1. **DocType permission table** - Role-based CRUD in each JSON file
2. **`get_permission_query_conditions()`** - View-Only Users only see Approved projects in list views
3. **`has_permission()`** - Doc-level read check for View-Only Users

## 📁 Documents & Files

Documents are organized by project with approval status:

- **Approved Documents** - Visible to all users (Admin and View-Only)
- **Pending Documents** - Visible only to Admin users
- Each document shows:
  - Project name
  - File type (PDF, DOCX, Images, etc.)
  - Upload date
  - Approval status

## 📋 Naming Series

| Doctype | Format |
|---------|--------|
| Project | PRJ-.YYYY.-.##### |
| GitHub Repository | GR-.YYYY.-.##### |
| Project Update | PU-.YYYY.-.##### |

## 📦 Modules

| Module | Description |
|--------|-------------|
| **Masters** | Project Category, Team, Technology, Project Status |
| **Transactions** | Project, Project Files, Project Screenshots, GitHub Repository, Project Update |
| **Reports** | Project Summary, Team Activity, Completed Projects, GitHub Repository |

## 🔧 Frappe v15 Compatible

- All code lives inside `apps/team_update_tool` only
- Uses Frappe ORM (`frappe.get_doc`, `frappe.get_all`, `frappe.db.count`)
- No deprecated APIs
- Upgrade-safe with version-controlled JSON files
- Fixtures exportable via `bench export-fixtures`
