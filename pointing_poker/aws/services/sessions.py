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
            votingStarted=False,
            expiration=86400  # 24 hours in seconds
        )

        self.repo.create(session)

        return session

    def set_reviewing_issue(self, session_id: str, issue: models.ReviewingIssue) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_reviewing_issue(session_id, models.ReviewingIssue(
            title=issue.title,
            description=issue.description,
            url=issue.description
        ))

        return self.repo.get(session_id)

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
            vote=models.Vote(points=0, abstained=True)
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

    def set_vote(self, session_id: str, participant_id: str, vote: models.Vote) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = next([participant for participant in session.participants if participant.id == participant_id],
                           None)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.set_vote(session_id, participant_id, vote)

        return self.repo.get(session_id)

    def start_voting(self, session_id: str) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, True)

        return self.repo.get(session_id)

    def stop_voting(self, session_id: str) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, False)

        return self.repo.get(session_id)

    def close_session(self, session_id: str) -> models.Session:
        session = self.repo.session(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.delete_session(session_id)

        session.isOpen = False

        return session
