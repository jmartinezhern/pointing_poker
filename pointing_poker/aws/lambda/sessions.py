from uuid import uuid4

from pointing_poker.repositories import sessions_dynamodb_repo
from pointing_poker.models import models


def handler(event, _):
    print(event)
    db = sessions_dynamodb_repo.SessionsDynamoDBRepo()

    session_description = event['sessionDescription']

    reviewing_issue = session_description['reviewingIssue']

    session = models.Session(
        id=str(uuid4()),
        name=session_description['name'],
        pointingMax=session_description['pointingMax'],
        pointingMin=session_description['pointingMin'],
        reviewingIssue=models.ReviewingIssue(
            title=reviewing_issue['title'],
            description=reviewing_issue['description'],
            url=reviewing_issue['url']
        ),
        isOpen=True,
        expiration=86400  # 24 hours in seconds
    )

    db.create(session)

    resp = session.to_json()

    resp['createdAt'] = str(session.createdAt)

    return resp
