import threading
import time
import uuid
import heapq
from queue import Queue
from datetime import datetime, timedelta

class Task:

    def __init__(self, func, args=None, kwargs=None, run_at=None, retries=0):
        self.task_id = str(uuid.uuid4())
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.run_at = run_at or datetime.now()
        self.retries = retries
    def __lt__(self, other):
        return self.run_at < other.run_at


# ---------------- RESULT BACKEND ---------------- #

class ResultBackend:

    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()

    def store(self, task_id, result):

        with self.lock:
            self.results[task_id] = result

    def get(self, task_id):

        with self.lock:
            return self.results.get(task_id)


# ---------------- TASK QUEUE ---------------- #

class TaskQueue:

    def __init__(self):
        self.queue = Queue()

    def push(self, task):
        self.queue.put(task)

    def pop(self):
        return self.queue.get()


# ---------------- WORKER ---------------- #

class Worker:

    def __init__(self, queue: TaskQueue, result_backend: ResultBackend):
        self.queue = queue
        self.result_backend = result_backend

    def start(self):

        while True:

            task = self.queue.pop()

            try:

                result = task.func(*task.args, **task.kwargs)

                self.result_backend.store(task.task_id, result)

            except Exception as e:

                self.result_backend.store(task.task_id, str(e))

            finally:

                self.queue.queue.task_done()


# ---------------- SCHEDULER ---------------- #

class Scheduler:

    def __init__(self, queue: TaskQueue):

        self.queue = queue
        self.delayed_tasks = []
        self.lock = threading.Lock()

    def schedule(self, task):

        with self.lock:
            heapq.heappush(self.delayed_tasks, task)

    def start(self):

        while True:

            now = datetime.now()

            with self.lock:

                while self.delayed_tasks and self.delayed_tasks[0].run_at <= now:

                    task = heapq.heappop(self.delayed_tasks)

                    self.queue.push(task)

            time.sleep(1)


# ---------------- TASK SERVICE ---------------- #

class TaskService:

    def __init__(self, worker_count=3):

        self.queue = TaskQueue()
        self.results = ResultBackend()
        self.scheduler = Scheduler(self.queue)

        # Start scheduler
        threading.Thread(
            target=self.scheduler.start,
            daemon=True
        ).start()

        # Start workers
        for _ in range(worker_count):

            worker = Worker(self.queue, self.results)

            threading.Thread(
                target=worker.start,
                daemon=True
            ).start()

    def submit(self, func, *args, delay=0):

        run_at = datetime.now() + timedelta(seconds=delay)

        task = Task(func, args=args, run_at=run_at)

        if delay == 0:
            self.queue.push(task)
        else:
            self.scheduler.schedule(task)

        return task.task_id

    def get_result(self, task_id):

        return self.results.get(task_id)


# ---------------- DEMO TASKS ---------------- #

def add(a, b):
    return a + b


def square(x):
    return x * x


def slow_task(x):
    time.sleep(2)
    return f"Processed {x}"


# ---------------- MAIN ---------------- #

def main():

    service = TaskService(worker_count=3)

    task1 = service.submit(add, 5, 7)

    task2 = service.submit(square, 9)

    task3 = service.submit(slow_task, "hello", delay=3)

    print("Submitted tasks...")

    time.sleep(4)

    print("Result1:", service.get_result(task1))
    print("Result2:", service.get_result(task2))
    print("Result3:", service.get_result(task3))


if __name__ == "__main__":
    main()