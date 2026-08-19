from .client.admin import fetch_and_save_token
from .services import sync_registered_school_list, sync_all_school_data


# def hourly():
# 	fetch_and_save_token()

def hourly():
	sync_registered_school_list()

def daily():
	sync_all_school_data()