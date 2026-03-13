import uuid
import threading
import queue
import time


# -----------------------------
# Message
# -----------------------------
class Message:

    def __init__(self, payload, routing_key):
        self.id = str(uuid.uuid4())
        self.payload = payload
        self.routing_key = routing_key


# -----------------------------
# Queue
# -----------------------------
class QueueService:

    def __init__(self, name):
        self.name = name
        self.messages = queue.Queue()

    def push(self, message):
        print(f"[QUEUE {self.name}] Received message {message.id}")
        self.messages.put(message)

    def pop(self):
        return self.messages.get()


# -----------------------------
# Exchange
# -----------------------------
class Exchange:

    def __init__(self, name):
        self.name = name
        self.bindings = {}

    def bind_queue(self, routing_key, queue):

        if routing_key not in self.bindings:
            self.bindings[routing_key] = []

        self.bindings[routing_key].append(queue)

    def route(self, message):

        queues = self.bindings.get(message.routing_key, [])

        if not queues:
            print("No queue bound for routing key")

        for q in queues:
            q.push(message)


# -----------------------------
# Broker
# -----------------------------
class Broker:

    def __init__(self):
        self.exchanges = {}
        self.queues = {}

    def create_exchange(self, name):
        exchange = Exchange(name)
        self.exchanges[name] = exchange
        return exchange

    def create_queue(self, name):
        q = QueueService(name)
        self.queues[name] = q
        return q

    def bind_queue(self, exchange_name, routing_key, queue_name):

        exchange = self.exchanges[exchange_name]
        queue = self.queues[queue_name]

        exchange.bind_queue(routing_key, queue)

    def publish(self, exchange_name, message):

        exchange = self.exchanges.get(exchange_name)

        if not exchange:
            raise Exception("Exchange not found")

        exchange.route(message)


# -----------------------------
# Producer
# -----------------------------
class Producer:

    def __init__(self, broker):
        self.broker = broker

    def send(self, exchange, routing_key, payload):

        message = Message(payload, routing_key)

        print(f"[PRODUCER] Sending message {message.id}")

        self.broker.publish(exchange, message)


# -----------------------------
# Consumer
# -----------------------------
class Consumer(threading.Thread):

    def __init__(self, name, queue):
        super().__init__()
        self.name = name
        self.queue = queue
        self.daemon = True

    def run(self):

        while True:

            message = self.queue.pop()

            print(
                f"[CONSUMER {self.name}] Processing message "
                f"{message.id} -> {message.payload}"
            )

            time.sleep(1)


# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":

    broker = Broker()

    # Create exchange
    exchange = broker.create_exchange("orders_exchange")

    # Create queues
    email_queue = broker.create_queue("email_queue")
    analytics_queue = broker.create_queue("analytics_queue")

    # Bind queues
    broker.bind_queue("orders_exchange", "order_created", "email_queue")
    broker.bind_queue("orders_exchange", "order_created", "analytics_queue")

    # Start consumers
    consumer1 = Consumer("email_service", email_queue)
    consumer2 = Consumer("analytics_service", analytics_queue)

    consumer1.start()
    consumer2.start()

    producer = Producer(broker)

    # Send messages
    producer.send(
        "orders_exchange",
        "order_created",
        {"order_id": 101}
    )

    producer.send(
        "orders_exchange",
        "order_created",
        {"order_id": 102}
    )

    while True:
        time.sleep(10)
