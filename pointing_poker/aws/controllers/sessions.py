from pointing_poker.aws.repositories import sessions as session_repo
from pointing_poker.services import sessions as session_service


def _default_service(service):
    if service is None:
        return session_service.SessionService(session_repo.SessionsDynamoDBRepo())

    return service


def create_session(event, _, service=None):
    session_description = event["sessionDescription"]

    moderator_description = event["moderator"]

    return _default_service(service).create_session(
        session_description, moderator_description
    )


def session(event, _, service=None):
    session_id = event["sessionID"]

    return _default_service(service).session(session_id)


def session_state_changed(event, _, service=None):
    session_id = event["id"]

    return _default_service(service).session(session_id)


def join_session(event, _, service=None):
    session_id = event["sessionID"]
    participant_description = event["participant"]

    return _default_service(service).join_session(session_id, participant_description)


def leave_session(event, _, service=None):
    session_id = event["sessionID"]
    participant_id = event["participantID"]

    return _default_service(service).leave_session(session_id, participant_id)


def close_session(event, _, service=None):
    session_id = event["sessionID"]

    return _default_service(service).close_session(session_id)


def set_vote(event, _, service=None):
    session_id = event["sessionID"]
    participant_id = event["participantID"]
    vote = event["vote"]

    return _default_service(service).set_vote(session_id, participant_id, vote)


def start_voting(event, _, service=None):
    session_id = event["sessionID"]

    return _default_service(service).start_voting(session_id)


def stop_voting(event, _, service=None):
    session_id = event["sessionID"]

    return _default_service(service).stop_voting(session_id)


def set_reviewing_issue(event, _, service=None):
    session_id = event["sessionID"]
    issue = event["issue"]

    return _default_service(service).set_reviewing_issue(session_id, issue)


def participant(event, _, service=None):
    participant_id = event["id"]

    return _default_service(service).participant(participant_id)
