from os import environ
from uuid import uuid4

import unittest

from moto import mock_dynamodb2
import boto3

from pointing_poker.models import models


def create_sessions_table(db):
    return db.create_table(
        AttributeDefinitions=[{
            'AttributeName': 'id',
            'AttributeType': 'S'
        }, {
            'AttributeName': 'sessionID',
            'AttributeType': 'S'
        }],
        TableName='sessions',
        KeySchema=[{
            'AttributeName': 'sessionID',
            'KeyType': 'HASH'
        }, {
            'AttributeName': 'id',
            'KeyType': 'RANGE'
        }],
        GlobalSecondaryIndexes=[{
            'IndexName': 'string',
            'KeySchema': [{
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }, {
                'AttributeName': 'sessionID',
                'KeyType': 'RANGE'
            }],
            'Projection': {
                'ProjectionType': 'ALL'
            },
        }]
    )


class SessionsRepositoryTestCase(unittest.TestCase):
    @mock_dynamodb2
    def test_create_session(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource('dynamodb'))

        repo = sessions.SessionsDynamoDBRepo()

        session = models.Session(
            id=str(uuid4()),
            name='test',
            pointingMax=0,
            pointingMin=1,
            reviewingIssue=models.ReviewingIssue(
                title='issue title',
                description='work to do',
                url='example.com'
            ),
            isOpen=True,
            expiration=86400  # 24 hours in seconds
        )

        repo.create(session)

        record = table.get_item(
            Key={
                'sessionID': session.id,
                'id': session.id
            }
        )

        self.assertEqual(record['Item']['sessionID'], session.id)
        self.assertEqual(record['Item']['id'], session.id)
        self.assertEqual(record['Item']['pointingMax'], session.pointingMax)
        self.assertEqual(record['Item']['pointingMin'], session.pointingMin)
        self.assertEqual(record['Item']['isOpen'], session.isOpen)
        self.assertEqual(record['Item']['reviewingIssueTitle'], session.reviewingIssue.title)
        self.assertEqual(record['Item']['reviewingIssueURL'], session.reviewingIssue.url)
        self.assertEqual(record['Item']['reviewingIssueDescription'], session.reviewingIssue.description)
        self.assertEqual(record['Item']['expiration'], session.expiration)
