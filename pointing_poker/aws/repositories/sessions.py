from os import environ
from typing import Union

from botocore.exceptions import ClientError
from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key

from pointing_poker.models import models


class SessionsDynamoDBRepo:
    def __init__(self):
        self.db = resource('dynamodb')
        self.table = self.db.Table(environ['SESSIONS_TABLE_NAME'] if 'SESSIONS_TABLE_NAME' in environ else 'sessions')

    def create(self, session: models.Session) -> None:
        self.table.put_item(
            Item={
                'id': session.id,
                'sessionID': session.id,
                'createdAt': session.createdAt,
                'name': session.name,
                'pointingMax': session.pointingMax,
                'pointingMin': session.pointingMin,
                'expiration': session.expiration,
                'votingStarted': session.votingStarted,
                'type': 'session'
            }
        )

    def get(self, session_id: str) -> Union[models.Session, None]:
        records = self.table.query(
            KeyConditionExpression=Key('sessionID').eq(session_id)
        )

        items = records['Items']

        if not items:
            return None

        participants = [models.Participant(
            id=item['id'],
            name=item['name'],
            isModerator=item['isModerator'],
            vote=models.Vote(points=item['points'], abstained=item['abstained'])
        ) for item in items if item['type'] == 'participant']

        session_item = [item for item in items if item['type'] == 'session'][0]

        session = models.Session(
            id=session_item['sessionID'],
            name=session_item['name'],
            createdAt=session_item['createdAt'],
            pointingMax=session_item['pointingMax'],
            pointingMin=session_item['pointingMin'],
            expiration=session_item['expiration'],
            votingStarted=False,
            participants=participants
        )

        if any(key in session_item for key in
               ['reviewingIssueTitle', 'reviewingIssueDescription', 'reviewingIssueURL']):
            session.reviewingIssue = models.ReviewingIssue(
                title=session_item.get('reviewingIssueTitle'),
                description=session_item.get('reviewingIssueDescription'),
                url=session_item.get('reviewingIssueURL'),
            )

        return session

    def get_participant_in_session(self, session_id: str, participant_id: str) -> Union[models.Participant, None]:
        record = self.table.get_item(
            Key={
                'sessionID': session_id,
                'id': participant_id,
            }
        )

        if 'Item' not in record:
            return None

        item = record['Item']

        return models.Participant(
            id=item['id'],
            name=item['name'],
            isModerator=item['isModerator'],
            vote=models.Vote(points=item['points'], abstained=item['abstained'])
        )

    def get_participant(self, user_id: str):
        records = self.table.query(
            IndexName='id-index',
            KeyConditionExpression=Key('id').eq(user_id)
        )

        items = records['Items']

        if not items:
            return None

        item = items[0]

        return models.Participant(
            id=item['id'],
            name=item['name'],
            isModerator=item['isModerator'],
            vote=models.Vote(points=item['points'], abstained=item['abstained'])
        )

    def set_reviewing_issue(self, session_id: str, issue: models.ReviewingIssue):
        self.table.update_item(
            Key={
                'sessionID': session_id,
                'id': session_id,
            },
            UpdateExpression="SET reviewingIssueTitle = :title, "
                             "reviewingIssueDescription = :description, reviewingIssueURL = :url",
            ExpressionAttributeValues={
                ':title': issue.title,
                ':description': issue.description,
                ':url': issue.url,
            }
        )

    def set_voting_state(self, session_id: str, value: bool) -> None:
        self.table.update_item(
            Key={
                'sessionID': session_id,
                'id': session_id,
            },
            UpdateExpression='SET votingStarted = :value',
            ExpressionAttributeValues={
                ':value': value,
            }
        )

    def delete_session(self, session_id) -> None:
        self.table.delete_item(
            Key={
                'sessionID': session_id,
                'id': session_id
            }
        )

    def add_participant(self, session_id: str, participant: models.Participant) -> None:
        try:
            self.table.put_item(
                Item={
                    'sessionID': session_id,
                    'id': participant.id,
                    'name': participant.name,
                    'isModerator': participant.isModerator,
                    'points': participant.vote.points,
                    'abstained': participant.vote.abstained,
                    'type': 'participant'
                },
                ConditionExpression=Attr('id').not_exists()
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception(f"participant with id {participant.id} already exists")
            else:
                raise Exception('failed to put item')

    def remove_participant(self, session_id: str, participant_id: str) -> None:
        self.table.delete_item(
            Key={
                'sessionID': session_id,
                'id': participant_id
            }
        )

    def set_vote(self, session_id: str, participant_id: str, vote: models.Vote) -> None:
        try:
            self.table.update_item(
                Key={
                    'sessionID': session_id,
                    'id': participant_id,
                },
                ConditionExpression=Attr('id').eq(participant_id),
                UpdateExpression='SET points = :points, abstained = :abstained',
                ExpressionAttributeValues={
                    ':abstained': vote.abstained,
                    ':points': vote.points
                }
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception('resource not found')
            else:
                raise Exception('failed to update item')
