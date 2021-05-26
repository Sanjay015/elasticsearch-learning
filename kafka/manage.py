import logging.config

from typing import List
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from kafka.errors import UnknownTopicOrPartitionError

from logger import setup_logger

logging.config.dictConfig(setup_logger())
logger = logging.getLogger("app")



class Admin(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.kwargs['bootstrap_servers'] = self.kwargs.get(
            'bootstrap_servers', ['localhost:9092'])
        self._client = None
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, errortype, value, traceback):
        self.close()

    def _connect(self):
        """Connect to kafka admin client"""
        try:
            self._client = KafkaAdminClient(**self.kwargs)
            logger.info('Connected to Kafka Admin client!')
        except Exception as ex:
            logger.error(
                'Unable to connect to Kafka Admin client. %s', str(ex))

    def connect(self):
        """Connect to kafka admin"""
        if self._client is None:
            self._connect()

    def create_topics(self, topics: List[dict]):
        """Create topics in kafka"""
        topics_to_create = []
        for topic in topics:
            _topic = NewTopic(
                name=topic['name'],
                num_partitions=topic.get('num_partitions', 1),
                replication_factor=topic.get('replication_factor', 1))
            topics_to_create.append(_topic)
        try:
            self._client.create_topics(
                new_topics=topics_to_create,
                validate_only=False)
            logger.info('Topic {%s} creates successfully', topics)
        except TopicAlreadyExistsError as ex:
            logger.debug(
                'Skipping to create topic as topic already exists %s', str(ex))
        except Exception as ex:
            logger.error('Unable to create topics. %s', str(ex))

    def delete_topics(self, topics: List[str]):
        """Delete topics"""
        try:
            self._client.delete_topics(topics)
            logger.info('Delete topics: {%s}', topics)
        except UnknownTopicOrPartitionError as ex:
            logger.debug(
                'Skipping topic delete as topic dos not exists %s', str(ex))
        except Exception as ex:
            logger.error('Unable to delete topics. %s', str(ex))

    def close(self):
        if self._client is None:
            return

        try:
            self._client.close()
            logger.info('Closed Kafka Admin client connection')
        except Exception as ex:
            logger.error(
                'Unable to close Kafka Admin client cnnection. %s', str(ex))
