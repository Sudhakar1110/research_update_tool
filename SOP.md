# Team Update Tool — Standard Operating Procedure (SOP)

**App Name:** Team Update Tool  
**Version:** 1.0.0  
**Compatibility:** Frappe Framework v15+ / ERPNext v15+  
**Repository:** https://github.com/balaji-001-gif/team_update_tool.git  
**Document Version:** 2.2  
**Last Updated:** July 21, 2026

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [System Requirements](#2-system-requirements)
3. [Installation Procedure](#3-installation-procedure)
4. [User Roles & Responsibilities](#4-user-roles--responsibilities)
5. [Role Permissions Matrix](#5-role-permissions-matrix)
6. [Team Creation Process](#6-team-creation-process)
7. [Task Assignment Workflow](#7-task-assignment-workflow)
8. [Admin Task Creation & Assignment](#8-admin-task-creation--assignment)
9. [Team Leader Task Assignment](#9-team-leader-task-assignment)
10. [Team Member Task Completion](#10-team-member-task-completion)
11. [GitHub Repository & File Upload](#11-github-repository--file-upload)
12. [Screenshot & Documentation Upload](#12-screenshot--documentation-upload)
13. [Team Leader Review Process](#13-team-leader-review-process)
14. [Admin Approval Process](#14-admin-approval-process)
15. [Viewer Access](#15-viewer-access)
16. [Notification Flow](#16-notification-flow)
17. [Workspace Usage Guide](#17-workspace-usage-guide)
18. [Project Status Report](#18-project-status-report)
19. [Complete End-to-End Workflow](#19-complete-end-to-end-workflow)
20. [Troubleshooting](#20-troubleshooting)
21. [Backup & Restore](#21-backup--restore)
22. [Appendix: Doctype Reference](#22-appendix-doctype-reference)

---

## 1. Purpose & Scope

### 1.1 Purpose
The Team Update Tool enables role-based task management where:
- **Admins** create tasks, assign to Team Leaders, and provide final approval
- **Team Leaders** assign tasks to Team Members, monitor progress, and review completed work
- **Team Members** work on assigned tasks, upload GitHub repositories, screenshots, and documentation
- **Viewers** browse approved projects in read-only mode

### 1.2 Scope
This SOP covers:
- Installation and setup on a Frappe/ERPNext v15+ bench
- Configuration of teams, members, and notification recipients
- Complete task workflow: creation → assignment → completion → review → approval
- Role management: Admin, Team Leader, Team Member, Viewer
- Troubleshooting common issues

---

## 2. System Requirements

### 2.1 Software Requirements
| Component | Version |
|-----------|---------|
| Frappe Framework | v15.0.0 or higher |
| ERPNext | v15.0.0 or higher **(required)** |
| Python | 3.10 or higher |
| Node.js | 18.x or higher |
| MariaDB | 10.6 or higher |
| Redis | 6.x or higher |

### 2.2 Hardware Requirements (Minimum)
| Resource | Requirement |
|----------|-------------|
| CPU | 2 cores |
| RAM | 4 GB |
| Disk | 20 GB free space |

---

## 3. Installation Procedure

> **Prerequisite:** ERPNext v15+ must be installed on your site before installing Team Update Tool. If you haven't already:
> ```bash
> bench --site your-site-name install-app erpnext
> ```
> 
> The `required_apps` declaration in `hooks.py` ensures this is handled automatically when running `install-app team_update_tool`.

### 3.1 Get the App
```bash
cd ~/frappe-bench
bench get-app https://github.com/balaji-001-gif/team_update_tool.git
```

### 3.2 Install on a Site
```bash
bench --site your-site-name install-app team_update_tool
```

> This will automatically install ERPNext if it's not already present, then run the app's `after_install()` hook.

**What this does:**
- Executes the `install.py` module's `after_install()` hook, which:
  - Creates the **Team Update Tool** domain
  - Automatically creates four roles:
    - `Team Update Admin` — Full access
    - `Team Update Team Leader` — Can assign tasks, monitor, and review
    - `Team Update Team Member` — Can work on assigned tasks
    - `Team Update Viewer` — Read-only access
  - Syncs all doctype fixtures into the database
  - Reloads workspace content and notification definitions

> **Note:** The `install.py` file (`team_update_tool/install.py`) is the app's installation entry point. It runs automatically during `install-app` and handles all first-time setup. Do not remove or modify it unless you understand the full setup process.

### 3.3 Run Migration
```bash
bench --site your-site-name migrate
```

**What migration does:**
- Applies all registered patches in `patches.txt` in sequence
- The `rename_roles` patch (`team_update_tool.patches.rename_roles`) handles upgrading from older versions by:
  - Creating any missing new roles (`Team Update Admin`, `Team Update Team Leader`, `Team Update Team Member`, `Team Update Viewer`)
  - Copying DocType permissions from old roles to new roles
  - Transferring user assignments from old roles to new roles
  - Removing the legacy role names once migration is complete

### 3.4 Build Assets
```bash
bench build --app team_update_tool
```

### 3.5 Restart Bench
```bash
bench restart
```

### 3.6 Verify Installation
1. Log in to your Frappe site
2. You should see **Team Update Tool** in the Workspace dropdown
3. Click to open the workspace with shortcuts

---

## 4. User Roles & Responsibilities

### 4.1 Team Update Admin
| Attribute | Description |
|-----------|-------------|
| **Who** | Project Managers, IT Admins, Department Heads |
| **Can Do** | Create, edit, assign, reassign, approve, reject, and delete tasks |
| **Can Do** | Create and manage Teams and Team Leaders |
| **Can Do** | View all teams, projects, tasks, and users |
| **Can Do** | Manage user roles and permissions |
| **Can Do** | View all reports and dashboards |
| **Can Do** | Configure application settings |
| **UI Banner** | ⚙️ Admin - Full access to all tasks |

### 4.2 Team Update Team Leader
| Attribute | Description |
|-----------|-------------|
| **Who** | Team Leads, Senior Developers |
| **Can Do** | View tasks assigned by Admin |
| **Can Do** | Assign tasks to Team Members within their team |
| **Can Do** | Monitor task progress |
| **Can Do** | Review completed tasks |
| **Can Do** | Update task status |
| **Cannot** | Delete projects or modify system settings |
| **Cannot** | Modify approval fields |
| **UI Banner** | 👥 Team Leader - You can assign tasks and review work |

### 4.3 Team Update Team Member
| Attribute | Description |
|-----------|-------------|
| **Who** | Developers, Designers, QA Engineers |
| **Can Do** | View only the tasks assigned to them |
| **Can Do** | Update task progress and status |
| **Can Do** | Upload completed project files |
| **Can Do** | Upload GitHub repository links |
| **Can Do** | Upload project screenshots and documentation |
| **Can Do** | Mark tasks as completed |
| **Cannot** | Assign tasks to other users |
| **Cannot** | Change review or approval fields |
| **UI Banner** | 🔧 Team Member - You can update progress and upload files |

### 4.4 Team Update Viewer
| Attribute | Description |
|-----------|-------------|
| **Who** | Marketing, Stakeholders, Management |
| **Can Do** | View approved projects only |
| **Can Do** | View GitHub repositories, screenshots, documentation |
| **Can Do** | View reports |
| **Cannot** | Create, edit, assign, submit, cancel, delete, or modify any records |
| **UI Banner** | 👁 View Only Access - Editing is disabled |

---

## 5. Role Permissions Matrix

### 5.1 Team Project Update Permissions
| Permission | Admin | Team Leader | Team Member | Viewer |
|------------|-------|-------------|-------------|--------|
| Create | ✅ | ✅ | ✅ | ❌ |
| Read | ✅ | ✅ (own team) | ✅ (own tasks) | ✅ (approved only) |
| Write | ✅ | ✅ (own team tasks) | ✅ (own tasks) | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |
| Export | ✅ | ✅ | ✅ | ✅ |
| Print | ✅ | ✅ | ✅ | ✅ |
| Share | ✅ | ❌ | ❌ | ❌ |

### 5.2 Team Permissions
| Permission | Admin | Team Leader | Team Member | Viewer |
|------------|-------|-------------|-------------|--------|
| Create | ✅ | ❌ | ❌ | ❌ |
| Read | ✅ | ✅ | ✅ | ✅ |
| Write | ✅ | ❌ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |

### 5.3 Team Update Settings Permissions
| Permission | Admin | Team Leader | Team Member | Viewer |
|------------|-------|-------------|-------------|--------|
| Full Access | ✅ | ❌ | ❌ | ❌ |
| Read Only | ✅ | ✅ | ✅ | ✅ |

### 5.4 Permission Query Conditions (List View Visibility)
| Role | Can See |
|------|---------|
| Admin / System Manager | All records |
| Team Leader | Tasks where they are the `assigned_team_leader` |
| Team Member | Tasks where they are the `assigned_to` |
| Viewer | Only tasks with status = "Approved" |

---

## 6. Team Creation Process

### 6.1 Who Can Create Teams
Only **Team Update Admin** can create and manage teams.

### 6.2 Create a New Team
1. Go to **Team Update Tool > Teams**
2. Click **+ Add Team**
3. Fill in:
   - **Team Name:** Unique name (e.g., "Development Team")
   - **Team Type:** Select from options
   - **Team Lead:** Select a user (this user should have Team Leader role)
   - **Is Active:** Checked
   - **Description:** Optional
4. Add **Members** in the child table:
   - **User:** Select user
   - **Role in Team:** e.g., "Frontend Developer"
5. Save

### 6.3 Important Notes
- A user cannot be added more than once to the same team
- The Team Lead should be assigned the **Team Update Team Leader** role in their User record
- Team Members should be assigned the **Team Update Team Member** role

---

## 7. Task Assignment Workflow

### 7.1 Complete Workflow Diagram
```
Admin → Create Task → Assign to Team Leader
                          ↓
              Team Leader → Assign to Team Member
                          ↓
              Team Member → Work on Task
                          ↓
              Upload GitHub Repo, Screenshots, Files
                          ↓
              Team Member → Mark Task as Completed
                          ↓
              Team Leader → Review Task
                          ↓
              Admin → Approve or Reject
                          ↓
              Project Published (Viewers can see)
```

### 7.2 Status Flow
```
Draft → Assigned → In Progress → Completed → Under Review → Approved
                                                               ↓
                                                          Rejected
```

---

## 8. Admin Task Creation & Assignment

### 8.1 Who Can Do This
**Team Update Admin** only.

### 8.2 Create a New Task
1. Go to **Team Update Tool > New Task**
2. Fill in:
   | Field | Required | Description |
   |-------|----------|-------------|
   | Project Title | Yes | Name of the project/task |
   | Team | Yes | Select the team |
   | Project Type | No | Type of project |
   | Status | Yes | Default: "Draft" |
   | Priority | No | Low, Medium, High, Urgent |
   | Assigned Team Leader | Yes | Select the team leader |
   | Start Date | No | When work should begin |
   | Project Description | No | Detailed description |
   | Tags | No | Comma-separated tags |

3. When you select **Assigned Team Leader**:
   - The `assigned_by_admin` checkbox is automatically checked
   - The status changes from "Draft" to "Assigned"
   - The Team Leader receives a **notification**

4. Click **Save**

### 8.3 Notifications Triggered
- Team Leader receives in-app notification: "New Task Assigned: [Project Title]"
- Email notification sent if email is configured in settings

---

## 9. Team Leader Task Assignment

### 9.1 Who Can Do This
**Team Update Team Leader** (for tasks assigned to them by Admin).

### 9.2 Assign Task to Team Member
1. Open the task assigned to you (find it from **All Tasks** or **My Tasks**)
2. In the **Assigned To (Team Member)** field, select a team member
3. When you select **Assigned To**:
   - The `assigned_by_team_leader` checkbox is automatically checked
   - The status changes from "Assigned" to "In Progress"
   - The Team Member receives a **notification**
4. Save

### 9.3 Notifications Triggered
- Team Member receives: "New Task Assigned: [Project Title] (as Team Member)"
- Admin is notified of the assignment

---

## 10. Team Member Task Completion

### 10.1 Who Can Do This
**Team Update Team Member** (for tasks assigned to them).

### 10.2 Work on the Task
1. Open your assigned task from **All Tasks** or **My Tasks**
2. Update the following as you work:
   - **Progress (%)** — Update this as you make progress
   - **Project Description** — Detailed description of what was done
   - **Tags** — Comma-separated tags

### 10.3 Mark Task as Completed
When the task is complete:

**Method 1:** Set **Progress (%)** to **100** — status auto-changes to "Completed"

**Method 2:** Click the **"Mark 100% Complete"** button in the Actions menu

### 10.4 Before Marking Complete
Make sure you have uploaded:
- ✅ GitHub Repository URL (see Section 11)
- ✅ Project Screenshots (see Section 12)
- ✅ Project Files (if applicable)
- ✅ Documentation (if applicable)

### 10.5 Notifications Triggered
- Team Leader receives: "Task Completed: [Project Title]"
- Admin receives notification
- The Team Leader Review section becomes active

---

## 11. GitHub Repository & File Upload

### 11.1 Who Can Upload
**Team Update Team Member** on their assigned tasks.

### 11.2 Upload GitHub Repository
1. Open your assigned task
2. In the **Source Code & Links** section:
   - **GitHub Repository URL:** Enter the full URL (e.g., https://github.com/username/repo-name)
   - **Live / Demo URL:** Enter the demo URL if available

### 11.3 Upload Project Files
1. In the **Uploaded Project Files** section, click **+ Add Row**
2. Click **Attach** to upload files (zip, tar, or source files)
3. Add a **Description** for each file
4. Save

### 11.4 URL Validation
If the GitHub URL does not contain "github.com", a warning message appears. Double-check the URL.

---

## 12. Screenshot & Documentation Upload

### 12.1 Upload Screenshots
1. In the **Screenshots** section, click **+ Add Row**
2. Click **Attach** to upload an image
3. Add a **Caption** (e.g., "Dashboard view after implementation")
4. Select the **Type**:
   - Workflow
   - Dashboard
   - UI Screen
   - Database / ERD
   - Other
5. Repeat for multiple screenshots
6. Save

### 12.2 Supported Formats
- Images: JPG, PNG, GIF
- Max size: As configured in Frappe System Settings

---

## 13. Team Leader Review Process

### 13.1 Who Can Do This
**Team Update Team Leader** (for completed tasks in their team).

### 13.2 Review Completed Task
1. Open the completed task
2. Go to the **Team Leader Review** section
3. Review the work, screenshots, GitHub repo, and files
4. Set **Team Leader Review** to:
   - **Reviewed** — If everything looks good
   - **Changes Requested** — If changes are needed
5. Add **Review Remarks** with feedback

### 13.3 Mark as Reviewed
Click the **"Mark Reviewed"** button in the Actions menu. This:
- Sets the review date automatically
- Changes status to "Under Review"
- Notifies Admin

### 13.4 Notifications Triggered
- Admin receives: "Task Reviewed: [Project Title]"
- Admin can now Approve or Reject

---

## 14. Admin Approval Process

### 14.1 Who Can Do This
**Team Update Admin** only.

### 14.2 Approve or Reject Task
1. Open the task (status should be "Under Review" or "Completed")
2. Review the work, screenshots, GitHub repo, and Team Leader review

**To Approve:**
- Click **"Approve Task"** in the Actions menu
- Status changes to "Approved"
- Approval date is auto-set
- Approver name is auto-set

**To Reject:**
- Click **"Reject Task"** in the Actions menu
- Status changes to "Rejected"
- Add **Admin Remarks** explaining why

### 14.3 Notifications Triggered on Approval
- **Team Leader** receives: "Task Approved: [Project Title]"
- **Team Member** receives: "Task Approved: [Project Title]"
- **Viewers** can now see the project as it is published

### 14.4 Notifications Triggered on Rejection
- **Team Leader** receives: "Task Rejected: [Project Title]"
- **Team Member** receives: "Task Rejected: [Project Title]"

---

## 15. Viewer Access

### 15.1 Who Can Do This
**Team Update Viewer** role.

### 15.2 What Viewers Can See
- ✅ Only tasks with status = **"Approved"**
- ✅ GitHub repository URLs
- ✅ Screenshots (displayed inline)
- ✅ Uploaded files (downloadable)
- ✅ Project descriptions
- ✅ Team information
- ✅ Project Status Summary report

### 15.3 What Viewers CANNOT Do
- ❌ Create new tasks
- ❌ Edit any records
- ❌ Delete any records
- ❌ Assign tasks
- ❌ Review or approve tasks
- ❌ Access Team Update Settings

### 15.4 Viewer Experience
- A yellow banner shows: **"👁 View Only Access - Editing is disabled for your role"**
- All form fields are disabled
- No Save or Delete buttons
- Can still view GitHub links, demo links, screenshots, and files

### 15.5 List View
Viewers only see tasks with **status = "Approved"** in the list view. This is enforced by server-side permission query conditions.

---

## 16. Notification Flow

### 16.1 Complete Notification Map

| Event | Sender | Recipient(s) | Channel |
|-------|--------|--------------|---------|
| Task Created | System | All roles | In-app Notification |
| Task Assigned to Team Leader | Admin | Team Leader | In-app + Email (if enabled) |
| Task Assigned to Team Member | Team Leader | Team Member | In-app + Email (if enabled) |
| Progress Updated (> previous) | Team Member | Team Leader | In-app |
| Task Completed | Team Member | Team Leader + Admin | In-app + Email |
| Task Under Review | System | Admin | In-app |
| Task Reviewed | Team Leader | Admin | In-app |
| Task Approved | Admin | Team Leader + Team Member + Viewer | In-app + Email |
| Task Rejected | Admin | Team Leader + Team Member | In-app |

### 16.2 Notification Channels
| Channel | Description |
|---------|-------------|
| **In-App Notification** | Appears in the bell icon (Notification Log) in Frappe toolbar |
| **Email** | Sent if **Team Update Settings > Enable Email Notification** is checked |

### 16.3 Configure Email Notifications
1. Go to **Team Update Settings**
2. Check **Enable Email Notification**
3. Add recipients in **Notify Recipients** table
4. Save

### 16.4 Frappe Notification Doctypes
| Notification | Event | Recipients |
|-------------|-------|------------|
| New Project Uploaded | New Record | All roles |
| Project Completed | Status → Completed | Admin, Team Leader |
| Project Approved | Status → Approved | Team Leader, Team Member, Viewer |

---

## 17. Workspace Usage Guide

### 17.1 Accessing the Workspace
- **Method 1:** Click the **Team Update Tool** module in the workspace dropdown
- **Method 2:** Search "Team Update Tool" in the Awesome Bar (Ctrl+G)

### 17.2 Workspace Shortcuts
| Shortcut | Action | Who Can Use |
|----------|--------|-------------|
| **New Task** | Opens a new Team Project Update form | Admin, Team Leader, Team Member |
| **All Tasks** | Opens list of all tasks (filtered by role) | All |
| **My Tasks** | Opens list filtered to current user | All |
| **Teams** | Opens list of teams | Admin, Team Leader, Team Member, Viewer |
| **Project Status Summary** | Opens the task report | All |
| **Team Update Settings** | Opens settings | Admin only |

### 17.3 Awesome Bar Shortcuts
Type these in the Awesome Bar (Ctrl+G):
- `Team Project Update` → Opens list of tasks
- `Team` → Opens list of teams
- `Project Status Summary` → Opens the report
- `Team Update Settings` → Opens settings

---

## 18. Project Status Report

### 18.1 Accessing the Report
1. Go to **Team Update Tool > Project Status Summary**

### 18.2 Report Description
The **Project Status Summary** report shows all tasks with their current status, assignments, progress, and review status.

### 18.3 Report Columns
| Column | Description |
|--------|-------------|
| **Project** | Project title |
| **Team** | Team name |
| **Team Leader** | Assigned team leader |
| **Assigned To** | Assigned team member |
| **Status** | Current status (Draft, Assigned, In Progress, Completed, Under Review, Approved, Rejected) |
| **Priority** | Priority level |
| **Progress** | Progress percentage |
| **Review Status** | Team Leader review status |
| **Completion Date** | Date of completion |

### 18.4 Filters
| Filter | Description |
|--------|-------------|
| **Team** | Filter by team |
| **Assigned To** | Filter by assigned user |
| **Completed From** | Filter by completion start date |
| **Completed To** | Filter by completion end date |

---

## 19. Complete End-to-End Workflow

### 19.1 Step-by-Step Walkthrough

**Step 1: Admin creates a Team**
- Go to Teams → Create "Development Team"
- Add members
- Assign Team Lead

**Step 2: Admin assigns Roles**
- Go to Users → Edit user → Add role:
  - Team Lead user → `Team Update Team Leader`
  - Developer users → `Team Update Team Member`
  - Marketing users → `Team Update Viewer`

**Step 3: Admin creates a Task**
- Go to New Task
- Fill in project details
- Select Assigned Team Leader
- Save → Task is now "Assigned"
- Team Leader gets notification

**Step 4: Team Leader assigns to Team Member**
- Open the task
- Select Assigned To (Team Member)
- Save → Status changes to "In Progress"
- Team Member gets notification

**Step 5: Team Member works on Task**
- Update progress percentage
- Add description and tags
- Upload GitHub repo URL
- Upload screenshots
- Upload project files

**Step 6: Team Member completes Task**
- Set Progress to 100%
- Or click "Mark 100% Complete"
- Status changes to "Completed"
- Team Leader + Admin get notification

**Step 7: Team Leader reviews**
- Open completed task
- Review screenshots, GitHub, files
- Click "Mark Reviewed"
- Status changes to "Under Review"
- Admin gets notification

**Step 8: Admin approves**
- Open task (Under Review)
- Click "Approve Task"
- Status changes to "Approved"
- Team Leader, Team Member, Viewer get notification

**Step 9: Viewer views approved project**
- Open task list (sees only Approved tasks)
- View GitHub, screenshots, files
- Cannot edit anything

---

## 20. Troubleshooting

### 20.1 Installation Errors

**Error:** `setup.py` not found  
**Solution:** Use the latest version:
```bash
bench get-app https://github.com/balaji-001-gif/team_update_tool.git --overwrite
```

**Error:** Module not found  
**Solution:**
```bash
bench --site your-site install-app team_update_tool
bench --site your-site migrate
bench restart
```

### 20.2 Permission Errors

**Error:** "You have View Only access"  
**Cause:** User has Viewer role  
**Solution:** Assign appropriate role (Admin/Team Leader/Team Member) if editing is required

**Error:** "You can only update tasks assigned to you"  
**Cause:** Team Member trying to edit another's task  
**Solution:** Only edit tasks where you are the `assigned_to`

**Error:** "Only Team Update Admin can delete"  
**Cause:** Non-admin trying to delete  
**Solution:** Only Admin/System Manager can delete records

### 20.3 Workflow Issues

**Issue:** Team Leader cannot see tasks  
**Solution:** Ensure tasks have the Team Leader set as `assigned_team_leader`

**Issue:** Team Member cannot see tasks  
**Solution:** Ensure tasks have the Team Member set as `assigned_to`

**Issue:** Viewer sees no tasks  
**Solution:** Ensure tasks have status = "Approved"

**Issue:** Progress not updating  
**Solution:** Team Members can only update progress on their own assigned tasks

### 20.4 Notification Issues

**Issue:** Notifications not appearing  
**Solution:**
1. Check that background jobs are running: `bench doctor`
2. Check Notification Log in Frappe toolbar bell icon

**Issue:** Emails not sending  
**Solution:**
1. Verify email setup in System Settings
2. Check Team Update Settings > Enable Email Notification
3. Verify recipients have valid email addresses

### 20.5 Workspace Issues

**Issue:** Workspace not showing up  
**Solution:**
```bash
bench build --app team_update_tool
bench --site your-site migrate
bench restart
```

---

## 21. Backup & Restore

### 21.1 Backup the Site
```bash
bench --site your-site backup --with-files
```

### 21.2 Restore from Backup
```bash
bench --site your-site restore /path/to/backup/file
```

---

## 22. Appendix: Doctype Reference

### 22.1 Complete List of Doctypes
| Doctype | Type | Purpose |
|---------|------|---------|
| **Team** | Master | Stores team information |
| **Team Member** | Child Table | Users in a team |
| **Team Project Update** | Master | Task management with full workflow |
| **Project File** | Child Table | Uploaded project files |
| **Project Screenshot** | Child Table | Uploaded screenshots |
| **Team Update Settings** | Single | Global settings for notifications |
| **Notification Recipient** | Child Table | Users to notify |

### 22.2 Task Status Options
| Status | Description |
|--------|-------------|
| Draft | Initial state when Admin creates a task |
| Assigned | Admin has assigned to Team Leader |
| In Progress | Team Leader has assigned to Team Member |
| Completed | Team Member has finished work |
| Under Review | Team Leader is reviewing |
| Approved | Admin has approved (published) |
| Rejected | Admin has rejected (returned for changes) |

### 22.3 Reports
| Report | Type | Purpose |
|--------|------|---------|
| **Project Status Summary** | Script Report | Task list with assignments, progress, and review status |

### 22.4 Notifications
| Notification | Event | Document Type |
|-------------|-------|---------------|
| **New Project Uploaded** | New Record | Team Project Update |
| **Project Completed** | Status → Completed | Team Project Update |
| **Project Approved** | Status → Approved | Team Project Update |

### 22.5 Roles
| Role | Desk Access | Description |
|------|-------------|-------------|
| **Team Update Admin** | Yes | Full access (create, edit, delete, assign, approve) |
| **Team Update Team Leader** | Yes | Assign tasks to members, monitor, review |
| **Team Update Team Member** | Yes | Work on assigned tasks, upload files |
| **Team Update Viewer** | Yes | Read-only access to approved projects |

### 22.6 Permission Query Conditions
| Role | List View Visibility |
|------|---------------------|
| Admin / System Manager | All tasks |
| Team Leader | Tasks where assigned_team_leader = current user |
| Team Member | Tasks where assigned_to = current user |
| Viewer | Tasks where status = "Approved" |

---

## 23. Complete Fix Instructions (Troubleshooting Directory Rebuild)

If you encounter issues where DocTypes are not showing up correctly, or if you need to completely re-sync all DocTypes, follow these steps.

### 23.1 Pull Latest Changes
```bash
cd ~/frappe-bench-v15/apps/team_update_tool
git pull origin main
cd ../..
```

### 23.2 Delete All Old Doctype Records Using SQL

Run the bench console:
```bash
bench --site [your-site-name] console
```

Then paste this and press Enter:
```python
frappe.db.sql("""
DELETE FROM `tabDocType` WHERE name IN (
    'Team', 'Team Member', 'Technology', 'Project Category', 'Project Status',
    'Project', 'Project Update', 'Project Files', 'Project Screenshots', 'Project Technology',
    'GitHub Repository',
    'Project Summary Report', 'Team Activity Report', 'Completed Projects Report', 'GitHub Repository Report',
    'New Project Uploaded', 'Project Approved', 'Project Status Updated',
    'Team Update Tool'
)
""")
frappe.db.commit()
exit()
```

### 23.3 Migrate to Re-sync All Doctypes
```bash
bench --site [your-site-name] migrate
```

### 23.4 Restart
```bash
bench restart
```

### 23.5 Clear Browser Cache
Press **Ctrl+Shift+R** (or **Cmd+Shift+R** on Mac) in your browser.

### 23.6 Alternative: MySQL Direct Approach

If the bench console approach doesn't work, try running directly in MySQL:

```bash
mysql -u root -p [your_password] [sitename]
```

Then:
```sql
USE [databasename];
DELETE FROM `tabDocType` WHERE name IN (
    'Team', 'Team Member', 'Technology', 'Project Category', 'Project Status',
    'Project', 'Project Update', 'Project Files', 'Project Screenshots', 'Project Technology',
    'GitHub Repository',
    'Project Summary Report', 'Team Activity Report', 'Completed Projects Report', 'GitHub Repository Report',
    'New Project Uploaded', 'Project Approved', 'Project Status Updated',
    'Team Update Tool'
);
DELETE FROM `tabPropertySetter` WHERE doc_type IN (
    'Team', 'Team Member', 'Technology', 'Project Category', 'Project Status',
    'Project', 'Project Update', 'Project Files', 'Project Screenshots', 'Project Technology',
    'GitHub Repository',
    'Project Summary Report', 'Team Activity Report', 'Completed Projects Report', 'GitHub Repository Report',
    'New Project Uploaded', 'Project Approved', 'Project Status Updated',
    'Team Update Tool'
);
FLUSH TABLES;
EXIT;
```

Then run `bench --site [your-site-name] migrate`.

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.2 | July 21, 2026 | System | Added Section 23 with complete fix instructions for DocType re-sync |
| 2.1 | July 16, 2026 | System | Added install.py details, rename_roles migration patch notes, and updated role names throughout |
| 2.0 | July 7, 2026 | System | Complete rewrite for role-based task management workflow with 4 roles |
| 1.0 | July 7, 2026 | System | Initial SOP document created |

---

*End of SOP Document*
