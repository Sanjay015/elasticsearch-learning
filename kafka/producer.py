import logging.config
import time
from typing import Union
from kafka import KafkaProducer

from logger import setup_logger

logging.config.dictConfig(setup_logger())
logger = logging.getLogger("app")


class Producer(object):

    def __init__(
        self, servers: Union[list, str]=None, api_version: tuple=(0, 10,)):

        if not servers:
            servers = ['localhost:9092']
        self.servers = servers
        self.api_version = api_version
        self._producer = None
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, errortype, value, traceback):
        """Close Kafka connection on exit"""
        self.close()

    def close(self):
        """Close Kafka connection"""
        try:
            if self._producer is not None:
                self._producer.close()
            logger.info('Closed Kafka producer connection')
        except Exception as ex:
            logger.error('Unable to close Kafka producer connection!')

    def _connect(self):
        """Connect to kafka server"""
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=self.servers, api_version=self.api_version)
            logger.info('Connected to Kafka producer!')
        except Exception as ex:
            logger.error(
                'Exception while connecting to Kafka producer. %s', str(ex))

    def connect(self):
        """Create kafka server connection"""
        if not self._producer:
            return self._connect()

    @staticmethod
    def _str_to_bytes(value):
        """Convert `value` to bytes"""
        if isinstance(value, bytes):
            return value
        return bytes('{}'.format(value), encoding='utf-8')

    def publish(self, topic_name, key, value):
        """Publish messages on kafka server."""
        key_bytes = self._str_to_bytes(key)
        value_bytes = self._str_to_bytes(value)
        try:
            self._producer.send(topic_name, key=key_bytes, value=value_bytes)
            self._producer.flush()
            logger.info('Message published successfully!')
        except Exception as ex:
            logger.error('Exception in publishing message. %s', str(ex))


with Producer() as produce:
    for i in range(10):
        produce.publish(
            'recipe', f'key-{i}', f'Hello {i} from python!')
        time.sleep(2)
