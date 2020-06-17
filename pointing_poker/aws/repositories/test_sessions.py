from time import time
from uuid import uuid4

import unittest

from moto import mock_dynamodb2
import boto3


def session_factory():
    session_id = str(uuid4())

    return (
        session_id,
        {
            "sessionID": session_id,
            "id": session_id,
            "type": "session",
            "name": "test",
            "pointingMax": 0,
            "pointingMin": 1,
            "votingStarted": False,
            "closed": False,
            "createdAt": int(time()),
            "expiresIn": int(time() + 24 * 60 * 60),
            "reviewing_issue_title": "IS-123",
            "reviewing_issue_url": "https://example.com",
            "reviewing_issue_description": "TODO",
        },
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

        session_id = str(uuid4())

        session = {
            "id": session_id,
            "name": "test",
            "pointingMax": 0,
            "pointingMin": 1,
            "votingStarted": False,
            "closed": False,
            "createdAt": int(time()),
            "expiresIn": int(time() + 24 * 60 * 60),
            "reviewing_issue_title": "IS-123",
            "reviewing_issue_url": "https://example.com",
            "reviewing_issue_description": "TODO",
        }

        repo.create(session, record_expiration=0)

        record = table.get_item(Key={"sessionID": session_id, "id": session_id})

        self.assertEqual(record["Item"]["sessionID"], session_id)
        self.assertEqual(record["Item"]["id"], session_id)
        self.assertEqual(record["Item"]["pointingMax"], session["pointingMax"])
        self.assertEqual(record["Item"]["pointingMin"], session["pointingMin"])
        self.assertEqual(record["Item"]["expiresIn"], session["expiresIn"])
        self.assertEqual(record["Item"]["votingStarted"], session["votingStarted"])
        self.assertEqual(record["Item"]["closed"], session["closed"])
        self.assertEqual(
            record["Item"]["reviewing_issue_title"], session["reviewing_issue_title"]
        )
        self.assertEqual(
            record["Item"]["reviewing_issue_url"], session["reviewing_issue_url"]
        )
        self.assertEqual(
            record["Item"]["reviewing_issue_description"],
            session["reviewing_issue_description"],
        )

    @mock_dynamodb2
    def test_get_session(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        table.put_item(Item=session)

        record = repo.get(session_id)

        self.assertEqual(record["id"], session_id)
        self.assertEqual(record["pointingMax"], session["pointingMax"])
        self.assertEqual(record["pointingMin"], session["pointingMin"])
        self.assertEqual(record["expiresIn"], session["expiresIn"])
        self.assertEqual(record["votingStarted"], session["votingStarted"])
        self.assertEqual(record["closed"], session["closed"])
        self.assertEqual(
            record["reviewingIssue"]["title"], session["reviewing_issue_title"]
        )
        self.assertEqual(
            record["reviewingIssue"]["url"], session["reviewing_issue_url"]
        )
        self.assertEqual(
            record["reviewingIssue"]["description"],
            session["reviewing_issue_description"],
        )

    @mock_dynamodb2
    def test_delete_session(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        table.put_item(Item=session)

        repo.delete_session(session_id)

        self.assertEqual(repo.get(session_id), None)

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

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        participant = {
            "id": str(uuid4()),
            "name": "John",
            "isModerator": True,
        }

        repo.add_participant(session_id, participant, record_expiration=0)

        record = table.get_item(Key={"sessionID": session_id, "id": participant["id"]})

        self.assertEqual(record["Item"]["id"], participant["id"])
        self.assertEqual(record["Item"]["name"], participant["name"])
        self.assertEqual(record["Item"]["isModerator"], participant["isModerator"])

    @mock_dynamodb2
    def test_add_participant_conflicts(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        participant_id = str(uuid4())

        participant = {
            "id": participant_id,
            "name": "John",
            "isModerator": True,
            "vote": None,
        }

        repo.add_participant(session_id, participant, record_expiration=0)

        try:
            repo.add_participant(session_id, participant, record_expiration=0)
        except Exception as err:
            self.assertEqual(
                err.args[0], f"participant with id {participant_id} already exists"
            )

    @mock_dynamodb2
    def test_get_participant_in_session(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        participant_id = str(uuid4())

        participant = {
            "id": participant_id,
            "name": "John",
            "isModerator": True,
            "vote": None,
        }

        repo.add_participant(session_id, participant, record_expiration=0)

        self.assertEqual(
            participant, repo.get_participant_in_session(session_id, participant_id)
        )

    @mock_dynamodb2
    def test_get_missing_participant(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        self.assertIsNone(repo.get_participant_in_session(session_id, "bogus"))

    @mock_dynamodb2
    def test_remove_participant(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        participant_id = str(uuid4())

        participant = {
            "id": participant_id,
            "name": "John",
            "isModerator": True,
            "vote": None,
        }

        session_id = str(uuid4())

        table.put_item(
            Item={
                "sessionID": session_id,
                "id": participant["id"],
                "name": participant["name"],
                "isModerator": participant["isModerator"],
            }
        )

        repo.remove_participant(session_id, participant_id)

        record = table.get_item(Key={"sessionID": session_id, "id": participant_id})

        self.assertNotIn("Item", record)

    @mock_dynamodb2
    def test_get_session_with_participants(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        participant = {
            "id": str(uuid4()),
            "name": "John",
            "isModerator": True,
            "vote": None,
        }

        repo.add_participant(session_id, participant, record_expiration=0)

        session = repo.get(session_id)

        self.assertIn(participant, session["participants"])

    @mock_dynamodb2
    def test_set_vote(self):
        from pointing_poker.aws.repositories import sessions

        create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        participant_id = str(uuid4())

        participant = {
            "id": participant_id,
            "name": "John",
            "isModerator": True,
            "vote": None,
        }

        repo.add_participant(session_id, participant, record_expiration=0)

        repo.set_vote(session_id, participant_id, {"points": 5, "abstained": False})

        participant = repo.get_participant_in_session(session_id, participant_id)

        self.assertEqual(participant["vote"]["points"], 5)
        self.assertEqual(participant["vote"]["abstained"], False)

    @mock_dynamodb2
    def test_set_reviewing_issue(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        repo.set_reviewing_issue(
            session_id,
            {
                "title": "My Issue",
                "description": "Work to do",
                "url": "https://example.com",
            },
        )

        item = table.get_item(Key={"sessionID": session_id, "id": session_id})

        self.assertIn("Item", item)
        self.assertEqual(item["Item"]["reviewing_issue_title"], "My Issue")
        self.assertEqual(item["Item"]["reviewing_issue_description"], "Work to do")
        self.assertEqual(item["Item"]["reviewing_issue_url"], "https://example.com")

    def test_set_reviewing_issue_empty(self):
        from pointing_poker.aws.repositories import sessions

        try:
            sessions.SessionsDynamoDBRepo().set_reviewing_issue("", {})
        except Exception as e:
            self.fail(f"set_reviewing_issue raised exception {e}")

    @mock_dynamodb2
    def test_set_voting_state(self):
        from pointing_poker.aws.repositories import sessions

        table = create_sessions_table(boto3.resource("dynamodb"))

        repo = sessions.SessionsDynamoDBRepo()

        session_id, session = session_factory()

        repo.create(session, record_expiration=0)

        repo.set_voting_state(session_id, True)

        item = table.get_item(Key={"sessionID": session_id, "id": session_id})

        self.assertIn("Item", item)
        self.assertEqual(item["Item"]["votingStarted"], True)
