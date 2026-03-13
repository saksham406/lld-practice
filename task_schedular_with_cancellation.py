import uuid
import heapq
import time
import threading
from enum import Enum
from datetime import datetime, timedelta


# ------------------------------------------------
# Task Status
# ------------------------------------------------
class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ------------------------------------------------
# Task
# ------------------------------------------------
class Task:

    def __init__(self, name, func, schedule_time, max_retries=2):

        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.schedule_time = schedule_time

        self.status = TaskStatus.PENDING

        self.retry_count = 0
        self.max_retries = max_retries

        self.start_time = None
        self.end_time = None

        self.cancelled = False

    def cancel(self):
        self.cancelled = True
        self.status = TaskStatus.CANCELLED

    def __lt__(self, other):
        return self.schedule_time < other.schedule_time


# ------------------------------------------------
# Task Queue (Min Heap)
# ------------------------------------------------
class TaskQueue:

    def __init__(self):
        self.heap = []
        self.lock = threading.Lock()

    def push(self, task):

        with self.lock:
            heapq.heappush(self.heap, task)

    def pop(self):

        with self.lock:
            if not self.heap:
                return None

            return heapq.heappop(self.heap)

    def peek(self):

        with self.lock:
            if not self.heap:
                return None

            return self.heap[0]


# ------------------------------------------------
# Executor
# ------------------------------------------------
class TaskExecutor:

    def execute(self, task):

        if task.cancelled:
            print(f"[EXECUTOR] Task {task.name} cancelled")
            return False

        try:

            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()

            print(f"[EXECUTOR] Running {task.name}")

            task.func()

            task.end_time = datetime.now()
            task.status = TaskStatus.COMPLETED

            print(f"[EXECUTOR] Task {task.name} completed")

            return True

        except Exception as e:

            print(f"[EXECUTOR] Task {task.name} failed → {e}")

            return False


# ------------------------------------------------
# Worker
# ------------------------------------------------
class Worker(threading.Thread):

    def __init__(self, scheduler, executor, task):
        super().__init__()
        self.scheduler = scheduler
        self.executor = executor
        self.task = task

    def run(self):

        success = self.executor.execute(self.task)

        if not success and not self.task.cancelled:

            if self.task.retry_count < self.task.max_retries:

                self.task.retry_count += 1

                self.task.schedule_time = datetime.now() + timedelta(seconds=3)

                print(
                    f"[RETRY] Retrying {self.task.name} "
                    f"(attempt {self.task.retry_count})"
                )

                self.scheduler.schedule(self.task)

            else:

                self.task.status = TaskStatus.FAILED

                print(f"[FAILED] Task {self.task.name} permanently failed")


# ------------------------------------------------
# Scheduler
# ------------------------------------------------
class Scheduler:

    def __init__(self):

        self.task_queue = TaskQueue()
        self.executor = TaskExecutor()
        self.task_registry = {}

        self.running = True

    def schedule(self, task):

        self.task_queue.push(task)

        task.status = TaskStatus.SCHEDULED

        self.task_registry[task.id] = task

        print(f"[SCHEDULER] Scheduled {task.name}")

        return task.id

    def cancel_task(self, task_id):

        task = self.task_registry.get(task_id)

        if not task:
            print("[SCHEDULER] Task not found")
            return

        task.cancel()

        print(f"[SCHEDULER] Task {task.name} cancelled")

    def run(self):

        print("[SCHEDULER] Scheduler started")

        while self.running:

            task = self.task_queue.peek()

            if not task:
                time.sleep(1)
                continue

            if task.schedule_time <= datetime.now():

                task = self.task_queue.pop()

                if task.cancelled:

                    print(f"[SCHEDULER] Skipping cancelled task {task.name}")

                    continue

                worker = Worker(self, self.executor, task)

                worker.start()

            else:

                time.sleep(0.5)


# ------------------------------------------------
# Example Jobs
# ------------------------------------------------
def job1():

    print("Running job1")

    time.sleep(2)


def job2():

    print("Running job2")

    time.sleep(1)

    raise Exception("Random failure")


def job3():

    print("Running job3")

    time.sleep(3)


# ------------------------------------------------
# Main
# ------------------------------------------------
if __name__ == "__main__":

    scheduler = Scheduler()

    now = datetime.now()

    task1 = Task("task1", job1, now + timedelta(seconds=3))
    task2 = Task("task2", job2, now + timedelta(seconds=5))
    task3 = Task("task3", job3, now + timedelta(seconds=10))

    id1 = scheduler.schedule(task1)
    id2 = scheduler.schedule(task2)
    id3 = scheduler.schedule(task3)

    # Cancel task3 after some time
    def cancel_task():

        time.sleep(4)

        scheduler.cancel_task(id3)

    threading.Thread(target=cancel_task).start()

    scheduler.run()
