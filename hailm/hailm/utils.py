

def normalize_mobile(mobile):
	if not mobile:
		return ""
	if mobile.startswith("+91"):
		return mobile
	if mobile.startswith("91") and len(mobile) == 12:
		return f"+{mobile}"
	if len(mobile) == 10:
		return f"+91{mobile}"
	else:
		return ""