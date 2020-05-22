from time import time
from uuid import UUID

from shortuuid import uuid


class SessionService:
    def __init__(self, repo):
        self.repo = repo

    def create_session(self, description, moderator):
        moderator["isModerator"] = True

        session_expiration = int(time() + (24 * 60 * 60))

        session_id = str(uuid())

        session = {
            "id": session_id,
            "name": description["name"],
            "pointingMax": description["pointingMax"],
            "pointingMin": description["pointingMin"],
            "votingStarted": False,
            "createdAt": int(time()),
            "expiresIn": session_expiration,
            "closed": False,
        }

        self.repo.create(session, record_expiration=session_expiration)

        session["participants"] = [moderator]

        self.repo.add_participant(
            session_id, moderator, record_expiration=session_expiration
        )

        return session

    def set_reviewing_issue(self, session_id, issue):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        session["reviewingIssue"] = issue

        self.repo.set_reviewing_issue(session_id, session["reviewingIssue"])

        return session

    def session(self, session_id):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        return session

    def join_session(self, session_id, participant):
        participant["id"] = str(UUID(participant["id"], version=4))

        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = {
            **participant,
            "isModerator": False,
        }

        self.repo.add_participant(
            session_id, participant, record_expiration=session["expiresIn"]
        )

        session["participants"].append(participant)

        return session

    def leave_session(self, session_id, participant_id):
        participant = self.repo.get_participant_in_session(session_id, participant_id)

        if participant is None:
            raise Exception(
                f"participant with id {participant_id} is not part of session with id {session_id}"
            )

        self.repo.remove_participant(session_id, participant_id)

        return self.repo.get(session_id)

    def set_vote(self, session_id, participant_id, vote):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = self.repo.get_participant_in_session(session_id, participant_id)

        if participant is None:
            raise Exception(
                f"participant with id {participant_id} is not part of session with id {session_id}"
            )

        self.repo.set_vote(session_id, participant_id, vote)

        participant_idx = [
            i
            for i, value in enumerate(session["participants"])
            if value["id"] == participant_id
        ][0]

        session["participants"][participant_idx]["vote"] = vote

        return session

    def start_voting(self, session_id: str):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, True)

        for idx, participant in enumerate(session["participants"]):
            if not participant["isModerator"]:
                session["participants"][idx]["vote"] = None
                self.repo.set_vote(session_id, participant["id"], None)

        session["votingStarted"] = True

        return session

    def stop_voting(self, session_id: str):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, False)

        return self.repo.get(session_id)

    def close_session(self, session_id: str):
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.delete_session(session_id)

        session["closed"] = True

        return session

    def participant(self, participant_id: str):
        participant = self.repo.get_participant(participant_id)

        if participant is None:
            raise Exception(f"participant with id {participant_id} was not found")

        return participant
