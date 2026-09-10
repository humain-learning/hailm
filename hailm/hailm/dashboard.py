import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Coalesce, Count, Date, DateFormat


def get_calls_by_day(from_date=None, to_date=None, user=None):
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	call_log = DocType("CRM Call Log")
	call_date = Coalesce(call_log.start_time, call_log.creation)
	query = (
		frappe.qb.from_(call_log)
		.select(
			DateFormat(call_date, "%Y-%m-%d").as_("date"),
			Count("*").as_("calls"),
		)
		.where(Date(call_date).between(from_date, to_date))
		.groupby(Date(call_date))
		.orderby(Date(call_date))
	)

	if user:
		query = query.where((call_log.caller == user) | (call_log.receiver == user))

	return {
		"data": query.run(as_dict=True),
		"title": _("Calls by day"),
		"subtitle": _("Daily CRM call activity"),
		"xAxis": {
			"title": _("Date"),
			"key": "date",
			"type": "time",
			"timeGrain": "day",
		},
		"yAxis": {"title": _("Calls")},
		"series": [{"name": "calls", "type": "line", "showDataPoints": True}],
	}