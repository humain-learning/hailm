// Copyright (c) 2026, Raghav Kaul and contributors
// For license information, please see license.txt

frappe.ui.form.on("HAILM Token", {
	fetch_token: function (frm) {
		frappe.call({
			method:"hailm.hailm.client.admin.fetch_and_save_token",
			freeze: true,
			freeze_message: "Fetching Token",
			callback: function(r) {
				if (r.exc) {
					frappe.throw("An error occured, please check the error log for mroe details");
				}

				frm.reload_doc();
			}
		})
	}
});
