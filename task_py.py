import uuid
import queue
import threading
import time
from enum import Enum


# -----------------------------
# Task Status Enum
# -----------------------------
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


# -----------------------------
# Task Model
# -----------------------------
class Task:

    def __init__(self, function_name, args):
        self.id = str(uuid.uuid4())
        self.function_name = function_name
        self.args = args
        self.status = TaskStatus.PENDING
        self.retry_count = 0


# -----------------------------
# Function Registry
# -----------------------------
class FunctionRegistry:

    def __init__(self):
        self.registry = {}

    def register(self, func):
        self.registry[func.__name__] = func

    def get(self, name):
        return self.registry.get(name)


# -----------------------------
# Task Queue
# -----------------------------
class TaskQueue:

    def __init__(self):
        self.queue = queue.Queue()

    def push(self, task):
        print(f"[QUEUE] Task submitted: {task.id}")
        self.queue.put(task)

    def pop(self):
        return self.queue.get()


# -----------------------------
# Result Store
# -----------------------------
class ResultStore:

    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()

    def store(self, task_id, result):
        with self.lock:
            self.results[task_id] = result

    def get(self, task_id):
        with self.lock:
            return self.results.get(task_id)


# -----------------------------
# Task Executor
# -----------------------------
class TaskExecutor:

    def __init__(self, registry):
        self.registry = registry

    def execute(self, task):

        func = self.registry.get(task.function_name)

        if not func:
            raise Exception("Function not registered")

        return func(*task.args)


# -----------------------------
# Worker
# -----------------------------
class Worker(threading.Thread):

    MAX_RETRY = 3

    def __init__(self, worker_id, task_queue, executor, result_store):
        super().__init__()
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.executor = executor
        self.result_store = result_store
        self.daemon = True

    def run(self):

        while True:

            task = self.task_queue.pop()

            try:
                print(f"[WORKER {self.worker_id}] Running task {task.id}")

                task.status = TaskStatus.RUNNING

                result = self.executor.execute(task)

                task.status = TaskStatus.SUCCESS

                self.result_store.store(task.id, result)

                print(
                    f"[WORKER {self.worker_id}] Task {task.id} completed → {result}"
                )

            except Exception as e:

                print(f"[WORKER {self.worker_id}] Error: {e}")

                if task.retry_count < self.MAX_RETRY:

                    task.retry_count += 1

                    print(
                        f"[WORKER {self.worker_id}] Retrying task {task.id}"
                    )

                    self.task_queue.push(task)

                else:

                    task.status = TaskStatus.FAILED

                    print(
                        f"[WORKER {self.worker_id}] Task {task.id} failed permanently"
                    )

            finally:
                self.task_queue.queue.task_done()


# -----------------------------
# Pipeline Manager
# -----------------------------
class PipelineManager:

    def __init__(self, task_queue):
        self.task_queue = task_queue

    def submit_task(self, function_name, args):

        task = Task(function_name, args)

        self.task_queue.push(task)

        return task.id


# -----------------------------
# Example Functions
# -----------------------------
def add(a, b):
    time.sleep(1)
    return a + b


def multiply(a, b):
    time.sleep(2)
    return a * b


def divide(a, b):
    time.sleep(1)
    return a / b


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    # Setup system components
    registry = FunctionRegistry()
    task_queue = TaskQueue()
    result_store = ResultStore()
    executor = TaskExecutor(registry)
    manager = PipelineManager(task_queue)

    # Register functions
    registry.register(add)
    registry.register(multiply)
    registry.register(divide)

    # Start workers
    workers = []

    for i in range(3):
        worker = Worker(i + 1, task_queue, executor, result_store)
        worker.start()
        workers.append(worker)

    # Submit tasks
    task_ids = []

    task_ids.append(manager.submit_task("add", (5, 3)))
    task_ids.append(manager.submit_task("multiply", (4, 6)))
    task_ids.append(manager.submit_task("divide", (10, 2)))

    # Wait for processing
    task_queue.queue.join()

    print("\nFINAL RESULTS")

    for tid in task_ids:
        print(tid, "→", result_store.get(tid))