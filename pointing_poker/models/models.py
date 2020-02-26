from datetime import date, datetime
from dataclasses import dataclass
from typing import List


@dataclass
class ReviewingIssue:
    title: str
    url: str
    description: str

    def to_json(self):
        return self.__dict__


@dataclass
class Participant:
    id: str
    name: str
    isModerator: bool
    currentVote: int


@dataclass
class Session:
    id: str
    name: str
    isOpen: bool
    pointingMax: int
    pointingMin: int
    expiration: int
    reviewingIssue: ReviewingIssue

    participants: List[Participant] = None

    createdAt: date = datetime.utcnow()

    def to_json(self):
        self_dict = self.__dict__
        self_dict['reviewingIssue'] = self.reviewingIssue.to_json()
        return self_dict


@dataclass
class SessionDescription:
    name: str
    pointingMax: int
    pointingMin: int
    reviewingIssue: ReviewingIssue


@dataclass
class ParticipantDescription:
    name: str
