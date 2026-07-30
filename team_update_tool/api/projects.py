# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import json
import calendar
from datetime import date, datetime, timedelta

import frappe
from frappe import _
from frappe.utils import today, now_datetime, getdate, fmt_money
from frappe.model.naming import make_autoname


# ---------------------------------------------------------------------------
# Remote-added: helpers and project CRUD
# ---------------------------------------------------------------------------


def _set_resolved_name(doc, naming_pattern, prefix):
    """Set a resolved name on a document using the naming series.

    Falls back to a hash-based unique name if the naming series fails.
    """
    try:
        doc.name = make_autoname(naming_pattern)
    except Exception:
        doc.name = f"{prefix}-{frappe.generate_hash(length=10)}"

def _get_default_status():
    """Return the name of a default Project Status (first available, or creates 'Pending')."""
    status = frappe.db.get_value("Project Status", {"status_name": "Pending"}, "name")
    if status:
        return status
    # Fallback to any existing status
    all_statuses = frappe.get_all("Project Status", fields=["name"], limit=1)
    if all_statuses:
        return all_statuses[0].name
    # If no status exists yet, create one
    doc = frappe.get_doc({"doctype": "Project Status", "status_name": "Pending", "color": "#6b7280"})
    doc.insert(ignore_permissions=True)
    return doc.name


def _get_or_create_github_repository(github_url, branch="main"):
    """Find existing GitHub Repository by URL or create a new one."""
    if not github_url:
        return None

    existing = frappe.db.get_value("GitHub Repository", {"repository_url": github_url}, "name")
    if existing:
        return existing

    # Extract repo name from URL
    repo_name = github_url.rstrip("/").split("/")[-1] if github_url else ""

    # Create the document with an explicitly resolved naming series name.
    # This avoids role-dependent failures in Frappe's document-level naming.
    doc = frappe.get_doc({
        "doctype": "GitHub Repository",
        "repository_url": github_url,
        "repository_name": repo_name,
        "default_branch": branch or "main",
    })
    _set_resolved_name(doc, "GR-.YYYY.-.#####", "GR")

    try:
        doc.insert(ignore_permissions=True)
        return doc.name
    except frappe.DuplicateEntryError:
        frappe.db.rollback()
        # Another request may have created this repo concurrently.
        existing = frappe.db.get_value("GitHub Repository", {"repository_url": github_url}, "name")
        if existing:
            return existing
        doc = frappe.get_doc({
            "doctype": "GitHub Repository",
            "repository_url": github_url,
            "repository_name": repo_name,
            "default_branch": branch or "main",
        })
        doc.name = f"GR-{frappe.generate_hash(length=10)}"
        doc.insert(ignore_permissions=True)
        return doc.name


@frappe.whitelist()
def create_project():
    """Create a new Project from the create_project page form.

    Expects POST data with:
      - project_title (required)
      - team (required)
      - project_category
      - priority
      - description
      - start_date, due_date
      - technologies (list of Technology names)
      - github_url, github_branch
    """
    data = frappe.local.form_dict

    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in to create a project."), frappe.PermissionError)

    # Validate required fields
    project_title = data.get("project_title")
    team = data.get("team")

    if not project_title:
        frappe.throw(_("Project title is required."))
    if not team:
        frappe.throw(_("Team is required."))

    # Get default status
    status = _get_default_status()

    # Handle GitHub repository
    github_url = data.get("github_url")
    github_branch = data.get("github_branch")
    github_repo = _get_or_create_github_repository(github_url, github_branch)

    # Build technologies child table
    technologies = data.get("technologies")
    if isinstance(technologies, str):
        technologies = frappe.parse_json(technologies)
    if not technologies:
        technologies = []

    tech_children = []
    for tech in technologies:
        if frappe.db.exists("Technology", tech):
            tech_children.append({"technology": tech})
        else:
            # Create Technology record if it doesn't exist
            try:
                tech_doc = frappe.get_doc({"doctype": "Technology", "technology_name": tech})
                tech_doc.insert(ignore_permissions=True)
                tech_children.append({"technology": tech_doc.name})
            except Exception:
                pass

    # Create the project
    project = frappe.get_doc({
        "doctype": "Project",
        "project_title": project_title,
        "project_category": data.get("project_category") or None,
        "team": team,
        "status": status,
        "priority": data.get("priority") or "Medium",
        "description": data.get("description") or "",
        "start_date": data.get("start_date") or None,
        "due_date": data.get("due_date") or None,
        "github_repository": github_repo,
        "technologies": tech_children,
    })

    project.insert(ignore_permissions=True, ignore_links=True)

    frappe.db.commit()

    return {
        "name": project.name,
        "project_title": project.project_title,
        "message": _("Project created successfully!"),
    }


@frappe.whitelist()
def add_project_file():
    """Link an uploaded file to a Project.

    Expects POST data with:
      - project_name (required)
      - file_url (required)
      - file_name
    """
    data = frappe.local.form_dict
    project_name = data.get("project_name")
    file_url = data.get("file_url")
    file_name = data.get("file_name")

    if not project_name or not file_url:
        frappe.throw(_("Project name and file URL are required."))

    if not frappe.db.exists("Project", project_name):
        frappe.throw(_("Project not found: {0}").format(project_name))

    # Determine file type from extension
    ext = (file_name or file_url or "").split(".")[-1].lower() if (file_name or file_url) else ""
    file_type_map = {
        "png": "PNG", "jpg": "JPG", "jpeg": "JPEG",
        "pdf": "PDF", "docx": "DOCX",
    }
    file_type = file_type_map.get(ext, "Other")

    doc = frappe.get_doc({
        "doctype": "Project Files",
        "project": project_name,
        "file": file_url,
        "file_name": file_name or file_url.split("/")[-1] if "/" in (file_url or "") else file_name,
        "file_type": file_type,
    })
    doc.insert(ignore_permissions=True, ignore_links=True)
    frappe.db.commit()

    return {
        "name": doc.name,
        "message": _("File linked successfully!"),
    }


@frappe.whitelist()
def create_project_readme():
    """Create or update a Project Readme for a project.

    Expects POST data with:
      - project_name (required)
      - readme_file (file URL of uploaded readme document)
      - readme_content (readme text content)
    """
    data = frappe.local.form_dict
    project_name = data.get("project_name")
    readme_file = data.get("readme_file")
    readme_content = data.get("readme_content")

    if not project_name:
        frappe.throw(_("Project name is required."))

    if not frappe.db.exists("Project", project_name):
        frappe.throw(_("Project not found: {0}").format(project_name))

    # Check if a readme already exists for this project
    existing = frappe.db.get_value("Project Readme", {"project": project_name}, "name")

    if existing:
        doc = frappe.get_doc("Project Readme", existing)
        if readme_file:
            doc.readme_file = readme_file
        if readme_content:
            doc.readme_content = readme_content
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"name": doc.name, "message": _("Readme updated successfully!")}
    else:
        doc_data = {"doctype": "Project Readme", "project": project_name}
        if readme_file:
            doc_data["readme_file"] = readme_file
        if readme_content:
            doc_data["readme_content"] = readme_content
        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True, ignore_links=True)
        frappe.db.commit()
        return {"name": doc.name, "message": _("Readme created successfully!")}


@frappe.whitelist()
def create_project_update():
    """Add an update to a Project.

    Expects POST data with:
      - project_name (required)
      - update_title (required)
      - update_date (required, format: YYYY-MM-DD)
      - update_description
      - status (optional, Link to Project Status)
    """
    data = frappe.local.form_dict

    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in to add a project update."), frappe.PermissionError)

    project_name = data.get("project_name")
    update_title = data.get("update_title")
    update_date = data.get("update_date")
    update_description = data.get("update_description", "")
    update_status = data.get("status")

    # Validate required fields
    if not project_name:
        frappe.throw(_("Project name is required."))
    if not update_title:
        frappe.throw(_("Update title is required."))
    if not update_date:
        frappe.throw(_("Update date is required."))

    # Check project exists
    if not frappe.db.exists("Project", project_name):
        frappe.throw(_("Project not found: {0}").format(project_name))

    # Permission check for Viewer role
    roles = frappe.get_roles(user)
    if "Team Update Viewer" in roles or "View-Only User" in roles:
        is_viewer = "Team Update Admin" not in roles and "Admin" not in roles and "System Manager" not in roles
        if is_viewer:
            frappe.throw(_("You do not have permission to add updates."), frappe.PermissionError)

    # Append update to Project's child table
    project = frappe.get_doc("Project", project_name)
    row = project.append("project_updates", {
        "update_title": update_title,
        "update_date": update_date,
        "update_description": update_description,
        "updated_by": user,
    })
    if update_status:
        row.status = update_status

    # Also update the project's main status if a status is provided
    if update_status and frappe.db.exists("Project Status", update_status):
        project.status = update_status

    project.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": row.name,
        "update_title": update_title,
        "update_date": update_date,
        "message": _("Update added successfully!"),
    }


# ---------------------------------------------------------------------------
# Helpers (added by our Kanban / Activity / Time features)
# ---------------------------------------------------------------------------

def _get_base_filters(user=None):
    """Return permission-aware base filters for the current user."""
    if user is None:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles
    is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not is_admin
    filters = {}
    if is_viewer:
        approved = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
        if approved:
            filters["status"] = approved
    return filters, is_admin


def _get_status_info(status):
    """Return dict with status_name and color for a status link value."""
    if not status:
        return {"status_name": "", "color": "#6b7280"}
    try:
        s = frappe.get_cached_doc("Project Status", status)
        return {"status_name": s.status_name, "color": s.color}
    except Exception:
        return {"status_name": status, "color": "#6b7280"}


def _enrich_project(p):
    """Attach status_name / status_color to a project dict."""
    info = _get_status_info(p.get("status") or "")
    p["status_name"] = info["status_name"]
    p["status_color"] = info["color"]
    return p


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_dashboard_stats():
    """Return dashboard statistics for the current user.

    Called by the dashboard JS (team_update_tool.api.projects.get_dashboard_stats).
    Returns a dict with:
      - total_projects, total_teams, total_technologies, my_projects
      - is_admin, status_counts, recent_projects, recent_repos
    """
    user = frappe.session.user
    if user == "Guest":
        return {"error": _("Please log in to view dashboard stats.")}

    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles
    is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not is_admin

    # Build base filters
    base_filters = {}
    if is_viewer:
        approved = frappe.db.get_value(
            "Project Status", {"status_name": "Approved"}, "name"
        )
        if approved:
            base_filters["status"] = approved

    # Statistics
    total_projects = frappe.db.count("Project", filters=base_filters)
    total_teams = frappe.db.count("Team", filters={"is_active": 1})
    total_technologies = frappe.db.count("Technology")
    my_projects = frappe.db.count("Project", filters={"owner": user})

    # Status counts
    status_counts = []
    statuses = frappe.get_all(
        "Project Status", fields=["name", "status_name", "color"]
    )
    for s in statuses:
        filters = {**base_filters, "status": s.name}
        count = frappe.db.count("Project", filters=filters)
        if count:
            status_counts.append({
                "name": s.status_name,
                "count": count,
                "color": s.color,
            })

    # Recent projects
    recent_projects = frappe.get_all(
        "Project",
        fields=["name", "project_title", "status", "owner", "creation"],
        limit=5,
        order_by="modified desc",
    )
    for p in recent_projects:
        _enrich_project(p)

    # Recent GitHub repos
    recent_repos = []
    try:
        recent_repos = frappe.get_all(
            "GitHub Repository",
            fields=["name", "repository_name", "repository_url", "creation"],
            limit=5,
            order_by="creation desc",
        )
        for r in recent_repos:
            if r.repository_name:
                r.name = r.repository_name
    except Exception:
        recent_repos = []

    return {
        "total_projects": total_projects,
        "total_teams": total_teams,
        "total_technologies": total_technologies,
        "my_projects": my_projects,
        "is_admin": is_admin,
        "status_counts": status_counts,
        "recent_projects": recent_projects,
        "recent_repos": recent_repos,
    }


# ---------------------------------------------------------------------------
# Public stats and listing (added remotely)
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def get_all_public_stats():
    """Return public stats and filter options for the projects listing page.

    Called by projects.html JS (team_update_tool.api.projects.get_all_public_stats).
    Returns:
      - total_projects
      - teams: [{name, team_name}]
      - statuses: [{name, status_name}]
      - categories: [{name, category_name}]
    """
    total_projects = frappe.db.count("Project")

    teams = frappe.get_all("Team", fields=["name", "team_name"], filters={"is_active": 1}, order_by="team_name asc")
    statuses = frappe.get_all("Project Status", fields=["name", "status_name", "color"], order_by="status_name asc")
    categories = frappe.get_all("Project Category", fields=["name", "category_name"], order_by="category_name asc")

    return {
        "total_projects": total_projects,
        "teams": teams,
        "statuses": statuses,
        "categories": categories,
    }


@frappe.whitelist(allow_guest=True)
def get_projects():
    """Return paginated, filtered list of projects for the projects listing page.

    Called by projects.html JS (team_update_tool.api.projects.get_projects).
    Query params:
      - limit (default 12)
      - offset (default 0)
      - search (text search)
      - status (Project Status name)
      - team (Team name)
      - category (Project Category name)

    Returns:
      - projects: [{name, project_title, team, category_name, status, status_name,
                    status_color, priority, screenshot_preview, modified, creation}]
      - total
      - offset
      - has_more
    """
    data = frappe.local.form_dict

    try:
        limit = int(data.get("limit", 12))
    except (ValueError, TypeError):
        limit = 12
    try:
        offset = int(data.get("offset", 0))
    except (ValueError, TypeError):
        offset = 0

    search = data.get("search", "")
    status_filter = data.get("status", "")
    team_filter = data.get("team", "")
    category_filter = data.get("category", "")

    # Build query filters
    query_filters = []
    if status_filter:
        query_filters.append(["status", "=", status_filter])
    if team_filter:
        query_filters.append(["team", "=", team_filter])
    if category_filter:
        query_filters.append(["project_category", "=", category_filter])
    if search:
        query_filters.append(["project_title", "like", f"%{search}%"])

    try:
        # Get total count with same filters
        filters_arg = query_filters if query_filters else None
        total = frappe.db.count("Project", filters=filters_arg)

        projects = frappe.get_all(
            "Project",
            fields=["name", "project_title", "team", "project_category", "status", "priority", "modified", "creation"],
            filters=filters_arg,
            limit=limit,
            start=offset,
            order_by="modified desc",
        )

        # Enrich with status info, team name, category name, and screenshot preview
        project_list = []
        for p in projects:
            # Status info
            status_name = ""
            status_color = "#6b7280"
            if p.status:
                try:
                    s = frappe.get_cached_doc("Project Status", p.status)
                    status_name = s.status_name
                    status_color = s.color
                except Exception:
                    status_name = p.status

            # Team name
            team_name = p.team or ""
            if p.team:
                try:
                    t = frappe.get_cached_doc("Team", p.team)
                    team_name = t.team_name
                except Exception:
                    pass

            # Category name
            category_name = ""
            if p.project_category:
                try:
                    cat = frappe.get_cached_doc("Project Category", p.project_category)
                    category_name = cat.category_name
                except Exception:
                    category_name = p.project_category

            # Screenshot preview (first screenshot of the project)
            screenshot_preview = None
            try:
                first_ss = frappe.db.get_value("Project Screenshots",
                    {"parent": p.name, "parenttype": "Project", "parentfield": "screenshots"},
                    "screenshot",
                    order_by="idx asc")
                if first_ss:
                    screenshot_preview = first_ss
            except Exception:
                pass

            project_list.append({
                "name": p.name,
                "project_title": p.project_title,
                "team": team_name,
                "category_name": category_name,
                "status": p.status,
                "status_name": status_name,
                "status_color": status_color,
                "priority": p.priority,
                "screenshot_preview": screenshot_preview,
                "modified": str(p.modified) if p.modified else None,
                "creation": str(p.creation) if p.creation else None,
            })

        has_more = (offset + limit) < total

        return {
            "projects": project_list,
            "total": total,
            "offset": offset,
            "has_more": has_more,
        }

    except Exception as e:
        frappe.log_error(
            message=f"get_projects failed: {str(e)}\n{frappe.get_traceback()}",
            title="Team Update Tool - get_projects Error"
        )
        frappe.throw(_("Failed to load projects: {0}").format(str(e)))


# ---------------------------------------------------------------------------
# Project Detail (merged: remote version + our total_hours_logged addition)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_project_detail(name):
    """Return full project detail for the project detail page.

    Called by the project.html JS (team_update_tool.api.projects.get_project_detail).
    Returns a dict with all project fields needed for rendering.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in to view project details."), frappe.PermissionError)

    try:
        project = frappe.get_doc("Project", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Project not found."))

    # Permission check for Viewer role
    roles = frappe.get_roles(user)
    is_viewer = "Team Update Viewer" in roles or "View-Only User" in roles
    if is_viewer:
        is_viewer = "Team Update Admin" not in roles and "Admin" not in roles and "System Manager" not in roles
    if is_viewer:
        approved = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
        if not approved or project.status != approved:
            frappe.throw(_("You do not have permission to view this project."), frappe.PermissionError)

    # Get team name
    team_name = ""
    if project.team:
        try:
            team_doc = frappe.get_cached_doc("Team", project.team)
            team_name = team_doc.team_name
        except Exception:
            team_name = project.team

    # Get status info
    status_info = {"color": "#6b7280", "status_name": ""}
    if project.status:
        try:
            s = frappe.get_cached_doc("Project Status", project.status)
            status_info = {"color": s.color, "status_name": s.status_name}
        except Exception:
            status_info = {"color": "#6b7280", "status_name": project.status}

    # Build technologies list (just names)
    technologies = []
    for t in project.technologies or []:
        try:
            tech_doc = frappe.get_cached_doc("Technology", t.technology)
            technologies.append(tech_doc.technology_name)
        except Exception:
            technologies.append(t.technology)

    # Build files list
    files_list = []
    for f in project.project_files or []:
        files_list.append({
            "file": f.file,
            "file_name": f.file_name,
            "file_type": f.file_type,
            "file_description": getattr(f, "file_description", ""),
        })

    # Build updates list
    updates = []
    for u in project.project_updates or []:
        updates.append({
            "update_title": u.update_title,
            "update_description": u.update_description,
            "update_date": str(u.update_date) if u.update_date else None,
            "updated_by": u.updated_by,
        })

    # Get GitHub info
    github_info = None
    if project.github_repository:
        try:
            repo = frappe.get_cached_doc("GitHub Repository", project.github_repository)
            github_info = {
                "repository_url": repo.repository_url,
                "default_branch": repo.default_branch,
                "commit_hash": getattr(repo, "commit_hash", ""),
                "languages": getattr(repo, "languages", ""),
            }
        except Exception:
            pass

    # Get README
    readme = None
    try:
        readme_doc = frappe.db.get_value("Project Readme", {"project": name}, ["readme_file", "readme_content"], as_dict=1)
        if readme_doc:
            readme = {
                "readme_file": readme_doc.get("readme_file"),
                "readme_content": readme_doc.get("readme_content"),
            }
    except Exception:
        pass

    # Screenshots
    screenshots = []
    for s in project.screenshots or []:
        screenshots.append({
            "screenshot": s.screenshot,
            "caption": getattr(s, "caption", ""),
            "screenshot_type": getattr(s, "screenshot_type", ""),
        })

    # Total time logged (for Time Tracking feature)
    total_hours = frappe.db.sql(
        """SELECT COALESCE(SUM(hours), 0) FROM `tabProject Time Log`
         WHERE project=%s AND docstatus < 2""",
        project.name
    )[0][0] or 0

    # Team projects for mini Gantt chart
    team_projects = []
    if project.team:
        try:
            team_projects_data = frappe.get_all(
                "Project",
                fields=["name", "project_title", "status", "start_date", "due_date", "completion_date"],
                filters={"team": project.team},
                order_by="start_date asc",
            )
            for tp in team_projects_data:
                tp_status_info = _get_status_info(tp.status or "")
                is_overdue = False
                if tp.due_date and not tp.completion_date:
                    if isinstance(tp.due_date, str):
                        due = datetime.strptime(tp.due_date, "%Y-%m-%d").date()
                    else:
                        due = tp.due_date
                    if due < date.today():
                        is_overdue = True
                team_projects.append({
                    "name": tp.name,
                    "title": tp.project_title,
                    "start_date": str(tp.start_date) if tp.start_date else None,
                    "due_date": str(tp.due_date) if tp.due_date else None,
                    "completion_date": str(tp.completion_date) if tp.completion_date else None,
                    "status_color": tp_status_info["color"],
                    "status_name": tp_status_info["status_name"],
                    "is_overdue": is_overdue,
                    "is_current": tp.name == project.name,
                })
        except Exception:
            pass

    return {
        "name": project.name,
        "project_title": project.project_title,
        "team": project.team,
        "team_name": team_name,
        "project_category": project.project_category,
        "priority": project.priority,
        "description": project.description,
        "status": status_info,
        "start_date": str(project.start_date) if project.start_date else None,
        "due_date": str(project.due_date) if project.due_date else None,
        "completion_date": str(project.completion_date) if hasattr(project, "completion_date") and project.completion_date else None,
        "creation": str(project.creation) if project.creation else None,
        "approved_by": getattr(project, "approved_by", ""),
        "tags": getattr(project, "tags", ""),
        "owner": project.owner,
        "technologies": technologies,
        "files": files_list,
        "updates": updates,
        "screenshots": screenshots,
        "github_repository": getattr(project, "github_repository", None),
        "github_info": github_info,
        "readme": readme,
        "total_hours_logged": total_hours,
        "is_owner": project.owner == user,
        "team_projects": team_projects,
    }


# ---------------------------------------------------------------------------
# Kanban Board
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_kanban_projects():
    """Return projects grouped by status for the Kanban board.

    Returns a list of columns with status info and projects[].
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    base_filters, _is_admin = _get_base_filters(user)

    # Fetch all statuses
    statuses = frappe.get_all("Project Status", fields=["name", "status_name", "color"], order_by="modified asc")

    # Fetch projects
    project_fields = ["name", "project_title", "status", "priority", "owner", "team", "start_date", "due_date", "creation"]
    projects = frappe.get_all("Project", fields=project_fields, filters=base_filters, order_by="modified desc")

    for p in projects:
        _enrich_project(p)
        # Resolve team name
        if p.team:
            try:
                t = frappe.get_cached_doc("Team", p.team)
                p.team_name = t.team_name if hasattr(t, "team_name") else p.team
            except Exception:
                p.team_name = p.team
        else:
            p.team_name = ""

    # Group projects by status
    columns = {}
    for s in statuses:
        col_key = s.status_name
        columns[col_key] = {
            "name": s.name,
            "status_name": s.status_name,
            "color": s.color or "#6b7280",
            "projects": [],
        }
    for p in projects:
        sname = p.get("status_name") or "Unknown"
        if sname in columns:
            columns[sname]["projects"].append(p)
        else:
            # Create a fallback column
            columns[sname] = {
                "name": p.get("status"),
                "status_name": sname,
                "color": "#6b7280",
                "projects": [p],
            }

    # Preserve status order
    ordered = []
    for s in statuses:
        if s.status_name in columns:
            ordered.append(columns.pop(s.status_name))
    # Add any remaining (unknown) columns
    for v in columns.values():
        ordered.append(v)

    return ordered


def _is_completion_status(status_name):
    """Check if a status name indicates a completed/finished state.

    Matches whole words to avoid false positives (e.g. 'Not Completed' won't match).
    """
    if not status_name:
        return False
    name_lower = status_name.lower().strip()
    completion_keywords = {"completed", "approved", "done", "finished", "closed"}
    words = set(name_lower.split())
    return bool(words & completion_keywords)


@frappe.whitelist()
def update_project_status(project, status):
    """Update a project's status (for Kanban drag-and-drop and inline status change).

    Only Team Update Admin, Team Update Team Leader, and System Manager can change status.
    When changing to a completion status (Completed, Approved, Done, etc.),
    automatically sets completion_date to today. Clears completion_date when
    moving away from a completion status.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles
    is_team_leader = "Team Update Team Leader" in roles
    is_team_member_only = "Team Update Team Member" in roles \
        and not is_admin and not is_team_leader
    is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) \
        and not is_admin

    if is_viewer or is_team_member_only:
        frappe.throw(_("You do not have permission to update project status."), frappe.PermissionError)

    # Validate status exists
    if not frappe.db.exists("Project Status", status):
        frappe.throw(_("Invalid status."))

    # Get the new status name to check if it's a completion status
    new_status_info = _get_status_info(status)
    new_is_completed = _is_completion_status(new_status_info["status_name"])

    doc = frappe.get_doc("Project", project)

    # Check if the previous status was a completion status
    old_status_name = ""
    if doc.status:
        old_info = _get_status_info(doc.status)
        old_status_name = old_info["status_name"]
    old_is_completed = _is_completion_status(old_status_name)

    # Auto-set or clear completion_date based on status change
    if new_is_completed and not old_is_completed:
        doc.completion_date = today()
    elif old_is_completed and not new_is_completed:
        doc.completion_date = None

    doc.status = status
    doc.save(ignore_permissions=True)

    frappe.db.commit()

    return {"success": True, "status_name": new_status_info["status_name"], "color": new_status_info["color"]}


# ---------------------------------------------------------------------------
# Activity Feed
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_project_activity(project):
    """Return unified activity feed for a project.

    Combines:
    - Frappe Comments (from the Comment doctype)
    - Project Updates (from child table)
    - Version change logs
    Returns a chronological list sorted by date (newest first).
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    activities = []

    # 1. Fetch comments from Frappe's Comment doctype
    try:
        comments = frappe.get_all("Comment",
            filters={
                "reference_doctype": "Project",
                "reference_name": project,
                "comment_type": ["in", ["Comment", "Info", "Assigned", "Unassigned"]],
            },
            fields=["name", "content", "comment_by", "comment_type", "creation"],
            order_by="creation desc",
            limit=50,
        )
        for c in comments:
            activities.append({
                "type": "comment",
                "subtype": c.comment_type or "Comment",
                "content": c.content,
                "author": c.comment_by,
                "date": str(c.creation),
                "timestamp": c.creation.timestamp() if hasattr(c.creation, "timestamp") else 0,
            })
    except Exception:
        pass

    # 2. Fetch project updates (child table)
    try:
        updates = frappe.get_all("Project Update",
            filters={"project": project},
            fields=["name", "update_title", "update_description", "updated_by", "update_date", "creation"],
            order_by="creation desc",
            limit=50,
        )
        for u in updates:
            activities.append({
                "type": "update",
                "subtype": "Update",
                "title": u.update_title,
                "content": u.update_description or "",
                "author": u.updated_by or "System",
                "date": str(u.update_date or u.creation),
                "timestamp": u.creation.timestamp() if hasattr(u.creation, "timestamp") else 0,
            })
    except Exception:
        pass

    # 3. Fetch version logs (tracked changes)
    try:
        versions = frappe.get_all("Version",
            filters={
                "ref_doctype": "Project",
                "docname": project,
            },
            fields=["name", "data", "modified_by", "creation"],
            order_by="creation desc",
            limit=50,
        )
        for v in versions:
            change_summary = _summarize_version(v.data)
            if change_summary:
                activities.append({
                    "type": "change",
                    "subtype": "Status Change" if "status" in str(v.data).lower() else "Change",
                    "content": change_summary,
                    "author": v.modified_by,
                    "date": str(v.creation),
                    "timestamp": v.creation.timestamp() if hasattr(v.creation, "timestamp") else 0,
                })
    except Exception:
        pass

    # Sort by timestamp descending (newest first)
    activities.sort(key=lambda a: a.get("timestamp", 0), reverse=True)

    return activities[:100]


def _summarize_version(data_json):
    """Extract a human-readable summary from a Version data JSON."""
    if not data_json:
        return ""
    try:
        data = json.loads(data_json) if isinstance(data_json, str) else data_json
        changed = data.get("changed", [])
        summaries = []
        for change in changed:
            if len(change) >= 3:
                field, old, new = change[0], change[1], change[2]
                if old != new:
                    summaries.append(f"{field}: {old or '(empty)'} \u2192 {new or '(empty)'}")
        if summaries:
            return "; ".join(summaries[:3])
        return ""
    except Exception:
        return ""


@frappe.whitelist()
def add_activity_comment(project, comment):
    """Add a comment to a project's activity feed using Frappe's built-in Comment doctype."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    if not comment or not comment.strip():
        frappe.throw(_("Comment cannot be empty."))

    doc = frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": "Project",
        "reference_name": project,
        "content": comment.strip(),
        "comment_by": frappe.utils.get_fullname(user) or user,
    })
    doc.insert(ignore_permissions=True)

    _notify_project_members(project, "New comment on project", comment.strip()[:100])

    frappe.db.commit()

    return {
        "success": True,
        "comment": {
            "name": doc.name,
            "content": doc.content,
            "author": doc.comment_by,
            "date": str(doc.creation),
        }
    }


@frappe.whitelist()
def add_activity_update(project, title, description=None):
    """Add a structured progress update to a project."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    if not title or not title.strip():
        frappe.throw(_("Update title cannot be empty."))

    doc = frappe.get_doc("Project", project)
    row = doc.append("project_updates", {
        "update_title": title.strip(),
        "update_description": description.strip() if description else "",
        "update_date": today(),
        "updated_by": frappe.utils.get_fullname(user) or user,
    })
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "update": {
            "name": row.name,
            "update_title": row.update_title,
            "update_description": row.update_description,
            "update_date": str(row.update_date),
            "updated_by": row.updated_by,
        }
    }


def _notify_project_members(project, subject, message):
    """Create notification log entries for project stakeholders."""
    try:
        owner = frappe.db.get_value("Project", project, "owner")
        recipients = set()
        if owner:
            recipients.add(owner)

        admins = frappe.get_all("Has Role",
            filters={"role": ["in", ["Team Update Admin", "System Manager"]]},
            pluck="parent"
        )
        for a in admins:
            recipients.add(a)

        for user in recipients:
            if user == frappe.session.user:
                continue
            try:
                nl = frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": subject[:140],
                    "email_content": message,
                    "for_user": user,
                    "type": "Alert",
                    "document_type": "Project",
                    "document_name": project,
                })
                nl.insert(ignore_permissions=True, ignore_links=True)
            except Exception:
                pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Time Tracking
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_time_logs(project):
    """Return time log entries for a project."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    logs = frappe.get_all("Project Time Log",
        filters={"project": project, "docstatus": ["<", 2]},
        fields=["name", "log_date", "hours", "description", "owner", "creation"],
        order_by="log_date desc, creation desc",
        limit=200,
    )

    total = sum(float(l.hours or 0) for l in logs)

    return {
        "logs": logs,
        "total_hours": round(total, 2),
    }


@frappe.whitelist()
def add_time_log(project, hours, description=None, log_date=None):
    """Add a time log entry for a project."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    try:
        hours_val = float(hours)
    except (TypeError, ValueError):
        frappe.throw(_("Hours must be a valid number."))

    if hours_val <= 0:
        frappe.throw(_("Hours must be greater than 0."))
    if hours_val > 24:
        frappe.throw(_("Hours cannot exceed 24 in a single entry."))

    if not log_date:
        log_date = today()

    doc = frappe.get_doc({
        "doctype": "Project Time Log",
        "project": project,
        "hours": hours_val,
        "description": (description or "").strip(),
        "log_date": log_date,
    })
    _set_resolved_name(doc, "TL-.YYYY.-.#####", "TL")

    try:
        doc.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        frappe.db.rollback()
        doc = frappe.get_doc({
            "doctype": "Project Time Log",
            "project": project,
            "hours": hours_val,
            "description": (description or "").strip(),
            "log_date": log_date,
        })
        doc.name = f"TL-{frappe.generate_hash(length=10)}"
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "log": {
            "name": doc.name,
            "log_date": str(doc.log_date),
            "hours": doc.hours,
            "description": doc.description,
            "owner": doc.owner,
        }
    }


@frappe.whitelist()
def delete_time_log(name):
    """Delete a time log entry."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    doc = frappe.get_doc("Project Time Log", name)

    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles
    if doc.owner != user and not is_admin:
        frappe.throw(_("You can only delete your own time log entries."), frappe.PermissionError)

    doc.delete(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True}


# ---------------------------------------------------------------------------
# Gantt Chart
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_gantt_data():
    """Return project data formatted for the Gantt chart view.

    Returns a dict with:
      - projects: list of project dicts with name, title, start, end, progress, status info, team
      - statuses: all project statuses for color coding
      - teams: all active teams
      - min_date: earliest start_date across projects
      - max_date: latest due_date across projects
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    base_filters, _is_admin = _get_base_filters(user)

    projects = frappe.get_all(
        "Project",
        fields=["name", "project_title", "status", "priority", "team", "start_date", "due_date", "completion_date", "creation"],
        filters=base_filters,
        order_by="start_date asc, due_date asc",
    )

    project_list = []
    min_date = None
    max_date = None
    today_date = date.today()

    for p in projects:
        # Resolve status info
        status_info = _get_status_info(p.status or "")

        # Calculate progress (0-100) based on completion_date
        progress = 0
        is_overdue = False
        if p.completion_date:
            progress = 100
        elif p.due_date:
            if isinstance(p.due_date, str):
                due = datetime.strptime(p.due_date, "%Y-%m-%d").date()
            else:
                due = p.due_date
            if due < today_date:
                is_overdue = True
            # Estimate progress based on time elapsed if we have start_date
            if p.start_date and not p.completion_date:
                if isinstance(p.start_date, str):
                    start = datetime.strptime(p.start_date, "%Y-%m-%d").date()
                else:
                    start = p.start_date
                total_days = (due - start).days
                if total_days > 0:
                    elapsed = (today_date - start).days
                    progress = min(max(round((elapsed / total_days) * 100), 5), 95)

        # Resolve team name
        team_name = ""
        if p.team:
            try:
                t = frappe.get_cached_doc("Team", p.team)
                team_name = t.team_name if hasattr(t, "team_name") else p.team
            except Exception:
                team_name = p.team

        start_str = str(p.start_date) if p.start_date else None
        due_str = str(p.due_date) if p.due_date else None

        # Track date range
        if start_str:
            if min_date is None or start_str < min_date:
                min_date = start_str
        if due_str:
            if max_date is None or due_str > max_date:
                max_date = due_str

        project_list.append({
            "name": p.name,
            "title": p.project_title,
            "start_date": start_str,
            "due_date": due_str,
            "completion_date": str(p.completion_date) if p.completion_date else None,
            "status": status_info["status_name"],
            "status_color": status_info["color"],
            "priority": p.priority or "Medium",
            "team": team_name,
            "team_raw": p.team or "",
            "progress": progress,
            "is_overdue": is_overdue,
        })

    # Get filter options
    statuses = frappe.get_all("Project Status", fields=["name", "status_name", "color"], order_by="status_name asc")
    teams = frappe.get_all("Team", fields=["name", "team_name"], filters={"is_active": 1}, order_by="team_name asc")

    return {
        "projects": project_list,
        "statuses": [{"name": s.status_name, "color": s.color or "#6b7280"} for s in statuses],
        "teams": [{"name": t.name, "team_name": t.team_name} for t in teams],
        "min_date": min_date,
        "max_date": max_date,
    }


# ---------------------------------------------------------------------------
# Milestone API
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_milestones():
    """Return all milestones for the Gantt chart view.

    Returns a list of milestone dicts with:
      - name, title, date, type, color, description, project
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    try:
        milestones = frappe.get_all("Project Milestone",
            fields=["name", "milestone_title", "milestone_date", "milestone_type", "color", "description", "project"],
            order_by="milestone_date asc",
        )

        result = []
        for m in milestones:
            result.append({
                "name": m.name,
                "title": m.milestone_title,
                "date": str(m.milestone_date) if m.milestone_date else None,
                "type": m.milestone_type or "Milestone",
                "color": m.color or "#f59e0b",
                "description": m.description or "",
                "project": m.project,
            })
        return result
    except Exception:
        # Doctype might not exist yet (before migrate), return empty
        return []


@frappe.whitelist()
def add_milestone():
    """Add a new milestone.

    Expects POST data with:
      - title (required)
      - date (required, YYYY-MM-DD)
      - milestone_type
      - color
      - description
      - project (optional, link to a project)
    """
    data = frappe.local.form_dict

    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    title = data.get("title")
    milestone_date = data.get("date")

    if not title:
        frappe.throw(_("Milestone title is required."))
    if not milestone_date:
        frappe.throw(_("Milestone date is required."))

    doc = frappe.get_doc({
        "doctype": "Project Milestone",
        "milestone_title": title.strip(),
        "milestone_date": milestone_date,
        "milestone_type": data.get("milestone_type") or "Milestone",
        "color": data.get("color") or "#f59e0b",
        "description": (data.get("description") or "").strip(),
        "project": data.get("project") or None,
    })
    _set_resolved_name(doc, "MS-.YYYY.-.#####", "MS")

    try:
        doc.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        frappe.db.rollback()
        doc = frappe.get_doc({
            "doctype": "Project Milestone",
            "milestone_title": title.strip(),
            "milestone_date": milestone_date,
            "milestone_type": data.get("milestone_type") or "Milestone",
            "color": data.get("color") or "#f59e0b",
            "description": (data.get("description") or "").strip(),
            "project": data.get("project") or None,
        })
        doc.name = f"MS-{frappe.generate_hash(length=10)}"
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "milestone": {
            "name": doc.name,
            "title": doc.milestone_title,
            "date": str(doc.milestone_date),
            "type": doc.milestone_type or "Milestone",
            "color": doc.color or "#f59e0b",
            "description": doc.description or "",
            "project": doc.project,
        }
    }


@frappe.whitelist()
def delete_milestone(name):
    """Delete a milestone."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    if not frappe.db.exists("Project Milestone", name):
        frappe.throw(_("Milestone not found."))

    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles

    doc = frappe.get_doc("Project Milestone", name)
    if doc.owner != user and not is_admin:
        frappe.throw(_("You can only delete your own milestones."), frappe.PermissionError)

    doc.delete(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True}


# ---------------------------------------------------------------------------
# Team Member Scorecard (KPI Tracking)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_member_scorecard():
    """Return team member scorecard with project completion stats.

    Query params:
      - period: 'week' | 'month' | 'year' (default 'month')
      - team: optional team filter (Team name)
      - offset: number of periods to offset (negative = past, positive = future)

    Returns scorecard data for each team member across the specified period.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)

    data = frappe.local.form_dict
    period = data.get("period", "month").lower()
    team_filter = data.get("team", "")
    try:
        offset = int(data.get("offset", 0))
    except (ValueError, TypeError):
        offset = 0

    if period not in ("week", "month", "year"):
        period = "month"

    roles = frappe.get_roles(user)
    is_admin = "System Manager" in roles or "Team Update Admin" in roles
    is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) and not is_admin

    # Calculate date range for the current period
    today_date = date.today()
    period_start, period_end, display_label, period_key = _get_period_range(today_date, period, offset)

    # Fetch all team members (active teams)
    team_members = []
    try:
        if team_filter:
            teams_data = frappe.get_all("Team",
                fields=["name", "team_name"],
                filters={"name": team_filter, "is_active": 1}
            )
        else:
            teams_data = frappe.get_all("Team",
                fields=["name", "team_name"],
                filters={"is_active": 1},
                order_by="team_name asc"
            )

        for team_doc in teams_data:
            # Fetch members of each team via the child table
            members = frappe.get_all("Team Member",
                fields=["user", "role_in_team"],
                filters={"parent": team_doc.name, "parenttype": "Team"}
            )
            for m in members:
                team_members.append({
                    "user": m.user,
                    "role": m.role_in_team or "Member",
                    "team_name": team_doc.team_name,
                    "team": team_doc.name,
                })
    except Exception as e:
        frappe.log_error(f"Error fetching team members: {str(e)}", "Scorecard")
        team_members = []

    # Deduplicate users across teams (a user can be in multiple teams)
    user_map = {}
    for tm in team_members:
        u = tm["user"]
        if u not in user_map:
            user_map[u] = {
                "user": u,
                "full_name": "",
                "teams": [],
                "completed": 0,
                "completed_projects": [],
                "team_names": set(),
            }
        user_map[u]["teams"].append(tm["team"])
        user_map[u]["team_names"].add(tm["team_name"])

    if not user_map:
        return {
            "scorecard": [],
            "period": period,
            "period_label": display_label,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "teams": _get_team_options(),
            "team_summary": {},
            "total_completed": 0,
        }

    # Resolve full names for all users
    user_emails = list(user_map.keys())
    user_fullnames = {}
    try:
        user_data = frappe.db.sql(
            """SELECT name, full_name FROM `tabUser`
             WHERE name IN %s""",
            [user_emails], as_dict=1
        )
        for ud in user_data:
            user_fullnames[ud.name] = ud.full_name or ud.name.split("@")[0]
    except Exception:
        for email in user_emails:
            user_fullnames[email] = email.split("@")[0]

    # Build filters for projects in the period
    all_teams = set()
    for um in user_map.values():
        for t in um["teams"]:
            all_teams.add(t)

    # Find all completion status names (Completed, Approved, Done, etc.)
    completion_status_names = []
    try:
        all_statuses = frappe.get_all("Project Status", fields=["name", "status_name"])
        for s in all_statuses:
            if _is_completion_status(s.status_name):
                completion_status_names.append(s.name)
    except Exception:
        pass

    # Get all completed projects for the teams in the period
    # Two sources:
    #   1) Projects with a completion_date set in the period
    #   2) Projects with a completion status AND modified in the period (fallback for status-only changes)
    completed_in_period = []
    try:
        if all_teams:
            team_list = list(all_teams)

            # Query 1: Projects with completion_date in the period
            by_date = frappe.db.sql(
                """SELECT name, project_title, owner, team, completion_date
                 FROM `tabProject`
                 WHERE team IN %s
                   AND completion_date >= %s
                   AND completion_date <= %s
                   AND completion_date IS NOT NULL
                   AND docstatus < 2
                 ORDER BY completion_date DESC""",
                [team_list, period_start, period_end],
                as_dict=1
            )
            completed_in_period = list(by_date)

            # Query 2: Projects with a completion status but no completion_date, modified in the period
            # Add one day to period_end for datetime comparison (modified is Datetime, not Date)
            modified_end = period_end + timedelta(days=1)
            if completion_status_names:
                by_status = frappe.db.sql(
                    """SELECT name, project_title, owner, team, completion_date
                     FROM `tabProject`
                     WHERE team IN %s
                       AND status IN %s
                       AND completion_date IS NULL
                       AND modified >= %s
                       AND modified < %s
                       AND docstatus < 2
                     ORDER BY modified DESC""",
                    [team_list, completion_status_names, period_start, modified_end],
                    as_dict=1
                )
                # Merge, avoiding duplicates (by name)
                seen_names = {p.name for p in completed_in_period}
                for p in by_status:
                    if p.name not in seen_names:
                        seen_names.add(p.name)
                        completed_in_period.append(p)

    except Exception as e:
        frappe.log_error(f"Error fetching completed projects: {str(e)}", "Scorecard")
        completed_in_period = []

    # Attribute projects to team members (by owner)
    for p in completed_in_period:
        owner = p.owner
        if owner in user_map:
            user_map[owner]["completed"] += 1
            user_map[owner]["completed_projects"].append({
                "name": p.name,
                "title": p.project_title,
                "completion_date": str(p.completion_date) if p.completion_date else None,
            })

    # Build team-level summary
    team_project_counts = {}
    for p in completed_in_period:
        team_key = p.team or "Unknown"
        if team_key not in team_project_counts:
            team_project_counts[team_key] = 0
        team_project_counts[team_key] += 1

    team_summary = {}
    for tm in team_members:
        t = tm["team"]
        if t not in team_summary:
            team_summary[t] = {
                "team_name": tm["team_name"],
                "completed": team_project_counts.get(t, 0),
                "member_count": 0,
            }
        team_summary[t]["member_count"] += 1

    # Add team names to team_summary keys
    team_summary_named = {}
    for t_key, t_val in team_summary.items():
        team_summary_named[t_val["team_name"]] = t_val

    # Build final sorted scorecard
    scorecard = []
    for u, um in user_map.items():
        full_name = user_fullnames.get(u, u.split("@")[0])
        team_list_str = ", ".join(sorted(um["team_names"]))
        scorecard.append({
            "user": u,
            "full_name": full_name,
            "teams": team_list_str,
            "role": um["teams"][0].get("role", "Member") if um["teams"] else "Member",
            "completed": um["completed"],
            "completed_projects": sorted(um["completed_projects"],
                key=lambda x: x.get("completion_date", ""), reverse=True),
        })

    # Sort by completed count descending (top performers first)
    scorecard.sort(key=lambda x: x["completed"], reverse=True)

    total_completed = sum(s["completed"] for s in scorecard)

    return {
        "scorecard": scorecard,
        "period": period,
        "period_label": display_label,
        "period_start": str(period_start),
        "period_end": str(period_end),
        "teams": _get_team_options(),
        "team_summary": team_summary_named,
        "total_completed": total_completed,
    }


def _get_period_range(base_date, period, offset=0):
    """Calculate the date range for a given period type and offset."""
    if period == "week":
        # Monday of the offset week
        target_date = base_date + timedelta(weeks=offset)
        start = target_date - timedelta(days=target_date.weekday())
        end = start + timedelta(days=6)
        label = start.strftime("%b %d") + " - " + end.strftime("%b %d, %Y")
        key = start.strftime("%Y-W%V")
        return start, end, label, key

    elif period == "month":
        target_date = date(base_date.year, base_date.month, 1)
        # Add offset months
        month = target_date.month - 1 + offset  # zero-based
        year = target_date.year + month // 12
        month = month % 12 + 1
        start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end = date(year, month, last_day)
        label = start.strftime("%B %Y")
        key = start.strftime("%Y-%m")
        return start, end, label, key

    else:  # year
        target_year = base_date.year + offset
        start = date(target_year, 1, 1)
        end = date(target_year, 12, 31)
        label = str(target_year)
        key = str(target_year)
        return start, end, label, key


def _get_team_options():
    """Return list of active teams for filter dropdown."""
    try:
        teams = frappe.get_all("Team",
            fields=["name", "team_name"],
            filters={"is_active": 1},
            order_by="team_name asc"
        )
        return [{"name": t.name, "team_name": t.team_name} for t in teams]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Reports & Analytics
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_reports():
    """Return comprehensive reports data for the Reports & Analytics page.

    Returns:
      - total_projects
      - status_summary: [{status, count, color}]
      - category_summary: [{category, count}]
      - team_summary: [{team, count}]
      - completed_projects: recent completed/approved projects
      - github_repos: linked GitHub repositories
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please log in to view reports."), frappe.PermissionError)

    try:
        base_filters = {}
        roles = frappe.get_roles(user)
        is_viewer = ("Team Update Viewer" in roles or "View-Only User" in roles) \
            and "System Manager" not in roles and "Team Update Admin" not in roles
        if is_viewer:
            approved = frappe.db.get_value("Project Status", {"status_name": "Approved"}, "name")
            if approved:
                base_filters["status"] = approved

        # Total projects
        total_projects = frappe.db.count("Project", filters=base_filters or None)

        # Status summary
        status_summary = []
        statuses = frappe.get_all("Project Status", fields=["name", "status_name", "color"], order_by="status_name asc")
        for s in statuses:
            filters = {**base_filters, "status": s.name} if base_filters else {"status": s.name}
            count = frappe.db.count("Project", filters=filters)
            if count:
                status_summary.append({
                    "status": s.status_name,
                    "count": count,
                    "color": s.color or "#6b7280",
                })

        if not status_summary:
            status_summary = []

        # Category summary
        category_summary = []
        categories = frappe.get_all("Project Category", fields=["name", "category_name"], order_by="category_name asc")
        for cat in categories:
            filters = {**base_filters, "project_category": cat.name} if base_filters else {"project_category": cat.name}
            count = frappe.db.count("Project", filters=filters)
            if count:
                category_summary.append({
                    "category": cat.category_name,
                    "count": count,
                })

        # Team summary
        team_summary = []
        teams = frappe.get_all("Team", fields=["name", "team_name"], filters={"is_active": 1}, order_by="team_name asc")
        for t in teams:
            filters = {**base_filters, "team": t.name} if base_filters else {"team": t.name}
            count = frappe.db.count("Project", filters=filters)
            if count:
                team_summary.append({
                    "team": t.team_name,
                    "count": count,
                })

        # Completed projects (recent 20)
        completed_projects = []
        completion_status_names = []
        all_s = frappe.get_all("Project Status", fields=["name", "status_name"])
        for s_obj in all_s:
            if _is_completion_status(s_obj.status_name):
                completion_status_names.append(s_obj.name)

        completed_q = frappe.db.sql(
            """SELECT name, project_title, team, status, priority, completion_date
             FROM `tabProject`
             WHERE status IN %s
               AND docstatus < 2
             ORDER BY COALESCE(completion_date, modified) DESC
             LIMIT 20""",
            [completion_status_names] if completion_status_names else [[""]],
            as_dict=1
        ) if completion_status_names else []

        for p in completed_q:
            team_name = ""
            if p.team:
                try:
                    td = frappe.get_cached_doc("Team", p.team)
                    team_name = td.team_name
                except Exception:
                    team_name = p.team
            completed_projects.append({
                "name": p.name,
                "project_title": p.project_title,
                "team": team_name,
                "priority": p.priority,
                "completion_date": str(p.completion_date) if p.completion_date else None,
            })

        # GitHub repositories
        github_repos = []
        try:
            github_repos = frappe.get_all(
                "GitHub Repository",
                fields=["name", "repository_name", "repository_url", "default_branch", "languages", "commit_hash"],
                order_by="creation desc",
                limit=20,
            )
        except Exception:
            github_repos = []

        return {
            "total_projects": total_projects,
            "status_summary": status_summary,
            "category_summary": category_summary,
            "team_summary": team_summary,
            "completed_projects": completed_projects,
            "github_repos": github_repos,
        }

    except Exception as e:
        frappe.log_error(
            message=f"get_reports failed: {str(e)}\n{frappe.get_traceback()}",
            title="Team Update Tool - get_reports Error"
        )
        frappe.throw(_("Failed to load reports: {0}").format(str(e)))
