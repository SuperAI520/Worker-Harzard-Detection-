
global thread_manager

class ThreadManager:
	def __init__(self):
		self.threads = []

	def add_thread(self, new_thread):
		self.threads.append(new_thread)

	def join_threads(self):
		for x in self.threads:
			x.join()
		print('all threads ended')

	def count_threads(self):
		return len(self.threads)

thread_manager = ThreadManager()