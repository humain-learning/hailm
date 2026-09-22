import frappe
from .api import send_aisensy_message
from .client import *
from datetime import datetime, timezone
from frappe.utils import getdate
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
	studentexam = get_nearest_exam("student", datetime.now().date())
	teacherexam = get_nearest_exam("teacher", datetime.now().date())

	student_recipients = build_recipient_list(studentexam, "student",True)
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",True)

	student_count = len(student_recipients)
	teacher_count = len(teacher_recipients)

	recipients = [
		*student_recipients,
		*teacher_recipients,
	]
	print(recipients)
	for recipient in recipients[:5]:
		template_params = _build_template_params(
			recipient,
			teacherexam,
			"general"
		)
		username = recipient.get("Name").replace("  ", " ")
		destination = "+919910491335"
		campaign_name = "Olympiad Thursday"
		send_aisensy_message(
			campaign_name=campaign_name,
			destination=destination,
			username=username,
			template_params=template_params
		)
		print(f"Sent message to {destination} for recipient {username}")

def saturday_olympiad_reminders():
	studentexam = get_nearest_exam("student", datetime.now().date())
	teacherexam = get_nearest_exam("teacher", datetime.now().date())

	student_recipients = build_recipient_list(studentexam, "student",True)
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",True)

	student_count = len(student_recipients)
	teacher_count = len(teacher_recipients)

	recipients = [
		*student_recipients,
		*teacher_recipients,
	]
	print(f"Total Recipients: {len(recipients)}")
	for recipient in recipients[:5]:
		template_params = _build_template_params(
			recipient,
			teacherexam,
			"mock"
		)
		username = recipient.get("Name").replace("  ", " ")
		destination = "+919910491335"
		campaign_name = "Olympiad Saturday"
		send_aisensy_message(
			campaign_name=campaign_name,
			destination=destination,
			username=username,
			template_params=template_params
		)
		print(f"Sent message to {destination} for recipient {username}")

def sunday_olympiad_reminders():
	studentexam = get_nearest_exam("student", datetime.now().date())
	teacherexam = get_nearest_exam("teacher", datetime.now().date())

	student_recipients = build_recipient_list(studentexam, "student",True)
	# student_recipients = []
	teacher_recipients = build_recipient_list(teacherexam, "teacher",True)

	student_count = len(student_recipients)
	teacher_count = len(teacher_recipients)

	recipients = [
		*student_recipients,
		*teacher_recipients,
	]
	print(f"Total Recipients: {len(recipients)}")
	for recipient in recipients[:5]:
		template_params = _build_template_params(
			recipient,
			teacherexam,
			""
		)
		username = recipient.get("Name").replace("  ", " ")
		destination = "+919910491335"
		campaign_name = "Olympiad Sunday"
		send_aisensy_message(
			campaign_name=campaign_name,
			destination=destination,
			username=username,
			template_params=template_params
		)
		print(f"Sent message to {destination} for recipient {username}")

def get_nearest_exam(role,date):
	date = getdate(date) if type(date) == str else date
	for key,value in EXAM_SLOTS[role].items():
		mockdate = getdate(value.get("mockdate"))
		if mockdate >= date:
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