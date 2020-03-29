from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Vote:
    points: int
    abstained: bool


@dataclass
class ReviewingIssue:
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

    def to_json(self):
        return self.__dict__


@dataclass
class Participant:
    id: str
    name: str
    isModerator: bool

    vote: Optional[Vote] = None

    def to_json(self):
        self_dict = self.__dict__

        if self.vote is not None:
            self_dict["vote"] = self.vote.__dict__

        return self_dict


@dataclass
class ParticipantDescription:
    id: str
    name: str


@dataclass
class Session:
    id: str
    name: str
    pointingMax: int
    pointingMin: int
    votingStarted: bool
    reviewingIssue: ReviewingIssue

    participants: List[Participant] = field(default_factory=list)

    createdAt: int = 0
    expiresIn: int = 0

    def to_json(self):
        self_dict = self.__dict__

        if self.reviewingIssue is not None:
            self_dict["reviewingIssue"] = self.reviewingIssue.to_json()

        if self.participants:
            self_dict["participants"] = [
                participant.to_json() for participant in self.participants
            ]

        return self_dict


@dataclass
class SessionDescription:
    name: str
    pointingMax: int
    pointingMin: int


@dataclass
class ReviewingIssueDescription:
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
