from uuid import uuid4

from pointing_poker.models import models


class SessionService:
    def __init__(self, repo):
        self.repo = repo

    def create_session(self, description) -> models.Session:
        reviewing_issue = description['reviewingIssue']

        session = models.Session(
            id=str(uuid4()),
            name=description['name'],
            pointingMax=description['pointingMax'],
            pointingMin=description['pointingMin'],
            reviewingIssue=models.ReviewingIssue(
                title=reviewing_issue['title'],
                description=reviewing_issue['description'],
                url=reviewing_issue['url']
            ),
            isOpen=True,
            expiration=86400  # 24 hours in seconds
        )

        self.repo.create(session)

        return session
