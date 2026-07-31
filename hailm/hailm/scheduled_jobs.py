from .client.admin import fetch_and_save_token
from .services import sync_registered_school_list


# def hourly():
# 	fetch_and_save_token()

def daily():
	sync_registered_school_list()