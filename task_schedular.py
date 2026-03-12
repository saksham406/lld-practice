import uuid
import time
import heapq
import threading
from enum import Enum
from datetime import datetime, timedelta


# -----------------------------
# Task Status Enum
# -----------------------------
class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# -----------------------------
# Task Class
# -----------------------------
class Task:

    def __init__(
        self, name, func, schedule_time,
        max_retries=3,
        retry_delay=3
    ):

        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.schedule_time = schedule_time

        self.status = TaskStatus.PENDING

        self.start_time = None
        self.end_time = None
        self.total_time = None

        # Retry config
        self.retry_count = 0
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def mark_start(self):
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()

    def mark_end(self):
        self.end_time = datetime.now()
        self.total_time = (self.end_time - self.start_time).total_seconds()
        self.status = TaskStatus.COMPLETED

    def __lt__(self, other):
        return self.schedule_time < other.schedule_time


# -----------------------------
# Task Executor
# -----------------------------
class TaskExecutor:

    def execute(self, task):
        try:
            print(f"[EXECUTOR] Starting task → {task.name}")
            task.mark_start()
            task.func()
            task.mark_end()
            print(
                f"[EXECUTOR] Task {task.name} completed in {task.total_time:.2f}s"
            )
            return True
        except Exception as e:
            print(f"[EXECUTOR] Task {task.name} failed → {e}")
            return False


# -----------------------------
# Scheduler
# -----------------------------
class Scheduler:

    def __init__(self, executor):

        self.executor = executor
        self.task_queue = []
        self.lock = threading.Lock()
        self.running = True

    def schedule_task(self, task):

        with self.lock:
            heapq.heappush(self.task_queue, task)
            task.status = TaskStatus.SCHEDULED
            print(
                f"[SCHEDULER] Task scheduled → {task.name} at {task.schedule_time}"
            )

    def _execute_task(self, task):
        success = self.executor.execute(task)
        if not success:
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.schedule_time = datetime.now() + timedelta(
                    seconds=task.retry_delay
                )
                print(
                    f"[RETRY] Retrying task {task.name} "
                    f"(attempt {task.retry_count}) at {task.schedule_time}"
                )
                self.schedule_task(task)
            else:
                task.status = TaskStatus.FAILED
                print(f"[FAILED] Task {task.name} failed permanently")
    def run(self):
        print("[SCHEDULER] Scheduler started...")
        while self.running:
            with self.lock:
                if self.task_queue:
                    next_task = self.task_queue[0]
                    if next_task.schedule_time <= datetime.now():
                        heapq.heappop(self.task_queue)
                        threading.Thread(
                            target=self._execute_task,
                            args=(next_task,)
                        ).start()
            time.sleep(0.5)


# -----------------------------
# Example Jobs
# -----------------------------
def job_success():
    print("Running success job...")
    time.sleep(2)


def job_fail():
    print("Running failing job...")
    time.sleep(1)

    raise Exception("Something went wrong")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    executor = TaskExecutor()
    scheduler = Scheduler(executor)
    now = datetime.now()
    task1 = Task(
        "success_task",
        job_success,
        now + timedelta(seconds=2)
    )

    task2 = Task(
        "failing_task",
        job_fail,
        now + timedelta(seconds=4),
        max_retries=2,
        retry_delay=3
    )
    scheduler.schedule_task(task1)
    scheduler.schedule_task(task2)
    scheduler.run()

#head for priority queue