frappe.listview_settings["CRM Deal"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Sync Registered Schools"), () => {
			frappe.call({
				method: "hailm.hailm.services.sync_registered_school_list",
				args: {
					from_scheduler: false,
				},
				freeze: true,
				freeze_message: __("Starting school sync..."),
				callback: (r) => {
					if (!r.exc) {
						frappe.msgprint({
							title: __("Sync Started"),
							message: __(
								"Syncing started in background. Check back after 2 minutes."
							),
							indicator: "green",
						});
					}
				},
			});
		});
	},
};