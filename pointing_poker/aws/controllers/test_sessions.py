from uuid import uuid4

from unittest import TestCase
from unittest.mock import Mock

from pointing_poker.aws.controllers.sessions import (
    create_session,
    close_session,
    join_session,
    leave_session,
    participant,
    session,
    session_state_changed,
    set_reviewing_issue,
    set_vote,
    start_voting,
    stop_voting,
)


class SessionsControllersTestCase(TestCase):
    def setUp(self) -> None:
        self.service = Mock()

    def test_create_session(self):
        event = {
            "sessionDescription": {
                "name": "test",
                "pointingMin": 1,
                "pointingMax": 100,
            },
            "moderator": {"name": "John", "id": "1234"},
        }

        self.service.create_session.return_value = {
            **event["sessionDescription"],
            "participant": [{**event["moderator"], "isModerator": True}],
        }

        response = create_session(event, None, self.service)

        self.service.create_session.assert_called_with(
            event["sessionDescription"], event["moderator"]
        )

        self.assertEqual(response["name"], event["sessionDescription"]["name"])

    def test_session(self):
        session_id = str(uuid4())

        event = {
            "sessionID": session_id,
        }

        session(event, None, self.service)

        self.service.session.assert_called_with(session_id)

    def test_session_stage_changed(self):
        session_id = str(uuid4())

        event = {
            "id": session_id,
        }

        session_state_changed(event, None, self.service)

        self.service.session.assert_called_with(session_id)

    def test_join_session(self):
        participant_id = str(uuid4())
        session_id = str(uuid4())

        event = {
            "participant": {"id": participant_id, "name": "test",},
            "sessionID": session_id,
        }

        join_session(event, None, self.service)

        self.service.join_session.assert_called_with(session_id, event["participant"])

    def test_close_session(self):
        session_id = str(uuid4())

        event = {
            "sessionID": session_id,
        }

        close_session(event, None, self.service)

        self.service.close_session.assert_called_with(session_id)

    def test_leave_session(self):
        participant_id = str(uuid4())
        session_id = str(uuid4())

        event = {"participantID": participant_id, "sessionID": session_id}

        leave_session(event, None, self.service)

        self.service.leave_session.assert_called_with(session_id, participant_id)

    def test_set_vote(self):
        session_id = str(uuid4())
        participant_id = str(uuid4())

        vote = {
            "points": 1,
            "abstained": False,
        }

        event = {
            "sessionID": session_id,
            "participantID": participant_id,
            "vote": vote,
        }

        set_vote(event, None, self.service)

        self.service.set_vote.assert_called_with(session_id, participant_id, vote)

    def test_start_voting(self):
        session_id = str(uuid4())

        event = {"sessionID": session_id}

        start_voting(event, None, self.service)

        self.service.start_voting.assert_called_with(session_id)

    def test_stop_voting(self):
        session_id = str(uuid4())

        event = {"sessionID": session_id}

        stop_voting(event, None, self.service)

        self.service.stop_voting.assert_called_with(session_id)

    def test_reviewing_issue(self):
        session_id = str(uuid4())
        issue = {"title": "test"}

        event = {"sessionID": session_id, "issue": issue}

        set_reviewing_issue(event, None, self.service)

        self.service.set_reviewing_issue.assert_called_with(session_id, issue)

    def test_participant(self):
        participant_id = str(uuid4())

        event = {"id": participant_id}

        participant(event, None, self.service)

        self.service.participant.assert_called_with(participant_id)
