app_name = "hailm"
app_title = "HAILM"
app_publisher = "Raghav Kaul"
app_description = "Custom App for Humain AI Literacy Mission"
app_email = "raghav.kaul@humainlearning.ai"
app_license = "mit"

# Apps
# ------------------

required_apps = ["crm"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "hailm",
		"logo": "/assets/hailm/logo.png",
		"title": "HAILM",
		"route": "/app/hailm",
		# "has_permission": "hailm.api.permission.has_app_permission"
	}
]
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["dt", "not in", ["Marketing Campaign", "Web Form Field"]],
			["options", "not in", ["Marketing Campaign"]],
			["is_system_generated", "=", 0],
		],
    },
    "Property Setter",
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hailm/css/hailm.css"
# app_include_js = "/assets/hailm/js/crm_deal_list.js"

# include js, css files in header of web template
# web_include_css = "/assets/hailm/css/hailm.css"
# web_include_js = "/assets/hailm/js/hailm.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hailm/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
	"CRM Deal" : "public/js/crm_deal_list.js",
	"User Analytics" : "public/js/user_analytics_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hailm/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hailm.utils.jinja_methods",
# 	"filters": "hailm.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hailm.install.before_install"
after_install = "hailm.setup.install.after_install"
after_migrate = "hailm.setup.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "hailm.uninstall.before_uninstall"
# after_uninstall = "hailm.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hailm.utils.before_app_install"
# after_app_install = "hailm.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hailm.utils.before_app_uninstall"
# after_app_uninstall = "hailm.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "hailm.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hailm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"CRM Deal": {
		"validate": "hailm.hailm.deal_hooks.validate",
		"before_save": "hailm.hailm.deal_hooks.before_save",
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"hailm.tasks.all"
	# ],
	"hourly": [
		"hailm.hailm.scheduled_jobs.hourly",
		"hailm.hailm.aisensy.payment_reminders.initial_dropped_payment_reminder"
	],
	"daily": [
		"hailm.hailm.scheduled_jobs.daily"
	],
	# "weekly": [
	# 	"hailm.tasks.weekly"
	# ],
	# "monthly": [
	# 	"hailm.tasks.monthly"
	# ],
	"cron": {
        "*/45 * * * *": [
            "hailm.hailm.client.admin.fetch_and_save_token",
        ],
		# "0 8 * * *": [
		# 	"hailm.hailm.scheduled_jobs.daily_report"
		# ]
		"0 18 * * *": [
			"hailm.hailm.aisensy.payment_reminders.daily_dropped_payment_reminders"
		]
    }
}

# Testing
# -------

# before_tests = "hailm.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "hailm.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"crm.api.dashboard.get_dashboard": "hailm.hailm.overrides.whitelisted.get_dashboard",
	"crm.fcrm.doctype.crm_deal.crm_deal.create_deal":
		"hailm.hailm.overrides.whitelisted.create_deal",
	"crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal":
		"hailm.hailm.overrides.whitelisted.convert_to_deal",
}

crm_dashboard_charts = {
	"axis_chart": [
		{
			"label": "Calls by Day",
			"value": "calls_by_day",
			"resolver": "hailm.hailm.dashboard.get_calls_by_day",
		}
	]
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hailm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hailm.utils.before_request"]
# after_request = ["hailm.utils.after_request"]

# Job Events
# ----------
# before_job = ["hailm.utils.before_job"]
# after_job = ["hailm.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hailm.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

