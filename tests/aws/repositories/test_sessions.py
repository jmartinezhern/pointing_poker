from time import time
from uuid import uuid4

import unittest

from moto import mock_dynamodb2
import boto3

from pointing_poker.models import models


def session_factory() -> models.Session:
    return models.Session(
        id=str(uuid4()),
        name="test",
        pointingMax=0,
        pointingMin=1,
        votingStarted=False,
        createdAt=int(time()),
        expiresIn=int(time() + 24 * 60 * 60),
        reviewingIssue=models.ReviewingIssue(),
    )


def create_sessions_table(db):
    return db.create_table(
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "sessionID", "AttributeType": "S"},
        ],
        TableName="sessions",
        KeySchema=[
            {"AttributeName": "sessionID", "KeyType": "HASH"},
            {"AttributeName": "id", "KeyType": "RANGE"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "string",
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"},
                    {"AttributeName": "sessionID", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )


class SessionsRepositoryTestCase(unittest.TestCase):
    @mock_dynamodb2
    def test_create_session(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = models.Session(
            id=str(uuid4()),
            name="test",
            pointingMax=0,
            pointingMin=1,
            votingStarted=False,
            createdAt=int(time()),
            expiresIn=int(time() + 24 * 60 * 60),
            reviewingIssue=models.ReviewingIssue(),
        )

        repo.create(session)

        record = table.get_item(Key={"sessionID": session.id, "id": session.id})

        self.assertEqual(record["Item"]["sessionID"], session.id)
        self.assertEqual(record["Item"]["id"], session.id)
        self.assertEqual(record["Item"]["pointingMax"], session.pointingMax)
        self.assertEqual(record["Item"]["pointingMin"], session.pointingMin)
        self.assertEqual(record["Item"]["expiresIn"], session.expiresIn)
        self.assertEqual(record["Item"]["votingStarted"], session.votingStarted)

    @mock_dynamodb2
    def test_get_session(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        record = repo.get(session.id)

        self.assertEqual(record, session)

    @mock_dynamodb2
    def test_delete_session(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        self.assertEqual(repo.get(session.id), session)

        repo.delete_session(session.id)

        self.assertEqual(repo.get(session.id), None)

    @mock_dynamodb2
    def test_get_missing_session(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        self.assertIsNone(sessions.SessionsDynamoDBRepo().get("bogus"))

    @mock_dynamodb2
    def test_add_participant(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        participant = models.Participant(
            id=str(uuid4()),
            name="John",
            isModerator=True,
            vote=models.Vote(points=0, abstained=True),
        )

        repo.add_participant(session.id, participant)

        record = table.get_item(Key={"sessionID": session.id, "id": participant.id})

        self.assertEqual(record["Item"]["id"], participant.id)
        self.assertEqual(record["Item"]["name"], participant.name)
        self.assertEqual(record["Item"]["isModerator"], participant.isModerator)

    @mock_dynamodb2
    def test_add_participant_conflicts(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        participant = models.Participant(
            id=str(uuid4()),
            name="John",
            isModerator=True,
            vote=models.Vote(points=0, abstained=True),
        )

        repo.add_participant(session.id, participant)

        try:
            repo.add_participant(session.id, participant)
        except Exception as err:
            self.assertEqual(
                err.args[0], f"participant with id {participant.id} already exists"
            )

    @mock_dynamodb2
    def test_get_participant_in_session(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        participant = models.Participant(
            id=str(uuid4()), name="John", isModerator=True,
        )

        repo.add_participant(session.id, participant)

        self.assertEqual(
            participant, repo.get_participant_in_session(session.id, participant.id)
        )

    @mock_dynamodb2
    def test_get_missing_participant(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        self.assertIsNone(repo.get_participant_in_session(session.id, "bogus"))

    @mock_dynamodb2
    def test_remove_participant(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()
        participant = models.Participant(
            id=str(uuid4()),
            name="John",
            isModerator=True,
            vote=models.Vote(points=0, abstained=True),
        )

        session_id = str(uuid4())

        table.put_item(
            Item={
                "sessionID": str(session_id),
                "id": participant.id,
                "name": participant.name,
                "isModerator": participant.isModerator,
            }
        )

        repo.remove_participant(session_id, participant.id)

        record = table.get_item(Key={"sessionID": session_id, "id": participant.id})

        self.assertNotIn("Item", record)

    @mock_dynamodb2
    def test_get_session_with_participants(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        participant = models.Participant(
            id=str(uuid4()), name="John", isModerator=True,
        )

        repo.add_participant(session.id, participant)

        session = repo.get(session.id)

        self.assertIn(participant, session.participants)

    @mock_dynamodb2
    def test_set_vote(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        participant = models.Participant(
            id=str(uuid4()),
            name="John",
            isModerator=True,
            vote=models.Vote(points=0, abstained=True),
        )

        repo.add_participant(session.id, participant)

        repo.set_vote(
            session.id, participant.id, models.Vote(points=5, abstained=False)
        )

        participant = repo.get_participant_in_session(session.id, participant.id)

        self.assertEqual(participant.vote.points, 5)
        self.assertEqual(participant.vote.abstained, False)

    @mock_dynamodb2
    def test_set_reviewing_issue(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        repo.set_reviewing_issue(
            session.id,
            models.ReviewingIssue(
                title="My Issue", description="Work to do", url="https://example.com",
            ),
        )

        item = table.get_item(Key={"sessionID": session.id, "id": session.id})

        self.assertIn("Item", item)
        self.assertEqual(item["Item"]["reviewingIssueTitle"], "My Issue")
        self.assertEqual(item["Item"]["reviewingIssueDescription"], "Work to do")
        self.assertEqual(item["Item"]["reviewingIssueURL"], "https://example.com")

    @mock_dynamodb2
    def test_set_voting_state(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session = session_factory()

        repo.create(session)

        repo.set_voting_state(session.id, True)

        item = table.get_item(Key={"sessionID": session.id, "id": session.id})

        self.assertIn("Item", item)
        self.assertEqual(item["Item"]["votingStarted"], True)
