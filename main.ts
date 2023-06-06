import { Worker } from 'worker_threads';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { RemoteCache } from './RemoteCache.js';

import { discrete_window } from './rate_limiters.js';

const REQS_PER_SEC = 10;
const RATE_LIMIT_THRESHOLD = 5; // max requests per second to allow
const DURATION = 2; // seconds
const WINDOW_LENGTH_MS = 1000; // millisecond
const num_requests = DURATION * REQS_PER_SEC;
const req_interval_ms = 1000 / REQS_PER_SEC;
const cache = new RemoteCache();

function experiment(rate_limiter: Function, reqs_per_sec: number, threshold: number, duration: number, window_length?: number) {
	console.log('\x1b[1m\x1b[36mStarting experiment:\x1b[0m', rate_limiter.name);

	const start_time = new Date().getTime();
	const requester = new Worker(new URL('./requester.js', import.meta.url), {
		workerData: { reqs_per_sec: reqs_per_sec, duration: duration },
	});
	let data = {
		experiment: { rate_limiter: rate_limiter.name, reqs_per_sec: reqs_per_sec, threshold: threshold, duration: duration, window_length: window_length },
		plot: [],
	};

	requester.on('message', async (msg) => {
		let current_time = new Date().getTime() - start_time;


		let output: any;
		// check if rate_limiter() has a window_length parameter, by name
		if (window_length) {
			output = rate_limiter('global', threshold, window_length, cache);
		} else {
			output = rate_limiter('global', threshold, cache);
		}

		if (msg !== 'DONE') {
			console.log(msg, '·', '\x1b[33m' + current_time.toString().padStart(4, '0') + '\x1b[0mms ·', output);

			data.plot.push({ time: current_time, ...output });
		} else { // experiment is done

			// write dataset to JSON file
			let file_path = `./data/${rate_limiter.name}.json`;
			fs.writeFileSync(file_path, JSON.stringify(data));
			console.log(file_path + ' saved');
			cache.reset();

			// spawn python process
			const python = spawn('python', ['plot.py', file_path]);
		}
	});
}

experiment(discrete_window, REQS_PER_SEC, RATE_LIMIT_THRESHOLD, DURATION, WINDOW_LENGTH_MS);
