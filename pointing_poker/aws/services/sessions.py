from datetime import datetime
from uuid import UUID, uuid4
from typing import Union

from pointing_poker.models import models


class SessionService:
    def __init__(self, repo):
        self.repo = repo

    def create_session(self, description: models.SessionDescription,
                       moderator: models.ParticipantDescription) -> models.Session:
        session = models.Session(
            id=str(uuid4()),
            name=description.name,
            pointingMax=description.pointingMax,
            pointingMin=description.pointingMin,
            votingStarted=False,
            reviewingIssue=models.ReviewingIssue(),
            expiration=24 * 60 * 60 * 1000,  # 24 hours in seconds
            participants=[],
            createdAt=str(datetime.utcnow())
        )

        session.participants.append(models.Participant(
            id=moderator.id,
            name=moderator.name,
            isModerator=True,
        ))

        self.repo.create(session)

        self.repo.add_participant(session.id, session.participants[0])

        return session

    def set_reviewing_issue(self, session_id: str, issue: models.ReviewingIssueDescription) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        session.reviewingIssue = models.ReviewingIssue(
            title=issue.title,
            description=issue.description,
            url=issue.url,
        )

        self.repo.set_reviewing_issue(session_id, session.reviewingIssue)

        return session

    def session(self, session_id: str) -> models.Session:
        session: Union[models.Session, None] = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        return session

    def join_session(self, session_id: str, participant_description: models.ParticipantDescription) -> models.Session:
        participant_description.id = str(UUID(participant_description.id, version=4))

        session: models.Session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = models.Participant(id=participant_description.id, name=participant_description.name,
                                         isModerator=False)

        self.repo.add_participant(session_id, participant)

        session.participants.append(participant)

        return session

    def leave_session(self, session_id: str, participant_id: str) -> models.Session:
        participant = self.repo.get_participant_in_session(session_id, participant_id)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.remove_participant(session_id, participant_id)

        return self.repo.get(session_id)

    def set_vote(self, session_id: str, participant_id: str, vote: models.Vote) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        participant = self.repo.get_participant_in_session(session_id, participant_id)

        if participant is None:
            raise Exception(f"participant with id {participant_id} is not part of session with {session_id}")

        self.repo.set_vote(session_id, participant_id, vote)

        participant_idx = [i for i, value in enumerate(session.participants) if value.id == participant_id][0]

        session.participants[participant_idx].vote = vote

        return session

    def start_voting(self, session_id: str) -> models.Session:
        session = self.repo.get(session_id)

        if session is None:
            raise Exception(f"session with id {session_id} not found")

        self.repo.set_voting_state(session_id, True)

        for idx, participant in enumerate(session.participants):
            if not participant.isModerator:
                session.participants[idx].vote = None
                self.repo.set_vote(session_id, participant.id, None)

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

    def participant(self, user_id: str) -> models.Participant:
        participant = self.repo.get_participant(user_id)

        if participant is None:
            raise Exception(f"participant with id {user_id} was not found")

        return participant
