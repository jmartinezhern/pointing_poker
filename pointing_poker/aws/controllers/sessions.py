from pointing_poker.aws.repositories import sessions as session_repo
from pointing_poker.aws.services import sessions as session_service


def handler(event, _):
    session_description = event['sessionDescription']

    session = session_service.SessionService(session_repo.SessionsDynamoDBRepo()).create_session(session_description)

    resp = session.to_json()

    resp['createdAt'] = str(session.createdAt)

    return resp
