import frappe
from html import escape
from .api import send_aisensy_message
from .client import *
from .olympiad_registrations import REGISTRATION_REPORT_RECIPIENTS
from datetime import datetime, timezone
from frappe.utils import getdate
from datetime import timedelta
from hailm.hailm.utils import normalize_mobile
EXAM_SLOTS = {
	"student": {
		"state_date_1": {
			"mockdate": "2026-08-30",
			"examdate": "2026-08-31",
			"3": {"batch_name": "","batch_id": ""},
			"4": {"batch_name": "","batch_id": ""},
			"5": {"batch_name": "","batch_id": ""},
			"6": {"batch_name": "","batch_id": ""},
			"7": {"batch_name": "","batch_id": ""},
			"8": {"batch_name": "","batch_id": ""},
			"9": {"batch_name": "","batch_id": ""},
			"10": {"batch_name": "","batch_id": ""},
			"11": {"batch_name": "","batch_id": ""},
			"12": {"batch_name": "","batch_id": ""}
		},
		"state_date_2": {
			"mockdate": "2026-09-26",
			"examdate": "2026-09-27",
			"3": {"batch_name": "Grade 3 27 Sep", "batch_id": "174026"},
			"4": {"batch_name": "Grade 4 27 Sep", "batch_id": "174027"},
			"5": {"batch_name": "Grade 5 27 Sep", "batch_id": "174028"},
			"6": {"batch_name": "Grade 6 27 Sep", "batch_id": "174029"},
			"7": {"batch_name": "Grade 7 27 Sep", "batch_id": "174030"},
			"8": {"batch_name": "Grade 8 27 Sep", "batch_id": "174031"},
			"9": {"batch_name": "Grade 9 27 Sep", "batch_id": "174032"},
			"10": {"batch_name": "Grade 10 27 Sep", "batch_id": "174033"},
			"11": {"batch_name": "Grade 11 27 Sep", "batch_id": "174034"},
			"12": {"batch_name": "Grade 12 27 Sep", "batch_id": "174035"}
		},
		"state_date_3": {
			"mockdate": "2026-10-03",
			"examdate": "2026-10-04",
			"3": {"batch_name": "Grade 3 4 Oct", "batch_id": "174036"},
			"4": {"batch_name": "Grade 4 4 Oct", "batch_id": "174037"},
			"5": {"batch_name": "Grade 5 4 Oct", "batch_id": "174038"},
			"6": {"batch_name": "Grade 6 4 Oct", "batch_id": "174039"},
			"7": {"batch_name": "Grade 7 4 Oct", "batch_id": "174040"},
			"8": {"batch_name": "Grade 8 4 Oct", "batch_id": "174041"},
			"9": {"batch_name": "Grade 9 4 Oct", "batch_id": "174042"},
			"10": {"batch_name": "Grade 10 4 Oct", "batch_id": "174043"},
			"11": {"batch_name": "Grade 11 4 Oct", "batch_id": "174044"},
			"12": {"batch_name": "Grade 12 4 Oct", "batch_id": "174045"}
		},
		"state_date_4": {
			"mockdate": "2026-10-10",
			"examdate": "2026-10-11",
			"3": {"batch_name": "Grade 3 11 Oct", "batch_id": "174046"},
			"4": {"batch_name": "Grade 4 11 Oct", "batch_id": "174047"},
			"5": {"batch_name": "Grade 5 11 Oct", "batch_id": "174048"},
			"6": {"batch_name": "Grade 6 11 Oct", "batch_id": "174049"},
			"7": {"batch_name": "Grade 7 11 Oct", "batch_id": "174050"},
			"8": {"batch_name": "Grade 8 11 Oct", "batch_id": "174051"},
			"9": {"batch_name": "Grade 9 11 Oct", "batch_id": "174052"},
			"10": {"batch_name": "Grade 10 11 Oct", "batch_id": "174053"},
			"11": {"batch_name": "Grade 11 11 Oct", "batch_id": "174054"},
			"12": {"batch_name": "Grade 12 11 Oct", "batch_id": "174055"}
		},
		"national": {
			"mockdate": "2026-10-17",
			"examdate": "2026-10-18",
			"3": {"batch_name": "Grade 3 18 Oct", "batch_id": "174056"},
			"4": {"batch_name": "Grade 4 18 Oct", "batch_id": "174057"},
			"5": {"batch_name": "Grade 5 18 Oct", "batch_id": "174058"},
			"6": {"batch_name": "Grade 6 18 Oct", "batch_id": "174059"},
			"7": {"batch_name": "Grade 7 18 Oct", "batch_id": "174060"},
			"8": {"batch_name": "Grade 8 18 Oct", "batch_id": "174061"},
			"9": {"batch_name": "Grade 9 18 Oct", "batch_id": "174062"},
			"10": {"batch_name": "Grade 10 18 Oct", "batch_id": "174063"},
			"11": {"batch_name": "Grade 11 18 Oct", "batch_id": "174064"},
			"12": {"batch_name": "Grade 12 18 Oct", "batch_id": "174065"}
		},
		"national_date_2": {
			"mockdate": "2026-10-24",
			"examdate": "2026-10-25",
			"3": {"batch_name": "Grade 3 25 Oct", "batch_id": "174066"},
			"4": {"batch_name": "Grade 4 25 Oct", "batch_id": "174067"},
			"5": {"batch_name": "Grade 5 25 Oct", "batch_id": "174068"},
			"6": {"batch_name": "Grade 6 25 Oct", "batch_id": "174069"},
			"7": {"batch_name": "Grade 7 25 Oct", "batch_id": "174070"},
			"8": {"batch_name": "Grade 8 25 Oct", "batch_id": "174071"},
			"9": {"batch_name": "Grade 9 25 Oct", "batch_id": "174072"},
			"10": {"batch_name": "Grade 10 25 Oct", "batch_id": "174073"},
			"11": {"batch_name": "Grade 11 25 Oct", "batch_id": "174074"},
			"12": {"batch_name": "Grade 12 25 Oct", "batch_id": "174075"}
		},
	},
	"teacher": {
		"state_date_1": {
			"mockdate": "2026-09-05",
			"examdate": "2026-09-06",
			"batch_name": "", 
			"batch_id": ""
		},
		"state_date_2": {
			"mockdate": "2026-10-3",
			"examdate": "2026-10-4",
			"batch_name": "Teacher 4 Oct", 
			"batch_id": "174076"
		},
		"national": {
			"mockdate": "2026-10-24",
			"examdate": "2026-10-25",
			"batch_name": "Teacher 25 Oct", 
			"batch_id": "174077"
		},
	}
}
 
def multipart_value(value):
	return (None, value) if value else (None,None)


# def test_reminders():
# 	# general_olympiad_reminders()
# 	# saturday_olympiad_reminders()
# 	sunday_olympiad_reminders()


def general_olympiad_reminders():
	studentexam = get_next_exam("student", datetime.now().date())
	teacherexam = get_next_exam("teacher", datetime.now().date())

	student_recipients = build_recipient_list(studentexam, "student",False) if studentexam else []
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",False) if teacherexam else []
	for recipient in student_recipients:
		recipient["exam"] = studentexam
	for recipient in teacher_recipients:
		recipient["exam"] = teacherexam

	recipients = [
		*student_recipients,
		*teacher_recipients,
	]
	failures = []
	stats = {"recipients_processed": len(recipients), "messages_sent": 0, "failures": 0}
	print("student true" if student_recipients else "student false")
	print("teacher true" if teacher_recipients else "teacher false")
	for recipient in recipients:
		campaign_name = "Olympiad Thursday"
		try:
			template_params = _build_template_params(recipient, recipient["exam"], "general")
			username = recipient.get("Name").replace("  ", " ")
			destination = normalize_mobile(recipient.get("MobileNo"))
			send_aisensy_message(
				campaign_name=campaign_name,
				destination=destination,
				username=username,
				template_params=template_params
			)
			print(template_params)
			stats["messages_sent"] += 1
			print(f"Sent message to {destination} for recipient {username}")
		except Exception as error:
			stats["failures"] += 1
			failures.append(_reminder_failure(recipient, campaign_name, error))
			frappe.log_error(title="Eklavvya Olympiad Reminder Failed", message=frappe.get_traceback())
	try:
		send_reminder_report("Thursday", failures, stats)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send Eklavvya Olympiad reminder report")

def saturday_olympiad_reminders():
	date = datetime.now().date()
	studentexam = get_today_exam("student", date)
	teacherexam = get_today_exam("teacher", date)

	student_recipients = build_recipient_list(studentexam, "student",False) if studentexam else []
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",False) if teacherexam else []
	for recipient in student_recipients:
		recipient["exam"] = studentexam
	for recipient in teacher_recipients:
		recipient["exam"] = teacherexam

	student_count = len(student_recipients)
	teacher_count = len(teacher_recipients)

	recipients = [
		*student_recipients,
		*teacher_recipients
	]
	failures = []
	stats = {"recipients_processed": len(recipients[:5]), "messages_sent": 0, "failures": 0}
	# print(f"Total Recipients: {len(recipients)}")
	print("student true" if student_recipients else "student false")
	print("teacher true" if teacher_recipients else "teacher false")
	for recipient in recipients:
		campaign_name = "Olympiad Saturday"
		try:
			template_params = _build_template_params(recipient, recipient["exam"], "mock")
			username = recipient.get("Name").replace("  ", " ")
			destination = normalize_mobile(recipient.get("MobileNo"))
			send_aisensy_message(
				campaign_name=campaign_name,
				destination=destination,
				username=username,
				template_params=template_params
			)
			print(template_params)
			stats["messages_sent"] += 1
			print(f"Sent message to {destination} for recipient {username}")
		except Exception as error:
			stats["failures"] += 1
			failures.append(_reminder_failure(recipient, campaign_name, error))
			frappe.log_error(title="Eklavvya Olympiad Reminder Failed", message=frappe.get_traceback())
	try:
		send_reminder_report("Saturday", failures, stats)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send Eklavvya Olympiad reminder report")

def sunday_olympiad_reminders():
	studentexam = get_today_exam("student", datetime.now().date())
	teacherexam = get_today_exam("teacher", datetime.now().date())

	student_recipients = build_recipient_list(studentexam, "student",False)if studentexam else []
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",False) if teacherexam else []
	for recipient in student_recipients:
		recipient["exam"] = studentexam
	for recipient in teacher_recipients:
		recipient["exam"] = teacherexam

	student_count = len(student_recipients)
	teacher_count = len(teacher_recipients)

	recipients = [
		*student_recipients,
		*teacher_recipients,
	]
	failures = []
	stats = {"recipients_processed": len(recipients[:5]), "messages_sent": 0, "failures": 0}
	print("student true" if student_recipients else "student false")
	print("teacher true" if teacher_recipients else "teacher false")
	for recipient in recipients:
		campaign_name = "Olympiad Sunday"
		try:
			template_params = _build_template_params(recipient, recipient["exam"], "")
			username = recipient.get("Name").replace("  ", " ")
			destination = normalize_mobile(recipient.get("MobileNo"))
			send_aisensy_message(
				campaign_name=campaign_name,
				destination=destination,
				username=username,
				template_params=template_params
			)
			print(template_params)
			stats["messages_sent"] += 1
			print(f"Sent message to {destination} for recipient {username}")
		except Exception as error:
			stats["failures"] += 1
			failures.append(_reminder_failure(recipient, campaign_name, error))
			frappe.log_error(title="Eklavvya Olympiad Reminder Failed", message=frappe.get_traceback())
	try:
		send_reminder_report("Sunday", failures, stats)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send Eklavvya Olympiad reminder report")


def _reminder_failure(recipient, campaign_name, error):
	return {
		"recipient": recipient.get("Name", ""),
		"role": recipient.get("role", ""),
		"roll_no": recipient.get("RollNo", ""),
		"campaign": campaign_name,
		"reason": str(error),
	}


def send_reminder_report(reminder_day, failures, stats):
	date = datetime.now(timezone.utc).strftime("%-d %b %Y")
	rows = "".join(
		f"<tr><td>{escape(str(failure['recipient']))}</td><td>{escape(str(failure['role']))}</td>"
		f"<td>{escape(str(failure['roll_no']))}</td><td>{escape(failure['campaign'])}</td>"
		f"<td>{escape(failure['reason'])}</td></tr>"
		for failure in failures
	)
	failure_table = (
		"<h3>Failures</h3><table border='1' cellpadding='6' cellspacing='0'>"
		"<tr><th>Recipient</th><th>Role</th><th>Roll No</th><th>Campaign</th><th>Reason</th></tr>"
		f"{rows}</table>"
		if failures
		else "<p>No reminder failures were recorded.</p>"
	)
	message = f"""
		<h2>Eklavvya Olympiad {reminder_day} reminder report</h2>
		<p>Recipients processed: {stats['recipients_processed']}<br>
		Messages sent: {stats['messages_sent']}<br>
		Failures: {stats['failures']}</p>
		{failure_table}
	"""
	frappe.sendmail(
		recipients=REGISTRATION_REPORT_RECIPIENTS,
		sender="schools@hailm.org",
		subject=f"Eklavvya Olympiad {reminder_day} Reminder Report - {date}",
		message=message,
	)

def get_next_exam(role,date):
	date = getdate(date) if type(date) == str else date
	for key,value in EXAM_SLOTS[role].items():
		mockdate = getdate(value.get("mockdate"))
		if mockdate >= date:
			if mockdate - date <= timedelta(days=4):
				return key
	return None

def get_weekend_exam(role, date):
	date = getdate(date) if type(date) == str else date
	weekend_start = date + timedelta(days=(5 - date.weekday()) % 7)
	weekend_end = weekend_start + timedelta(days=1)
	for key, value in EXAM_SLOTS[role].items():
		examdate = getdate(value.get("examdate"))
		if weekend_start <= examdate <= weekend_end:
			return key
	return None

def get_today_exam(role,date):
	date = getdate(date) if type(date) == str else date
	for key,value in EXAM_SLOTS[role].items():
		mockdate = getdate(value.get("mockdate"))
		examdate = getdate(value.get("examdate"))
		if mockdate == date or examdate == date:
			return key
	return None

def build_recipient_list(exam,role,test=False):
	recipients = []
	if role == "student":
		for key,value in EXAM_SLOTS[role][exam].items():
			if key in ["mockdate", "examdate"]:
				continue
			recipients.extend({**recipient, "role": role} for recipient in get_candidate_list_of_batch(value.get("batch_id") if not test else "174015"))
	if role == "teacher":
		for key,value in EXAM_SLOTS[role][exam].items():
			if key != "batch_id":
				continue
			recipients.extend({**recipient, "role": role} for recipient in get_candidate_list_of_batch(value if not test else "174015"))
	return recipients


def _build_template_params(recipient,exam,reminder_type:str):
	exam_type = "State" if "state" in exam else "National" if "national" in exam else ""
	if reminder_type == "general":
		return [
			recipient.get("Name").replace("  ", " ").title(),
			exam_type,
			getdate(EXAM_SLOTS[recipient["role"]][exam]["examdate"]).strftime("%-d %b %Y"),
			"10AM - 2PM",
			"60 Minutes",
			getdate(EXAM_SLOTS[recipient["role"]][exam]["mockdate"]).strftime("%-d %b %Y"),
			"10AM - 2PM",
			"30 Minutes",
			f"Username: {recipient["RollNo"]} | Password: {recipient["Password"]}"
		]

	if reminder_type in ["mock",""]:
		return [
			recipient.get("Name").replace("  ", " ").title(),
			f"{reminder_type.capitalize()} {exam_type} Olympiad".strip(),
			"10AM - 2PM",
			"30 Minutes" if reminder_type == "mock" else "60 Minutes",
			f"Username: {recipient['RollNo']} | Password: {recipient['Password']}",
			"https://olympiad.ailiteracymission.org",
			"https://hlai.in/2RXhG8",
			"Call or WhatsApp at +919028021962"
		]    