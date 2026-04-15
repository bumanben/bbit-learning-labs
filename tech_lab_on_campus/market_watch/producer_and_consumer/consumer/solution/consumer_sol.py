import os

import pika
from consumer_interface import mqConsumerInterface

class mqConsumer(mqConsumerInterface):
    def __init__(
        self, binding_key: str, exchange_name: str, queue_name: str
    ) -> None:
        self.m_binding_key = binding_key
        self.m_exchange_name = exchange_name
        self.m_queue_name = queue_name
        self.setupRMQConnection()

    def setupRMQConnection(self) -> None:
        con_params = pika.URLParameters(os.environ["AMQP_URL"])
        self.m_connection = pika.BlockingConnection(parameters=con_params)
        self.m_channel = self.m_connection.channel()

        self.m_channel.queue_declare(queue=self.m_queue_name)
        self.m_channel.exchange_declare(self.m_exchange_name)
        self.m_channel.queue_bind(
            queue=self.m_queue_name,
            routing_key=self.m_binding_key,
            exchange=self.m_exchange_name,
        )

        self.m_channel.basic_consume(
            queue=self.m_queue_name,
            on_message_callback=self.on_message_callback,
            auto_ack=False,
        )

    def on_message_callback(
        self, channel, method_frame, header_frame, body
    ) -> None:
        channel.basic_ack(method_frame.delivery_tag)
        message = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
        print(f" [x] Received Message: {message}")
        try:
            self.m_channel.close()
        except Exception:
            pass
        try:
            self.m_connection.close()
        except Exception:
            pass

    def startConsuming(self) -> None:
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.m_channel.start_consuming()

    def __del__(self) -> None:
        try:
            if hasattr(self, "m_channel") and self.m_channel.is_open:
                self.m_channel.close()
        except Exception:
            pass
        try:
            if hasattr(self, "m_connection") and self.m_connection.is_open:
                self.m_connection.close()
        except Exception:
            pass

