import { workerData, parentPort } from "worker_threads";
const delay = (time: number) => new Promise((res) => setTimeout(res, time));

const { reqs_per_sec, duration } = workerData;
const num_requests = reqs_per_sec * duration;
const req_interval_ms = 1000 / reqs_per_sec;

console.log(`${num_requests} reqs in ${duration} seconds: ${reqs_per_sec} req/s -- ${req_interval_ms} ms/req`);

for (let index = 1; index <= num_requests; index++) {
  parentPort.postMessage(`req${index.toString().padStart(2, "0")}`);
  await delay((1 / reqs_per_sec) * 1000);
}

parentPort.postMessage(`DONE`);
