# Teams API Documentation

This document provides details on the team management endpoints available in the Teams API.

## Base URL

All endpoints are relative to the base API URL with prefix `/teams/`.

## Authentication

Most endpoints in the Teams API use JWT (JSON Web Token) authentication. Protected endpoints require a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Create Team

Creates a new team with the authenticated user as owner.

- **URL**: `/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:

```json
{
  "thesis_topic": 1,
  "status": "pending"
}
```

- **Response**:
  - **201 Created**:
    ```json
    {
      "id": 1,
      "thesis_topic": 1,
      "owner": 2,
      "members": [3],
      "supervisor": null,
      "status": "pending"
    }
    ```
  - **400 Bad Request**: Error details for invalid input
  - **401 Unauthorized**: Authentication credentials not provided

### List Teams

Retrieves a list of all teams.

- **URL**: `/`
- **Method**: `GET`
- **Authentication**: None
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "thesis_topic": {
          "id": 1,
          "title": "Machine Learning Application in Healthcare",
          "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
          "required_skills": [1, 2, 3]
        },
        "owner": {
          "id": 2,
          "email": "student@example.com"
        },
        "members": [
          {
            "id": 3,
            "first_name": "John",
            "last_name": "Doe"
          }
        ],
        "supervisor": null,
        "status": "pending"
      }
    ]
    ```

### Get Team Details

Retrieves details of a specific team.

- **URL**: `/<id>/`
- **Method**: `GET`
- **Authentication**: None
- **URL Parameters**:
  - `id`: ID of the team
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "thesis_topic": {
        "id": 1,
        "title": "Machine Learning Application in Healthcare",
        "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
        "required_skills": [1, 2, 3]
      },
      "owner": {
        "id": 2,
        "email": "student@example.com"
      },
      "members": [
        {
          "id": 3,
          "first_name": "John",
          "last_name": "Doe"
        }
      ],
      "supervisor": null,
      "status": "pending"
    }
    ```
  - **404 Not Found**: Team not found

### Get My Team

Retrieves the team that the authenticated user owns or is a member of.

- **URL**: `/my/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "thesis_topic": {
        "id": 1,
        "title": "Machine Learning Application in Healthcare"
      },
      "owner": {
        "id": 2,
        "email": "student@example.com"
      },
      "members": [
        {
          "id": 3,
          "first_name": "John",
          "last_name": "Doe"
        }
      ],
      "supervisor": null,
      "status": "pending"
    }
    ```
  - **404 Not Found**: You are not part of any team

### Join Team

Sends a request to join a team.

- **URL**: `/<id>/join/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the team
- **Response**:
  - **201 Created**:
    ```json
    {
      "id": 1,
      "student": 3,
      "team": 1,
      "status": "pending",
      "created_at": "2025-05-12T10:30:00Z"
    }
    ```
  - **400 Bad Request**: You are already a member of this team or have a pending request
  - **401 Unauthorized**: Authentication credentials not provided

### List My Join Requests

Retrieves all join requests made by the authenticated user.

- **URL**: `/my-join-requests/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "student": {
          "id": 3,
          "first_name": "John",
          "last_name": "Doe"
        },
        "team": {
          "id": 1,
          "thesis_topic": {
            "title": "Machine Learning Application in Healthcare"
          }
        },
        "status": "pending",
        "created_at": "2025-05-12T10:30:00Z"
      }
    ]
    ```

### Cancel Join Request

Cancels a join request made by the authenticated user.

- **URL**: `/my-join-requests/<id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the team
- **Response**:
  - **204 No Content**: Request deleted successfully
  - **404 Not Found**: Join request not found

### List Team Join Requests

Retrieves all join requests for teams owned by the authenticated user.

- **URL**: `/my-team-join-requests/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "student": {
          "id": 4,
          "first_name": "Jane",
          "last_name": "Smith"
        },
        "team": {
          "id": 1,
          "thesis_topic": {
            "title": "Machine Learning Application in Healthcare"
          }
        },
        "status": "pending",
        "created_at": "2025-05-12T11:30:00Z"
      }
    ]
    ```

### Accept Join Request

Accepts a request to join a team.

- **URL**: `/<id>/join-requests/<student_id>/accept/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the team
  - `student_id`: ID of the student
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Join request accepted"
    }
    ```
  - **403 Forbidden**: You are not the team owner
  - **404 Not Found**: Join request not found

### Reject Join Request

Rejects a request to join a team.

- **URL**: `/<id>/join-requests/<student_id>/reject/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the team
  - `student_id`: ID of the student
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Join request rejected"
    }
    ```
  - **403 Forbidden**: You are not the team owner
  - **404 Not Found**: Join request not found

### Create Supervisor Request

Sends a request to a supervisor to supervise a team.

- **URL**: `/supervisor-request/<supervisor_id>/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `supervisor_id`: ID of the supervisor
- **Response**:
  - **201 Created**:
    ```json
    {
      "id": 1,
      "team": 1,
      "supervisor": 5,
      "status": "pending",
      "created_at": "2025-05-12T12:30:00Z"
    }
    ```
  - **400 Bad Request**: You already have a pending supervisor request
  - **403 Forbidden**: You are not the team owner

### List Incoming Supervisor Requests

Retrieves all supervisor requests for the authenticated supervisor.

- **URL**: `/supervisor-requests/incoming/`
- **Method**: `GET`
- **Authentication**: Required (Supervisor role)
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "team": {
          "id": 1,
          "thesis_topic": {
            "title": "Machine Learning Application in Healthcare"
          },
          "members": [
            {
              "id": 3,
              "first_name": "John",
              "last_name": "Doe"
            }
          ]
        },
        "status": "pending",
        "created_at": "2025-05-12T12:30:00Z"
      }
    ]
    ```

### Accept Supervisor Request

Accepts a request to supervise a team.

- **URL**: `/supervisor-requests/<request_id>/accept/`
- **Method**: `POST`
- **Authentication**: Required (Supervisor role)
- **URL Parameters**:
  - `request_id`: ID of the supervisor request
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Supervisor request accepted"
    }
    ```
  - **400 Bad Request**: You cannot supervise more than 10 teams
  - **403 Forbidden**: You are not the requested supervisor
  - **404 Not Found**: Supervisor request not found

### Reject Supervisor Request

Rejects a request to supervise a team.

- **URL**: `/supervisor-requests/<request_id>/reject/`
- **Method**: `POST`
- **Authentication**: Required (Supervisor role)
- **URL Parameters**:
  - `request_id`: ID of the supervisor request
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Supervisor request rejected"
    }
    ```
  - **403 Forbidden**: You are not the requested supervisor
  - **404 Not Found**: Supervisor request not found

### Cancel Supervisor Request

Cancels a supervisor request made by the authenticated team owner.

- **URL**: `/supervisor-requests/cancel/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**:
  - **204 No Content**: Request deleted successfully
  - **404 Not Found**: Supervisor request not found

### Like/Unlike Team

Toggles like for a team.

- **URL**: `/likes/toggle/<team_id>/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `team_id`: ID of the team
- **Response**:
  - **200 OK**:
    ```json
    {
      "liked": true
    }
    ```
  - **404 Not Found**: Team not found

### List Liked Teams

Retrieves all teams liked by the authenticated user.

- **URL**: `/likes/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "thesis_topic": {
          "id": 1,
          "title": "Machine Learning Application in Healthcare"
        },
        "owner": {
          "id": 2,
          "email": "student@example.com"
        },
        "members": [
          {
            "id": 3,
            "first_name": "John",
            "last_name": "Doe"
          }
        ],
        "supervisor": null,
        "status": "pending"
      }
    ]
    ```

### Leave Team

Allows a student to leave a team they are a member of.

- **URL**: `/leave/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Left team successfully"
    }
    ```
  - **400 Bad Request**: You are not a member of any team
  - **403 Forbidden**: Team owners cannot leave their teams

### Remove Team Member

Removes a member from a team.

- **URL**: `/<id>/remove-member/<student_id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the team
  - `student_id`: ID of the student to remove
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Member removed successfully"
    }
    ```
  - **403 Forbidden**: You are not the team owner
  - **404 Not Found**: Student not found in team

### Approve Team (Dean Office)

Approves a team for the thesis process.

- **URL**: `/<id>/approve/`
- **Method**: `POST`
- **Authentication**: Required (Dean Office role)
- **URL Parameters**:
  - `id`: ID of the team
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Team approved successfully"
    }
    ```
  - **403 Forbidden**: Only Dean Office staff can approve teams
  - **404 Not Found**: Team not found

### List Approved Teams

Retrieves all approved teams (for Dean Office).

- **URL**: `/approved/`
- **Method**: `GET`
- **Authentication**: Required (Dean Office role)
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "thesis_topic": {
          "id": 1,
          "title": "Machine Learning Application in Healthcare"
        },
        "owner": {
          "id": 2,
          "email": "student@example.com"
        },
        "members": [
          {
            "id": 3,
            "first_name": "John",
            "last_name": "Doe"
          }
        ],
        "supervisor": {
          "id": 5,
          "first_name": "Professor",
          "last_name": "Smith"
        },
        "status": "approved"
      }
    ]
    ```

### Export Approved Teams to Excel

Exports approved teams to an Excel file.

- **URL**: `/export-excel/`
- **Method**: `GET`
- **Authentication**: Required (Dean Office role)
- **Response**:
  - **200 OK**: Excel file download

## Models

### Team

The main model for thesis teams.

Fields:

- `id`: Auto-generated primary key
- `thesis_topic`: One-to-one relationship to ThesisTopic
- `owner`: Foreign key to User (team owner)
- `members`: Many-to-many relationship to StudentProfile through Membership
- `supervisor`: Foreign key to SupervisorProfile (null if no supervisor assigned)
- `status`: Team status (pending, approved, rejected)

### JoinRequest

Model for student requests to join teams.

Fields:

- `student`: Foreign key to StudentProfile
- `team`: Foreign key to Team
- `status`: Request status (pending, accepted, rejected)
- `created_at`: Timestamp when the request was created

### SupervisorRequest

Model for team requests to supervisors.

Fields:

- `team`: Foreign key to Team
- `supervisor`: Foreign key to SupervisorProfile
- `status`: Request status (pending, accepted, rejected)
- `created_at`: Timestamp when the request was created

### Like

Model for team likes.

Fields:

- `user`: Foreign key to User
- `team`: Foreign key to Team
- `created_at`: Timestamp when the like was created
