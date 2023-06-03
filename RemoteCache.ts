/**
 * A class that mimics a remote cache data store.
 */
export class RemoteCache {
	/**
	 * In-memory data store. Type is any because we can store any type of data.
	 * We could use a Map but we won't because we're only storing a small amount of data.
	 */
	private data: any = {};

	/**
	 * Creates a new instance of the `RemoteCache` class.
	 */
	constructor() { }

	/**
	 * Sets data with optional TTL in milliseconds.
	 * @param key The key to set.
	 * @param value The value to set.
	 * @param ttl The time-to-live in milliseconds.
	 */
	set(key: string, value: any, ttl?: number) {
		const expiration = ttl ? Date.now() + ttl : null;

		this.data[key] = { value, expiration };
	}

	/**
	 * Gets data if it exists and TTL has not expired.
	 * @param key The key to get.
	 * @returns The value associated with the key, or null if the key does not exist or has expired.
	 */
	get(key: string): any | null {
		const data = this.data[key];
		if (!data) return null;
		if (data.expiration && data.expiration < Date.now()) {
			// delete the key if expired
			delete this.data[key];
			return null;
		}
		return data.value;
	}

	/**
	 * Increments the value of a key. Does not reset TTL.
	 * @param key The key to increment.
	 */
	incr(key: string) {
		// check if key exists and is a number
		if (typeof this.data[key].value === "number") {
			this.data[key].value += 1;
		}
	}

	/**
	 * Resets the data store.
	 */
	reset() {
		this.data = {};
	}
}
