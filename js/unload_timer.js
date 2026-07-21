/* eslint quotes:0 */
/* eslint prefer-spread:0 */
/* global LiteGraph */
/* eslint operator-linebreak:0 */

import { app } from "../../scripts/app.js";

async function set_unload_timer_secs(secs) {
	const url = '/unload_timer/secs';
	const userData = { secs };

	try {
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(userData)
		});

		// Check if the server returned a success status (200-299)
		if (!response.ok) {
			throw new Error(`HTTP error! Status: ${response.status}`);
		}

		const result = await response.json();
		console.log('Success:', result);
	} catch (error) {
		console.error('Error sending data:', error);
	}
}

const SETTING_CATEGORY_NAME = "Unload Timer";
const SETTING_SECTION_TIMER = "Timer";
const unloadTimerExt = {
	name: "Unload Timer",
	settings: [
		{
			id: `UnloadTimer.Secs`,
			name: "Seconds of idleness before unloading",
//			tooltip: "",
			type: "number",
			category: [SETTING_CATEGORY_NAME, SETTING_SECTION_TIMER, "Seconds of idleness before unloading VRAM"],

			defaultValue: 60*15,
			onChange: (...args) => {
				const secs = parseInt(args[0]);
				set_unload_timer_secs(secs);

				return null;
			},
		},
	],

	init() {
	},
};

app.registerExtension(unloadTimerExt);
