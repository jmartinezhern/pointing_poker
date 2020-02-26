from uuid import uuid4

from pointing_poker.models import models


class SessionService:
    def __init__(self, repo):
        self.repo = repo

    def create_session(self, description: models.SessionDescription) -> models.Session:
        session = models.Session(
            id=str(uuid4()),
            name=description.name,
            pointingMax=description.pointingMax,
            pointingMin=description.pointingMin,
            reviewingIssue=description.reviewingIssue,
            isOpen=True,
            expiration=86400  # 24 hours in seconds
        )

        self.repo.create(session)

        return session

    def session(self, session_id: str) -> models.Session:
        return self.repo.get(session_id)

    def join_session(self, session_id: str, participant_description: models.ParticipantDescription) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.add_participant(session_id, models.Participant(
            id=str(uuid4()),
            name=participant_description.name,
            isModerator=False,
            currentVote=0
        ))

        return self.repo.session(session_id)

    def leave_session(self, session_id: str, participant_id: str) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = next([participant for participant in session.participants if participant.id == participant_id],
                           None)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.remove_participant(session_id, participant_id)

        return self.repo.get(session_id)
