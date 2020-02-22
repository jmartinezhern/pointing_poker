from datetime import date, datetime
from dataclasses import dataclass


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


@dataclass
class Session:
    id: str
    name: str
    isOpen: bool
    pointingMax: int
    pointingMin: int
    expiration: int
    reviewingIssue: ReviewingIssue

    createdAt: date = datetime.utcnow()

    def to_json(self):
        self_dict = self.__dict__
        self_dict['reviewingIssue'] = self.reviewingIssue.to_json()
        return self_dict
