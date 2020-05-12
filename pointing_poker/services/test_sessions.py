from unittest import TestCase
from unittest.mock import Mock

from pointing_poker.services.sessions import SessionService


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
        self.assertEqual(participant["name"], moderator["name"])
        self.assertEqual(participant["id"], moderator["id"])
        self.assertTrue(participant["isModerator"])

        self.repo.add_participant.assert_called_with(
            session["id"], participant, record_expiration=session["expiresIn"]
        )