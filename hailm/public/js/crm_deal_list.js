frappe.listview_settings["CRM Deal"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Sync All School Data"), () => {
			frappe.call({
				method: "hailm.hailm.services.sync_all_school_data",
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