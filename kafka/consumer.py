import json
import logging.config

from kafka import KafkaConsumer

from logger import setup_logger

logging.config.dictConfig(setup_logger())
logger = logging.getLogger("app")


class Consumer(object):

    def __init__(self, topic, **kwargs):
        self.topic = topic
        self._consumer = None

        self.kwargs = kwargs
        self.kwargs['bootstrap_servers'] = self.kwargs.get(
            'bootstrap_servers', ['localhost:9092'])
        self.kwargs['api_version'] = self.kwargs.get('api_version', (0, 10,))

        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, errortype, value, traceback):
        self.close()

    def _connect(self):
        try:
            self._consumer = KafkaConsumer(self.topic, **self.kwargs)
            logger.info('Connected to Kafka Consumer!')
        except Exception as ex:
            logger.error('Unable to conenct to Kafka consumer. %s', str(ex))

    def connect(self):
        if self._consumer is None:
            self._connect()

    def close(self):
        if self._consumer is not None:
            try:
                self._consumer.close()
                logger.info('Closed kafka consumer connection')
            except Exception as ex:
                logger.error('Unable to close Kafka comsumer connection')

    def consume(self):
        for msg in self._consumer:
            logger.info('Topic {%s}: Msg {%s}', msg.topic, msg.value)


# kwargs = {
#     'auto_offset_reset': 'earliest',
#     'group_id': 'quickstart',
#     'enable_auto_commit': True,
#     # Default this is inf, if not set will keep streaming data
#     # 'consumer_timeout_ms': 1000,
# }
# with Consumer('recipe', **kwargs) as consumer:
#     consumer.consume()
