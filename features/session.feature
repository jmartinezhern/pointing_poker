Feature: Operate on pointing poker sessions

  Scenario: Create a session
    Given a graphql query for field "createSession"
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
        createdAt
        closed
        expiresIn
        votingStarted
        name
        pointingMin
        pointingMax
        participants {
          id
          isModerator
          name
        }
      }
    }
    """

    When we execute the graphql query

    Then the field "id" is not empty
    And the field "name" matches "poker"
    And the field "pointingMin" equals 1
    And the field "pointingMax" equals 100
    And the field "closed" is False
    And the field "participants" contains
    """
    {
      "name": "John",
      "id": "1234",
      "isModerator": true
    }
    """

  Scenario: Get a session
    Given a poker session
    And a graphql query for field "session"
    """
    query ($sessionID: ID!) {
      session(sessionID: $sessionID) {
        id
        createdAt
        expiresIn
        votingStarted
        name
        pointingMin
        pointingMax
        participants {
          id
          isModerator
          name
        }
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "id" is not empty
    And the field "name" matches "poker"
    And the field "pointingMin" equals 1
    And the field "pointingMax" equals 100
    And the field "participants" is not empty

  Scenario: Get missing session
    Given a graphql query for field "session"
    """
    query {
      session(sessionID: "bogus") {
        id
      }
    }
    """

    When we execute the graphql query

    Then the response contains error with message "session with id bogus not found"

  Scenario: Get a participant
    Given a poker session
    And a participant with id "c2c7f148-fa36-49b9-bfb4-0e643daf6bff" and name "test"
    And a graphql query for field "participant"
    """
    query ($participantID: ID!) {
      participant(id: $participantID) {
        id
        name
        isModerator
      }
    }
    """

    When we execute the graphql query with the last session and participant

    Then the field "id" matches "c2c7f148-fa36-49b9-bfb4-0e643daf6bff"
    And the field "name" matches "test"
    And the field "isModerator" is False

  Scenario: Join a session
    Given a poker session
    And a graphql query for field "joinSession"
    """
    mutation ($sessionID: ID!) {
      joinSession(sessionID: $sessionID, participant: { id: "028010ee-f7e4-4ca8-9320-83c06e504bbe", name: "Max" }) {
        participants {
          id
          name
          isModerator
        }
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "participants" contains
    """
    {
      "id": "028010ee-f7e4-4ca8-9320-83c06e504bbe",
      "name": "Max",
      "isModerator": false
    }
    """

  Scenario: Set Reviewing Issue - all fields
    Given a poker session
    And a graphql query for field "setReviewingIssue"
    """
    mutation ($sessionID: ID!) {
      setReviewingIssue(
        sessionID: $sessionID,
        issue: {
          title: "ISS-1234",
          description: "Something we need to do",
          url: "https://example.com"
        }
      ) {
        reviewingIssue {
          title
          description
          url
        }
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "reviewingIssue" is json
    """
    {
      "title": "ISS-1234",
      "description": "Something we need to do",
      "url": "https://example.com"
    }
    """

 Scenario: Set Reviewing Issue - URL only
   Given a poker session
   And a graphql query for field "setReviewingIssue"
    """
    mutation ($sessionID: ID!) {
      setReviewingIssue(
        sessionID: $sessionID,
        issue: {
          url: "https://example.com"
        }
      ) {
        reviewingIssue {
          url
        }
      }
    }
    """

   When we execute the graphql query with the last session

   Then the field "reviewingIssue" is json
    """
    {
      "url": "https://example.com"
    }
    """

  Scenario: Set Reviewing Issue - description only
    Given a poker session
    And a graphql query for field "setReviewingIssue"
    """
    mutation ($sessionID: ID!) {
      setReviewingIssue(
        sessionID: $sessionID,
        issue: {
          description: "Something we need to do"
        }
      ) {
        reviewingIssue {
          description
        }
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "reviewingIssue" is json
    """
    {
      "description": "Something we need to do"
    }
    """

  Scenario: Set Reviewing Issue - title only
    Given a poker session
    And a graphql query for field "setReviewingIssue"
    """
    mutation ($sessionID: ID!) {
      setReviewingIssue(
        sessionID: $sessionID,
        issue: {
          title: "ISS-1234"
        }
      ) {
        reviewingIssue {
          title
        }
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "reviewingIssue" is json
    """
    {
      "title": "ISS-1234"
    }
    """

  Scenario: Start Voting
    Given a poker session
    And a graphql query for field "startVoting"
    """
    mutation ($sessionID: ID!) {
      startVoting(sessionID: $sessionID) {
        votingStarted
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "votingStarted" is True

  Scenario: Stop Voting
    Given a poker session
    And a graphql query for field "stopVoting"
    """
    mutation ($sessionID: ID!) {
      stopVoting(sessionID: $sessionID) {
        votingStarted
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "votingStarted" is False

  @set_vote
  Scenario: Set Vote
    Given a poker session
    And a participant with id "c2c7f148-fa36-49b9-bfb4-0e643daf6bff" and name "test"
    And a graphql query for field "setVote"
    """
    mutation ($sessionID: ID!, $participantID: ID!) {
      setVote(sessionID: $sessionID, participantID: $participantID, vote: {points: 1, abstained: false}) {
        participants {
          id
          vote {
            points
            abstained
          }
        }
      }
    }
    """

    When we execute the graphql query with the last session and participant

    Then the field "participants" contains
    """
    {
      "id": "c2c7f148-fa36-49b9-bfb4-0e643daf6bff",
      "vote": {
        "points": 1,
        "abstained": false
      }
    }
    """

  Scenario: Close session
    Given a poker session
    And a graphql query for field "closeSession"
    """
    mutation ($sessionID: ID!) {
      closeSession(sessionID: $sessionID) {
        closed
      }
    }
    """

    When we execute the graphql query with the last session

    Then the field "closed" is True
