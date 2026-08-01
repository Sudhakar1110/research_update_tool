# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1

def get_context(context):
	context.title = _("Contact")
	context.no_header = 1
	context.no_breadcrumbs = 1
