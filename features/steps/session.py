from os import environ
from json import loads

from behave import *
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url=f"https://{environ['GRAPHQL_ENDPOINT']}/graphql",
    use_json=True,
    headers={"x-api-key": f"{environ['API_KEY']}"},
    verify=False,
)

client = Client(retries=3, transport=transport, fetch_schema_from_transport=True)

create_session_query = gql(
    """
    mutation {
      createSession(
        sessionDescription: {
          name: "poker",
          pointingMin: 1,
          pointingMax: 100
        },
        moderator: {
          id: "1234",
          name: "John"
        }
      ) {
        id
      }
    }
    """
)

join_session_query = gql(
    """
    mutation ($sessionID: ID!, $participantID: ID!, $name: String!) {
      joinSession(sessionID: $sessionID, participant: {
        id: $participantID,
        name: $name
      }) {
        participants {
          id
          name
        }
      }
    }
    """
)

use_step_matcher("parse")


def get_value_for_field(context, field):
    response = getattr(context, "response")
    if response is None:
        raise KeyError("Response not found. GraphQL query should be executed first.")

    query = response.get(context.query_field)
    if query is None:
        raise KeyError(f"Response is missing field value {context.query_field}")

    value = query.get(field)
    if value is None:
        raise KeyError(f"Field {field} not found in response.")

    return value


@given('a graphql query for field "{field}"')
def step_impl(context, field):
    context.query = gql(context.text)
    context.query_field = field


@when("we execute the graphql query")
def step_impl(context):
    context.response = client.execute(context.query)


@then('the field "{field}" matches "{match}"')
def step_impl(context, field, match):
    value = get_value_for_field(context, field)

    if value != match:
        raise ValueError(f"Field {field} does not match {match}. Got {value}.")


@then('the field "{field}" equals {number:d}')
def step_impl(context, field, number):
    value = get_value_for_field(context, field)

    if value != number:
        raise ValueError(f"Expected field to equal {number}. Got {value}.")


@then('the field "{field}" is not empty')
def step_impl(context, field):
    value = get_value_for_field(context, field)

    if not value:
        raise ValueError(
            f"Expected value for field {field} to not be empty but it was."
        )


@then('the field "{field}" contains')
def step_impl(context, field):
    value = get_value_for_field(context, field)

    if loads(context.text) not in value:
        raise ValueError(f"Expected field to match {context.text}. Got {value}")


@given("a poker session")
def step_impl(context):
    response = client.execute(create_session_query)

    context.session_id = response["createSession"]["id"]


@when("we execute the graphql query with the last session")
def step_impl(context):
    session_id = getattr(context, "session_id")
    if session_id is None:
        raise RuntimeError(f"A session is not defined")

    context.response = client.execute(
        context.query, variable_values={"sessionID": session_id}
    )


@when("we execute the graphql query with the last session and participant")
def step_impl(context):
    session_id = getattr(context, "session_id")
    if session_id is None:
        raise RuntimeError(f"A session is not defined")

    participant_id = getattr(context, "participant_id")
    if participant_id is None:
        raise RuntimeError(f"A participant is not defined")

    context.response = client.execute(
        context.query,
        variable_values={"sessionID": session_id, "participantID": participant_id},
    )


@then('the field "{field}" is json')
def step_impl(context, field):
    value = get_value_for_field(context, field)

    if loads(context.text) != value:
        raise ValueError(f"Expected field to be json {context.text}. Got {value}")


@then('the field "{field}" is True')
def step_impl(context, field):
    value = get_value_for_field(context, field)

    if value is not True:
        raise ValueError(f"Expected field to be true. Got {value}.")


@then('the field "{field}" is False')
def step_impl(context, field):
    value = get_value_for_field(context, field)

    if value is not False:
        raise ValueError(f"Expected field to be false. Got {value}.")


@step('a participant with id "{participant_id}" and name "{name}"')
def step_impl(context, participant_id, name):
    session_id = getattr(context, "session_id")
    if session_id is None:
        raise RuntimeError(f"A session is not defined")

    client.execute(
        join_session_query,
        variable_values={
            "sessionID": session_id,
            "participantID": participant_id,
            "name": name,
        },
    )

    context.participant_id = participant_id
