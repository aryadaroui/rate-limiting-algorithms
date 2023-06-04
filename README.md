# rate-limiting-algorithms

Examples of simple rate limiting algorithms in TypeScript and Python. 

## Usage

This was created to accompany a blog post on rate limiting algorithms, but you can also take the rate limiting functions in `rate_limiters.ts` and use them in your own projects.

**NOTE**: I use a local dummy `RemoteCache` class to emulate a remote cache because that's a common implementation for rate limiting. *You must replace this with your own data storage service / method*.

### Experiments

To run the experiments:
```bash
npm install # to install dependencies
npm run start # to run the experiments
```
## Coverage

| Rate limiting algorithm                                      | TypeScript | Python |
| ------------------------------------------------------------ | :----------: | :------: |
| Discrete window                                              | ✅          | ✅      |
| Exclusion window (Enforced average)                          | ⚠️          | ✅      |
| Sliding window                                  | ⚠️          | ✅      |