from os import environ

import boto3


class SessionsDynamoDBRepo:
    def __init__(self):
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(environ['SESSIONS_TABLE_NAME'])

    def create(self, session):
        self.table.put_item(
            Item={
                'id': session.id,
                'sessionID': session.id,
                'createdAt': str(session.createdAt),
                'name': session.name,
                'reviewingIssueTitle': session.reviewingIssue.title,
                'reviewingIssueDescription': session.reviewingIssue.description,
                'reviewingIssueURL': session.reviewingIssue.url,
                'isOpen': session.isOpen,
                'pointingMax': session.pointingMax,
                'pointingMin': session.pointingMin,
                'expiration': session.expiration
            }
        )

        return session
