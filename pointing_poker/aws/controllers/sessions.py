from pointing_poker.aws.repositories import sessions as session_repo
from pointing_poker.aws.services import sessions as session_service
from pointing_poker.models import models


def create_session(event, _):
    payload = event['sessionDescription']

    reviewing_issue = payload['reviewingIssue']

    session_description = models.SessionDescription(
        name=payload['name'],
        pointingMax=payload['pointingMax'],
        pointingMin=payload['pointingMin'],
        reviewingIssue=models.ReviewingIssue(
            title=reviewing_issue['title'],
            description=reviewing_issue['description'],
            url=reviewing_issue['url']
        )
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).create_session(
        session_description).to_json()


def session(event, _):
    session_id = event['sessionID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).session(session_id).to_json()


def join_session(event, _):
    session_id = event['sessionID']
    payload = event['participant']

    participant_description = models.ParticipantDescription(
        name=payload['name']
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).join_session(
        session_id, participant_description).to_json()


def close_session(event, _):
    session_id = event['sessionID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).close_session(session_id).to_json()


def set_vote(event, _):
    session_id = event['sessionID']
    participant_id = event['participantID']
    vote = models.Vote(points=event['vote']['points'], abstained=event['vote']['abstained'])

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).set_vote(session_id, participant_id,
                                                                                        vote).to_json()


def start_voting(event, _):
    session_id = event['sessionID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).start_voting(session_id).to_json()


def stop_voting(event, _):
    session_id = event['sessionID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).stop_voting(session_id).to_json()


def set_reviewing_issue(event, _):
    session_id = event['sessionID']
    description = event['issue']

    issue = models.ReviewingIssueDescription(
        title=description['title'],
        description=description['description'],
        url=description['url']
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).set_reviewing_issue(session_id,
                                                                                                   issue).to_json()
