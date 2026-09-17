import frappe
from datetime import timezone,datetime,timedelta
from hailm.hailm.client.admin import fetch_payments, fetch_user
from hailm.hailm.utils import normalize_mobile

EXAM_SLOTS = {
	"student": {
		"state_date_1": {
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
		"state_date_1": {"batch_name": "", "batch_id": ""},
		"state_date_2": {"batch_name": "Teacher 4 Oct", "batch_id": "174076"},
		"national": {"batch_name": "Teacher 25 Oct", "batch_id": "174077"},
	}
}

def register_user():
	paid_users = fetch_and_consolidate_users()
	for user in paid_users:
		for exam_slot in user.get("examSlots"):
			batch_id = evaluate_batchID(user, exam_slot)
			print(f"User: {user['userData'].get('firstname')} {user['userData'].get('lastname')}, Exam Slot: {exam_slot}, Batch ID: {batch_id}")
	
def fetch_and_consolidate_users():
	yest = datetime.now(timezone.utc) - timedelta(days=1)
	payments = fetch_payments(yest.date(), yest.date(), status="paid")
	unique_users = {}

	for payment in payments:
		user_id = payment.get("userId")
		user = fetch_user(user_id)
		payment["beneficiary"]["mobile"] = normalize_mobile(user.get("phone"))
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
	return (None, value)


def _build_payment_payload(user,exam_slot):
	payload = {
		"FirstName": multipart_value(user["userData"].get("firstname")),
		"LastName": multipart_value(user["userData"].get("lastname")),
		"MobileNo": multipart_value(user["userData"].get("mobile")),
		"Email": multipart_value(user["userData"].get("email") if user["userData"].get("email").endswith(("dummy.org","ailiteracymission.org")) else ""),
		"Class": multipart_value(user["userData"].get("class")),
		"RollNo": multipart_value(user["userData"].get("olympiadParticipantId")),
	}

def evaluate_batchID(user, exam_slot):
	role = user["userData"].get("role")
	if role == "student":
		return EXAM_SLOTS[role][exam_slot][user["userData"]["class"]]["batch_id"]
	elif role == "teacher":
		return EXAM_SLOTS[role][exam_slot]["batch_id"]

	