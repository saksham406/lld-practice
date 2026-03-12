from abc import ABC, abstractmethod
from enum import Enum
from queue import Queue
import threading
import time


# ---------------- ENUM ---------------- #

class NotificationChannel(Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


# ---------------- MODEL ---------------- #

class Notification:

    def __init__(self, user_id, message, channel: NotificationChannel):
        self.user_id = user_id
        self.message = message
        self.channel = channel

    def __str__(self):
        return f"[{self.channel.value}] -> {self.user_id} : {self.message}"


# ---------------- SENDER INTERFACE ---------------- #

class NotificationSender(ABC):

    @abstractmethod
    def send(self, notification: Notification):
        pass


# ---------------- CHANNEL IMPLEMENTATIONS ---------------- #

class EmailSender(NotificationSender):

    def send(self, notification: Notification):
        print(f"Sending EMAIL to {notification.user_id}: {notification.message}")


class SMSSender(NotificationSender):

    def send(self, notification: Notification):
        print(f"Sending SMS to {notification.user_id}: {notification.message}")


class PushSender(NotificationSender):

    def send(self, notification: Notification):
        print(f"Sending PUSH to {notification.user_id}: {notification.message}")


# ---------------- FACTORY ---------------- #

class SenderFactory:

    @staticmethod
    def get_sender(channel: NotificationChannel):

        if channel == NotificationChannel.EMAIL:
            return EmailSender()

        if channel == NotificationChannel.SMS:
            return SMSSender()

        if channel == NotificationChannel.PUSH:
            return PushSender()

        raise Exception("Unsupported channel")


# ---------------- SERVICE ---------------- #

class NotificationService:

    def __init__(self):
        self.queue = Queue()

    def send_notification(self, notification: Notification):

        # push notification to queue
        self.queue.put(notification)

    def worker(self):

        while True:

            notification = self.queue.get()

            sender = SenderFactory.get_sender(notification.channel)

            sender.send(notification)

            self.queue.task_done()


# ---------------- DEMO ---------------- #

def main():

    service = NotificationService()

    # start worker thread
    worker_thread = threading.Thread(target=service.worker, daemon=True)
    worker_thread.start()

    n1 = Notification(
        "user1",
        "Your order is shipped",
        NotificationChannel.EMAIL
    )

    n2 = Notification(
        "user2",
        "OTP: 839221",
        NotificationChannel.SMS
    )

    n3 = Notification(
        "user3",
        "You have a new message",
        NotificationChannel.PUSH
    )

    service.send_notification(n1)
    service.send_notification(n2)
    service.send_notification(n3)

    time.sleep(1)


if __name__ == "__main__":
    main()