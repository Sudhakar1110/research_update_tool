# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class GitHubRepository(Document):
	def validate(self):
		self.validate_url()
		self.validate_duplicate_repository()
		if not self.repository_name:
			self.set_repository_name()

	def validate_url(self):
		if self.repository_url and "github.com" not in self.repository_url.lower():
			frappe.msgprint("The URL does not appear to be a valid GitHub URL. Please check.", alert=True, indicator="orange")

	def validate_duplicate_repository(self):
		if self.repository_url:
			filters = {"repository_url": self.repository_url}
			if not self.is_new():
				filters["name"] = ["!=", self.name]
			if frappe.db.exists("GitHub Repository", filters):
				frappe.throw("This GitHub repository URL already exists. Duplicate repositories are not allowed.")

	def set_repository_name(self):
		match = re.search(r"github\.com/([^/]+)/([^/]+)", self.repository_url)
		if match:
			self.repository_name = match.group(2).rstrip("/").replace(".git", "")


def validate_github_repository(doc, method=None):
	"""Hook called from doc_events. Fetches GitHub metadata."""
	if not doc.repository_url or not doc.is_new():
		return

	match = re.search(r"github\.com/([^/]+)/([^/]+)", doc.repository_url)
	if not match:
		return

	owner, repo_name = match.group(1), match.group(2).rstrip("/").replace(".git", "")

	try:
		import requests
		api = f"https://api.github.com/repos/{owner}/{repo_name}"
		headers = {}
		token = frappe.conf.get("github_api_token")
		if token:
			headers["Authorization"] = f"Bearer {token}"

		repo_data = requests.get(api, headers=headers, timeout=10).json()
		doc.default_branch = repo_data.get("default_branch", "main")
		doc.repository_name = doc.repository_name or repo_data.get("name", repo_name)

		branch_data = requests.get(f"{api}/branches/{doc.default_branch}", headers=headers, timeout=10).json()
		doc.commit_hash = branch_data.get("commit", {}).get("sha", "")

		langs = requests.get(f"{api}/languages", headers=headers, timeout=10).json()
		sorted_langs = sorted(langs.keys(), key=lambda k: langs[k], reverse=True)[:5]
		if sorted_langs:
			doc.languages = ", ".join(sorted_langs)

	except Exception as e:
		frappe.log_error(f"GitHub API error: {str(e)}", "GitHub Metadata")
