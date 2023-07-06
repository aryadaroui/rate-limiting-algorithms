import random

class MyDateTime:
	''' Simulated datetime for experiments.
	'''
	def __init__(self, rps: float, duration: float, mode='uniform'):
		self.change_times(rps, duration, mode)

	def now(self):
		return self.times[self.current_time_index]

	def advance_time(self):
		self.current_time_index += 1
		
	def change_times(self, rps, duration, mode='uniform'):
		self.current_time_index = 0
		if mode == 'uniform':
			self.times = self._generate_times(rps, duration)
		elif mode == 'random':
			self.times = self._generate_random_times(int(duration * rps), duration)
		elif mode == 'cross_window':
			self.times = self._generate_times(rps, duration)
			self.times = [x for x in self.times if x < 200 or x > 700] # not the best way of doing this right now

	def reset(self):
		self.current_time_index = 0

	@staticmethod
	def _generate_times(rps: float, duration: float, start_time: float = 0.0) -> list:
		''' Generates a list of times in milliseconds starting from the given start time. rps is requests per second.'''
		times_ms = []
		interval = 1000 / rps
		for i in range(int(rps * duration)):
			times_ms.append(start_time + (i + 1) * interval)  # i + 1 to make it not start at 0
		return times_ms

	@staticmethod
	def _generate_random_times(num: int, duration: float, start_time: float = 0.0) -> list:
		""" Generates a list of `num` random times
		"""
		return sorted([random.uniform(start_time, (start_time + duration) * 1000) for _ in range(num)])
	

	def __iter__(self):
		for idx, time in enumerate(self.times):
			self.current_time_index = idx
			yield time