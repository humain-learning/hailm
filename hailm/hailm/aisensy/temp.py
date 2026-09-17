import pandas as pd

data = pd.read_csv("eklavvya-batch-ids.csv")

exams_slots = {
	"student": {}
}
exam = exams_slots["student"]

slot_names = ["state_date_2","state_date_3","state_date_4","national","national_2"]

for slot_name in slot_names:
	exam[slot_name] = {}
	
	for _, row in data.iterrows():
		exam