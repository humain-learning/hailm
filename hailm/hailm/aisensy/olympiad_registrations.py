import frappe
from html import escape
from datetime import timezone,datetime,timedelta
from hailm.hailm.client.admin import fetch_payments, fetch_user
from hailm.hailm.utils import normalize_mobile
from .api import create_new_candidate, EklavvyaExistingCandidateError, assign_to_batch, update_user_password

TEST_BATCHID = 174015
REGISTRATION_REPORT_RECIPIENTS = ["raghav.kaul@humainlearning.ai","abhi.s@humainlearning.ai","viren@humainlearning.ai", "ragini@humainlearning.ai", "parul.a@humainlearning.ai"]
EXAM_SLOTS = {
	"student": {
		"state_date_1": {
			"date": "2026-08-31",
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
			"batch_name": "", "batch_id": ""
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

def register_users():
	paid_users = fetch_and_consolidate_users()
	failures = []
	stats = {
		"users_processed": len(paid_users),
		"exam_registrations": 0,
		"created_candidates": 0,
		"existing_candidates": 0,
		"already_assigned": 0,
		"assignment_failures": 0,
	}
	print(paid_users)
	for user in paid_users:
		for exam_slot in user.get("examSlots") or []:
			if exam_slot == "state_date_1":
				continue
			stats["exam_registrations"] += 1
			batch_id = _resolve_batchID(user, exam_slot)
			candidate_id = None
			candidate_password = None
			assignment_attempted = False
			try:
				candidate = _build_creation_payload(user, exam_slot,test=False)
				response = create_new_candidate(candidate)
				candidate_id = response.get("Data", {}).get("CandidateID")
				candidate_password = response.get("Data", {}).get("Password")
				if not candidate_id:
					raise ValueError(response.get("Data", {}).get("Message") or response)
				stats["created_candidates"] += 1
				print("New User Created and assigned to batch")
			except EklavvyaExistingCandidateError as e:
				print("User already exists, assigning to batch")
				data = e.data
				candidate_data = data.get("Data") or {}
				candidate_id = candidate_data.get("CandidateID")
				candidate_password = candidate_data.get("Password")
				try:
					if not candidate_id:
						failures.append(_registration_failure(user, exam_slot, candidate_id, candidate_data.get("Message") or data))
					else:
						stats["existing_candidates"] += 1
						candidate = _build_assignment_payload(candidate_id, batch_id, test=False)
						assignment_attempted = True
						response = assign_to_batch(candidate)
						assignment_data = response.get("Data") or {}
						successful_ids = str(assignment_data.get("SuccessfulCandidateIDList") or "").replace(" ", "").split(",")
						unsuccessful_ids = str(assignment_data.get("UnsuccessfulCandidateList") or "").replace(" ", "").split(",")
						message = str(assignment_data.get("Message") or "")
						if str(candidate_id) in successful_ids:
							print("User assigned to batch successfully")
						elif str(candidate_id) in unsuccessful_ids and "active candidate(s) cannot be assigned" in message.lower():
							stats["already_assigned"] += 1
						else:
							stats["assignment_failures"] += 1
							failures.append(_registration_failure(user, exam_slot, candidate_id, message or response))
				except Exception as error:
					print("A: ",error)
					failures.append(_registration_failure(user, exam_slot, candidate_id, error))
					if assignment_attempted:
						stats["assignment_failures"] += 1
					frappe.log_error(title="Eklavvya Registration Failed", message=frappe.get_traceback())
			except Exception as error:
				print("B: ",error)
				failures.append(_registration_failure(user, exam_slot, candidate_id, error))
				if assignment_attempted:
					stats["assignment_failures"] += 1
				frappe.log_error(title="Eklavvya Registration Failed", message=frappe.get_traceback())
			finally:
				if candidate_password:
					update_user_password(user, candidate_password,batch_id)

	try:
		send_registration_report(failures, stats)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send Eklavvya registration report")


def _registration_failure(user, exam_slot, candidate_id, error):
	user_data = user.get("userData", {})
	return {
		"student": f"{user_data.get('firstname', '')} {user_data.get('lastname', '')}".strip(),
		"email": user_data.get("email", ""),
		"user_id": user_data.get("userId", ""),
		"roll_no": user_data.get("olympiadParticipantId", ""),
		"exam": exam_slot,
		"candidate_id": candidate_id or "",
		"reason": str(error),
	}


def send_registration_report(failures, stats):
	date = datetime.now(timezone.utc).strftime("%-d %b %Y")
	rows = "".join(
		f"<tr><td>{escape(failure['student'])}</td><td>{escape(str(failure['email']))}</td>"
		f"<td>{escape(str(failure['roll_no']))}</td><td>{escape(failure['exam'])}</td>"
		f"<td>{escape(str(failure['candidate_id']))}</td><td>{escape(failure['reason'])}</td></tr>"
		for failure in failures
	)
	failure_table = (
		"<h3>Failures</h3><table border='1' cellpadding='6' cellspacing='0'>"
		"<tr><th>Student</th><th>Email</th><th>Roll No</th><th>Exam</th>"
		f"<th>Candidate ID</th><th>Reason</th></tr>{rows}</table>"
		if failures
		else "<p>No registration failures were recorded.</p>"
	)
	message = f"""
		<h2>Eklavvya daily registration</h2>
		<p>Users processed: {stats['users_processed']}<br>
		Exam registrations: {stats['exam_registrations']}<br>
		Created candidates: {stats['created_candidates']}<br>
		Existing candidates: {stats['existing_candidates']}<br>
		Already assigned: {stats['already_assigned']}<br>
		Assignment failures: {stats['assignment_failures']}</p>
		{failure_table}
		<p>{'The following registrations could not be completed automatically and require manual registration in Eklavvya.' if failures else 'All registrations were completed automatically.'}</p>
	"""
	frappe.sendmail(
		recipients=REGISTRATION_REPORT_RECIPIENTS,
		sender="schools@hailm.org",
		subject=f"Eklavvya Olympiad Registration Report - {date}",
		message=message,
	)


	
def fetch_and_consolidate_users():
	yest = datetime.now(timezone.utc) - timedelta(days=1)
	# today = datetime.now(timezone.utc)
	payments = fetch_payments(yest.date(), yest.date(), status="paid")
	unique_users = {}

	for payment in payments:
		user_id = payment.get("userId")
		user = fetch_user(user_id)
		print(f"fetched user {user_id}")
		payment["beneficiary"]["mobile"] = normalize_mobile(user.get("phone")).removeprefix("+91")
		payment["beneficiary"]["olympiadParticipantId"] = user.get("olympiadParticipantId")
		payment["beneficiary"]["class"]= str(user.get("classLevel"))
		payment["beneficiary"]["firstname"] = user.get("firstName")
		payment["beneficiary"]["lastname"] = user.get("lastName")

		if user_id in unique_users.keys():
			unique_users[user_id]["examSlots"].extend(payment.get("examSlots", []))
		else:
			unique_users[user_id] = {
				**payment,
			}

	return [
		{
			"userData": user["beneficiary"],
			"examSlots": user.get("examSlots", []),   
		}
		for user in unique_users.values()
	]

def multipart_value(value):
	return (None, value) if value else (None,None)


def _build_creation_payload(user:dict,exam_slot:str,test=False):
	payload = {
		"FirstName": multipart_value(user["userData"].get("firstname")),
		"LastName": multipart_value(user["userData"].get("lastname")),
		"MobileNo": multipart_value(user["userData"].get("mobile")),
		# "Class": multipart_value(user["userData"].get("class")),
		"RollNo": multipart_value(user["userData"].get("olympiadParticipantId")),
		"BatchID": multipart_value(_resolve_batchID(user, exam_slot)) if not test else (None,TEST_BATCHID),
	}

	if not (email:= user["userData"]["email"]).endswith(("dummy.org","ailiteracymission.org")):
		payload["EmailID"] = multipart_value(email)
	return payload

def _build_assignment_payload(candidate_id:str,batch_id:str,test=False):
	payload = {
		"CandidateIDList": multipart_value(candidate_id),
		"BatchID": multipart_value(batch_id) if not test else (None,TEST_BATCHID),
	}
	return payload

def _resolve_batchID(user, exam_slot):
	role = user["userData"].get("role")
	if role == "student":
		return EXAM_SLOTS[role][exam_slot][user["userData"]["class"]]["batch_id"]
	elif role == "teacher":
		return EXAM_SLOTS[role][exam_slot]["batch_id"]
