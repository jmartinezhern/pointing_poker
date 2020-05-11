from os import environ

from botocore.exceptions import ClientError
from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key


def _item_to_participant(item):
    return {
        "id": item["id"],
        "name": item["name"],
        "isModerator": item["isModerator"],
        "vote": None
        if "points" not in item or "abstained" not in item
        else {"points": item["points"], "abstained": item["abstained"]},
    }


class SessionsDynamoDBRepo:
    def __init__(self):
        self.table = resource("dynamodb").Table(
            environ["SESSIONS_TABLE_NAME"]
            if "SESSIONS_TABLE_NAME" in environ
            else "sessions"
        )

    def create(self, session, record_expiration):
        item = {
            **session,
            **{"sessionID": session["id"], "ttl": record_expiration, "type": "session"},
        }

        self.table.put_item(Item=item)

    def get(self, session_id):
        records = self.table.query(
            KeyConditionExpression=Key("sessionID").eq(session_id)
        )

        items = records["Items"]

        if not items:
            return None

        participants = [
            _item_to_participant(item)
            for item in items
            if item.get("type", "") == "participant"
        ]

        session_item = [item for item in items if item.get("type", "") == "session"][0]

        issue = {}

        if any(
            key in session_item
            for key in [
                "reviewingIssueTitle",
                "reviewingIssueDescription",
                "reviewingIssueURL",
            ]
        ):
            issue = {
                "title": session_item.get("reviewingIssueTitle"),
                "description": session_item.get("reviewingIssueDescription"),
                "url": session_item.get("reviewingIssueURL"),
            }

        session = {
            "id": session_item["sessionID"],
            "name": session_item["name"],
            "createdAt": session_item["createdAt"],
            "pointingMax": session_item["pointingMax"],
            "pointingMin": session_item["pointingMin"],
            "expiresIn": session_item["expiresIn"],
            "votingStarted": session_item["votingStarted"],
            "participants": participants,
            "reviewingIssue": issue,
        }

        return session

    def get_participant_in_session(self, session_id, participant_id):
        record = self.table.get_item(
            Key={"sessionID": session_id, "id": participant_id}
        )

        if "Item" not in record:
            return None

        return _item_to_participant(record["Item"])

    def get_participant(self, user_id):
        records = self.table.query(
            IndexName="id-index", KeyConditionExpression=Key("id").eq(user_id)
        )

        items = records["Items"]

        if not items:
            return None

        return _item_to_participant(items[0])

    def set_reviewing_issue(self, session_id, issue):
        self.table.update_item(
            Key={"sessionID": session_id, "id": session_id},
            UpdateExpression="SET reviewingIssueTitle = :title, "
            "reviewingIssueDescription = :description, reviewingIssueURL = :url",
            ExpressionAttributeValues={
                f":{key}": value for (key, value) in issue.items()
            },
        )

    def set_voting_state(self, session_id, value):
        self.table.update_item(
            Key={"sessionID": session_id, "id": session_id},
            UpdateExpression="SET votingStarted = :value",
            ExpressionAttributeValues={":value": value},
        )

    def delete_session(self, session_id):
        self.table.delete_item(Key={"sessionID": session_id, "id": session_id})

    def add_participant(self, session_id, participant, record_expiration):
        try:
            self.table.put_item(
                Item={
                    "sessionID": session_id,
                    "id": participant["id"],
                    "name": participant["name"],
                    "isModerator": participant["isModerator"],
                    "ttl": record_expiration,
                    "type": "participant",
                },
                ConditionExpression=Attr("id").not_exists(),
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise Exception(
                    f"participant with id {participant['id']} already exists"
                )
            else:
                raise Exception("failed to put item")

    def remove_participant(self, session_id, participant_id):
        self.table.delete_item(Key={"sessionID": session_id, "id": participant_id})

    def set_vote(self, session_id, participant_id, vote):
        try:
            key = {
                "sessionID": session_id,
                "id": participant_id,
            }

            if vote is None:
                self.table.update_item(
                    Key=key,
                    ConditionExpression=Attr("id").eq(participant_id),
                    UpdateExpression="REMOVE points, abstained",
                )
                return

            self.table.update_item(
                Key=key,
                ConditionExpression=Attr("id").eq(participant_id),
                UpdateExpression="SET points = :points, abstained = :abstained",
                ExpressionAttributeValues={
                    ":abstained": vote["abstained"],
                    ":points": vote["points"],
                },
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise Exception("resource not found")
            else:
                raise Exception("failed to update item")
