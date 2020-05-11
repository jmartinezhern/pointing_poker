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

  Scenario: Set Reviewing Issue
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
