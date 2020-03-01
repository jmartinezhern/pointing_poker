from datetime import datetime
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
            votingStarted=False,
            expiration=86400,  # 24 hours in seconds
            createdAt=str(datetime.utcnow())
        )

        self.repo.create(session)

        return session

    def set_reviewing_issue(self, session_id: str, issue: models.ReviewingIssueDescription) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        session.reviewingIssue = models.ReviewingIssue(
            title=issue.title,
            description=issue.description,
            url=issue.description
        )

        self.repo.set_reviewing_issue(session_id, session.reviewingIssue)

        return session

    def session(self, session_id: str) -> models.Session:
        return self.repo.get(session_id)

    def join_session(self, session_id: str, participant_description: models.ParticipantDescription) -> models.Session:
        session: models.Session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = models.Participant(id=str(uuid4()), name=participant_description.name, isModerator=False,
                                         vote=models.Vote(points=0, abstained=True))

        self.repo.add_participant(session_id, participant)

        session.participants.append(participant)

        return session

    def leave_session(self, session_id: str, participant_id: str) -> models.Session:
        participant = self.repo.get_participant(session_id, participant_id)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.remove_participant(session_id, participant_id)

        return self.repo.get(session_id)

    def set_vote(self, session_id: str, participant_id: str, vote: models.Vote) -> models.Session:
        participant = self.repo.get_participant(session_id, participant_id)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.set_vote(session_id, participant_id, vote)

        return self.repo.get(session_id)

    def start_voting(self, session_id: str) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, True)

        session.votingStarted = True

        return session

    def stop_voting(self, session_id: str) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, False)

        return self.repo.get(session_id)

    def close_session(self, session_id: str) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.delete_session(session_id)

        return session
