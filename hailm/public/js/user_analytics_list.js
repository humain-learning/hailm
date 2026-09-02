frappe.listview_settings["User Analytics"] = {
	get_indicator(doc) {
		if (doc.status === "active") {
			return ["active", "green"];
		}
		if (doc.status === "inactive") {
			return ["inactive", "yellow"];
		}
		if (doc.status === "suspended") {
			return ["disabled", "red"];
		}

		return [doc.status, "gray"];
	},

	formatters: {
        role(value) {
            const colors = {
                Student: "pink",
                Teacher: "blue",
                Principal: "green",
                "School Admin": "green"
            };

            return `<span class="indicator-pill ${colors[value] || "gray"}">
                <span class="indicator-pill-dot"></span>
                ${frappe.utils.escape_html(value)}
            </span>`;
        },
		state(value) {
            return frappe.utils.escape_html(value || "");
        }
	},
	onload(listview) {
		listview.page.wrapper
			.find(".filter-selector")
			.addClass("hidden");
		listview.page.wrapper
            .find('[data-fieldname="name"], [data-fieldname="full_name"]')
            .closest(".form-group")
            .addClass("hidden");
		listview.page.add_inner_button("Export Verified Phones", () => {
			open_url_post(
				"/api/method/hailm.hailm.doctype.user_analytics.user_analytics.export_users",
				{ filters: JSON.stringify(listview.get_filters_for_args()) }
			);
		});

		if (typeof listview.get_count_str === "function") {
			const original = listview.get_count_str.bind(listview);
			listview.get_count_str = async function () {
				const str = await original();
				let exact = null;

				const shortened = str.replace(/[\d,]{6,}/g, (match) => {
					const n = parseInt(match.replace(/,/g, ""), 10);
					if (isNaN(n) || n < 100000) return match;
					exact = match;
					return Math.floor(n / 100000) + " Lakh+";
				});

				// title is set after render, since this returns a plain string
				setTimeout(() => {
					const el = listview.$result
						? listview.$result.find(".list-count")
						: listview.page.wrapper.find(".list-count");
					if (exact) {
						el.attr("title", `${exact} total`);
					} else {
						el.removeAttr("title");
					}
				}, 0);

				return shortened;
			};
		}

		const fromDeal = frappe.utils.get_url_arg("from_deal");
		if (fromDeal) {
			listview.page.add_menu_item(__("Back to Deal"), () => {
				window.location.href = `/crm/deals/${encodeURIComponent(fromDeal)}`;
			});
		}
	},
	
}