import logging
import json
import random

import boto3


class StreamSubmit(object):

    def __init__(self):
        self.stream_name = 'splunk-firehose-input-stream'
        self.kinesis_client = boto3.client('kinesis', 'eu-west-1')

    def format_data(
        self,
        event_data,
        index=None,
        sourcetype=None,
        source=None,
        host=None,
        time=None
    ):
        """

        :param event_data: Data to be sent
        :kwarg index:
        :kwarg sourcetype:
        :kwarg source:
        :kwarg host:
        :kwarg time:
        """
        data = {
            'index': index,
            'event': event_data
        }

        if sourcetype:
            data['sourcetype'] = sourcetype

        if source:
            data['source'] = source

        if host:
            data['host'] = host

        if 'time' in event_data and isinstance(event_data, dict):
            if not isinstance(event_data['time'], (int, float)):
                raise TypeError('time must be numerical, not: %s' % (
                    type(event_data),
                ))
            data['time'] = event_data['time']
        elif time:
            data['time'] = time

        return data

    def submit(self, index_name, data, **kwargs):
        """

        :param index_name:
        :param data: Event data
        :kwarg time:
        :kwarg host:
        :kwarg source:
        :kwarg sourcetype:
        """
        kwargs.setdefault('time', None)
        kwargs.setdefault('host', None)
        kwargs.setdefault('source', None)
        kwargs.setdefault('sourcetype', None)

        if not isinstance(data, list):
            data = [data]

        self.kinesis_client.put_records(
            StreamName=self.stream_name,
            Records=[
                {
                    'Data': json.dumps(
                        self.format_data(
                            d,
                            index=index_name,
                            sourcetype=kwargs['sourcetype'],
                            source=kwargs['source'],
                            host=kwargs['host'],
                            time=kwargs['time']
                        )
                    ),
                    'PartitionKey': str(index_name)
                } for d in data
            ]
        )
