from .client.admin import fetch_and_save_token
from .services import sync_registered_school_list, sync_all_school_data
import frappe
from frappe.utils.csvutils import to_csv
from frappe.utils import today, add_to_date, now_datetime



def hourly():
	sync_registered_school_list()

def daily():
	sync_all_school_data()


def daily_report():

	cumulative_progress_report_file = generate_cumulative_report()
	# print("cumulative report generated")
	table = generate_daily_new_schools()
	# print("daily report generated")
	frappe.sendmail(
		recipients=[
			"manit@humainlearning.ai",
			"amit@eduxa.ai",
			"viren@humainlearning.ai",
			"raghav.kaul@humainlearning.ai",
			"rajni.t@humainlearning.ai"
			"ragini@humainlearning.ai"
		],
		sender="schools@hailm.org",
		subject= f"Daily School Progress Report - {today()}",
		message = f"""
			<div style="
				font-family: Arial, sans-serif;
				font-size: 14px;
				color: #333;
				line-height: 1.5;
			">

				<h2 style="margin-bottom: 16px;">
					Daily School Progress Report
				</h2>

				<p>
					Please find the cumulative progress attached below.
				</p>

				<h3 style="margin-top: 24px; margin-bottom: 12px;">
					Schools Joined in the Last 24 Hours
				</h3>

				{table}

			</div>
		""",
		attachments=[
			{
				"fname": f"School Progress Report - {today()}.csv",
				"fcontent": cumulative_progress_report_file,
			}
		],
	)
	# print("mail queued")
	return 

def _convert_to_headers(fieldnames:list):
	headers = fieldnames.copy()

	return [header.removeprefix("custom_").replace("_"," ").title() for header in headers]

	# file_doc = frappe.get_doc({
	# 	"doctype": "File",
	# 	"file_name" : f"School Progress Report - {frappe.utils.today()}",
	# 	"content": file,
	# 	"is_private" : 0
	# }).insert(ignore_permissions=True)

	# file_doc.reload()


def generate_cumulative_report():
	COLUMNS = [
		"custom_school_id",
		"organization_name",
		"custom_address",
		"custom_student_strength",
		"custom_student_count",
		"custom_student_percentage",
		"custom_student_logged_in",
		"custom_student_active_percent",
		"custom_student_foundational_enrolled",
		"custom_student_foundational_completed",
		"custom_student_intermediate_enrolled",
		"custom_student_intermediate_completed",
		"custom_student_advanced_enrolled",
		"custom_student_advanced_completed",
		"custom_student_state_1_olympiad_purchases",
		"custom_student_state_2_olympiad_purchases",
		"custom_student_national_olympiad_purchases",
		"custom_teacher_strength",
		"custom_teacher_count",
		"custom_teacher_percentage",
		"custom_teacher_logged_in",
		"custom_teacher_active_percent",
		"custom_teacher_foundational_enrolled",
		"custom_teacher_foundational_completed",
		"custom_teacher_intermediate_enrolled",
		"custom_teacher_intermediate_completed",
		"custom_teacher_advanced_enrolled",
		"custom_teacher_advanced_completed",
		"custom_teacher_state_1_olympiad_purchases",
		"custom_teacher_state_2_olympiad_purchases",
		"custom_teacher_national_olympiad_purchases",
	]

	rows = frappe.get_all("CRM Deal", fields=COLUMNS, filters={"status":["!=", "Junk"]}, order_by="creation desc", as_list=True)

	headers = _convert_to_headers(fieldnames=COLUMNS)

	data = [headers,*rows]

	return to_csv(data).encode("utf-8")

def _table_to_html(headers, fieldnames, rows):
	html = """
	<table style="
		border-collapse: collapse;
		width: 100%;
		font-family: Arial, sans-serif;
		font-size: 14px;
	">
		<thead>
			<tr>
	"""

	for header in headers:
		html += f"""
				<th style="
					border: 1px solid #ddd;
					padding: 8px;
					text-align: left;
					background-color: #f5f5f5;
				">{header}</th>
		"""

	html += """
			</tr>
		</thead>
		<tbody>
	"""

	for row in rows:
		html += "<tr>"

		for fieldname in fieldnames:
			value = row.get(fieldname) or ""

			html += f"""
				<td style="
					border: 1px solid #ddd;
					padding: 8px;
				">{value}</td>
			"""

		html += "</tr>"

	html += """
		</tbody>
	</table>
	"""

	return html


def generate_daily_new_schools():
	COLUMNS = [
		"custom_school_id",
		"organization_name",
		"custom_address",
		"custom_kyc_status"
	]

	end = now_datetime()
	start = add_to_date(end,hours=-24)

	new_schools = frappe.get_all("CRM Deal", filters={"creation": ["between", [start,end]]}, fields=COLUMNS)
	
	headers = _convert_to_headers(fieldnames=COLUMNS)

	return _table_to_html(
		headers=headers,
		fieldnames=COLUMNS,
		rows=new_schools,
	)