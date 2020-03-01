from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Vote:
    points: int
    abstained: bool


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
    vote: Vote


@dataclass
class Session:
    id: str
    name: str
    pointingMax: int
    pointingMin: int
    expiration: int
    reviewingIssue: ReviewingIssue
    votingStarted: bool

    participants: List[Participant] = field(default_factory=list)

    createdAt: str = ''

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


@dataclass
class ReviewingIssueDescription:
    title: str
    url: Optional[str]
    description: Optional[str]
