from pointing_poker.aws.repositories import sessions as session_repo
from pointing_poker.aws.services import sessions as session_service
from pointing_poker.models import models


def create_session(event, _):
    payload = event['sessionDescription']

    session_description = models.SessionDescription(
        name=payload['name'],
        pointingMax=payload['pointingMax'],
        pointingMin=payload['pointingMin'],
    )

    moderator_description = models.ParticipantDescription(
        id=event['moderator']['id'],
        name=event['moderator']['name']
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).create_session(
        session_description, moderator_description).to_json()


def session(event, _):
    session_id = event['sessionID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).session(session_id).to_json()


def session_state_changed(event, _):
    session_id = event['id']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).session(session_id).to_json()


def join_session(event, _):
    session_id = event['sessionID']
    payload = event['participant']

    participant_description = models.ParticipantDescription(
        id=payload['id'],
        name=payload['name']
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).join_session(
        session_id, participant_description).to_json()


def leave_session(event, _):
    session_id = event['sessionID']
    participant_id = event['participantID']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).leave_session(session_id,
                                                                                             participant_id).to_json()


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
        title=description.get('title'),
        description=description.get('description'),
        url=description.get('url')
    )

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).set_reviewing_issue(session_id,
                                                                                                   issue).to_json()


def participant(event, _):
    user_id = event['id']

    return session_service.SessionService(session_repo.SessionsDynamoDBRepo()).participant(user_id).to_json()
