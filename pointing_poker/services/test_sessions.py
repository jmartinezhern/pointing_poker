from unittest import TestCase
from unittest.mock import Mock
from time import time
from uuid import uuid4

from shortuuid import uuid

from pointing_poker.services.sessions import SessionService


def session_factory():
    return {
        "id": str(uuid()),
        "name": "test",
        "pointingMax": 1,
        "pointingMin": 100,
        "votingStarted": False,
        "createdAt": int(time()),
        "expiresIn": int(time() + (24 * 60 * 60)),
        "closed": False,
        "participants": [{"id": str(uuid4()), "name": "test", "isModerator": True}],
    }


class SessionsServiceTestCase(TestCase):
    def setUp(self) -> None:
        self.repo = Mock()
        self.service = SessionService(self.repo)

    def test_create_session(self):
        description = {"name": "test", "pointingMax": 100, "pointingMin": 1}
        moderator = {"id": "id", "name": "test"}

        session = self.service.create_session(
            description=description, moderator=moderator
        )

        self.assertEqual(len(session["participants"]), 1)

        participant = session["participants"][0]

        self.repo.create.assert_called_with(
            session, record_expiration=session["expiresIn"]
        )

        self.assertGreater(len(session["id"]), 0)
        self.assertEqual(session["name"], description["name"])
        self.assertEqual(session["pointingMax"], description["pointingMax"])
        self.assertEqual(session["pointingMin"], description["pointingMin"])
        self.assertFalse(session["votingStarted"])
        self.assertFalse(session["closed"])
        self.assertEqual(participant["name"], moderator["name"])
        self.assertEqual(participant["id"], moderator["id"])
        self.assertTrue(participant["isModerator"])

        self.repo.add_participant.assert_called_with(
            session["id"], participant, record_expiration=session["expiresIn"]
        )

    def test_set_reviewing_issue(self):
        issue = {
            "title": "IS-1234",
            "description": "Something to do.",
            "url": "https://example.com/IS-1234",
        }

        expected_session = session_factory()

        self.repo.get.return_value = expected_session

        session = self.service.set_reviewing_issue(expected_session["id"], issue)

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.set_reviewing_issue.assert_called_with(expected_session["id"], issue)

        self.assertEqual(session["reviewingIssue"]["title"], issue["title"])
        self.assertEqual(session["reviewingIssue"]["description"], issue["description"])
        self.assertEqual(session["reviewingIssue"]["url"], issue["url"])

    def test_set_reviewing_issue_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.set_reviewing_issue("bogus", {}),
            msg="session with id bogus not found",
        )

    def test_session(self):
        expected_session = session_factory()

        self.repo.get.return_value = expected_session

        session = self.service.session(expected_session["id"])

        self.repo.get.assert_called_with(expected_session["id"])

        self.assertEqual(expected_session, session)

    def test_session_not_found(self):
        self.repo.session.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.session("bogus"),
            msg="session with id bogus not found",
        )

    def test_join_session(self):
        participant = {"id": str(uuid4()), "name": "test"}

        expected_session = session_factory()

        self.repo.get.return_value = expected_session

        session = self.service.join_session(expected_session["id"], participant)

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.add_participant(
            expected_session["id"],
            participant,
            record_expiration=expected_session["expiresIn"],
        )

        self.assertEqual(len(session["participants"]), 2)
        self.assertEqual(session["participants"][1]["id"], participant["id"])
        self.assertEqual(session["participants"][1]["name"], participant["name"])
        self.assertFalse(session["participants"][1]["isModerator"])

    def test_join_session_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.repo.join_session("bogus", {}),
            msg="session with id bogus not found",
        )

    def test_leave_session(self):
        expected_session = session_factory()

        participant = {"id": str(uuid4())}

        self.repo.get.return_value = expected_session

        self.service.leave_session(expected_session["id"], participant["id"])

        self.repo.get_participant_in_session.assert_called_with(
            expected_session["id"], participant["id"]
        )

        self.repo.remove_participant.assert_called_with(
            expected_session["id"], participant["id"]
        )

    def test_leave_session_session_not_found(self):
        self.repo.get_participant_in_session.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.leave_session("bogus", "bogus"),
            msg="participant with id bogus is not part of session with id bogus",
        )

    def test_set_vote(self):
        expected_session = session_factory()

        participant = {
            "id": str(uuid4()),
            "isModerator": False,
            "vote": {"points": 1, "abstained": False},
        }

        expected_session["participants"].append(participant)

        self.repo.get_participant_in_session.return_value = participant

        self.repo.get.return_value = expected_session

        vote = {"points": 8, "abstained": True}

        session = self.service.set_vote(expected_session["id"], participant["id"], vote)

        self.assertEqual(session["participants"][1]["vote"]["points"], 8)
        self.assertTrue(session["participants"][1]["vote"]["abstained"])

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.get_participant_in_session.assert_called_with(
            expected_session["id"], participant["id"]
        )

        self.repo.set_vote.assert_called_with(
            expected_session["id"], participant["id"], vote
        )

    def test_set_vote_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.set_vote("bogus", "bogus", {}),
            msg="session with id bogus not found",
        )

    def test_set_vote_participant_not_found(self):
        session = session_factory()

        self.repo.get.return_value = session

        self.repo.get_participant_in_session.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.set_vote(session["id"], "bogus", {}),
            msg=f"participant with id bogus is not part of session with id {session['id']}",
        )

    def test_start_voting(self):
        expected_session = session_factory()

        participant = {
            "id": str(uuid4()),
            "isModerator": False,
            "vote": {"points": 1, "abstained": False},
        }

        expected_session["participants"].append(participant)

        self.repo.get.return_value = expected_session

        session = self.service.start_voting(expected_session["id"])

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.set_voting_state.assert_called_with(expected_session["id"], True)

        self.assertTrue(session["votingStarted"])

        self.assertNotIn("vote", session["participants"][0])

        self.assertIsNone(session["participants"][1]["vote"])

    def test_start_voting_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.start_voting("bogus"),
            "session with id bogus not found",
        )

    def test_stop_voting(self):
        expected_session = session_factory()

        self.repo.get.return_value = expected_session

        session = self.service.stop_voting(expected_session["id"])

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.set_voting_state.assert_called_with(expected_session["id"], False)

        self.assertFalse(session["votingStarted"])

    def test_stop_voting_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.stop_voting("bogus"),
            "session with id bogus not found",
        )

    def test_close_session(self):
        expected_session = session_factory()

        self.repo.get.return_value = expected_session

        session = self.service.close_session(expected_session["id"])

        self.repo.get.assert_called_with(expected_session["id"])

        self.repo.delete_session.assert_called_with(expected_session["id"])

        self.assertTrue(session["closed"])

    def test_close_session_not_found(self):
        self.repo.get.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.close_session("bogus"),
            "session with id bogus not found",
        )

    def test_participant(self):
        expected_participant = {
            "id": str(uuid4()),
        }

        self.repo.get_participant.return_value = expected_participant

        participant = self.service.participant(expected_participant["id"])

        self.repo.get_participant.assert_called_with(expected_participant["id"])

        self.assertEqual(participant["id"], expected_participant["id"])

    def test_participant_not_found(self):
        self.repo.get_participant.return_value = None

        self.assertRaises(
            Exception,
            lambda: self.service.participant("bogus"),
            msg="participant with id bogus not found",
        )
