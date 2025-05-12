# Profiles API Documentation

This document provides details on the user profiles management endpoints available in the Profiles API.

## Base URL

All endpoints are relative to the base API URL with prefix `/profiles/`.

## Authentication

All endpoints in the Profiles API use JWT (JSON Web Token) authentication. Protected endpoints require a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Complete Profile

Updates user profile information for the authenticated user.

- **URL**: `/complete-profile/`
- **Method**: `PUT` or `PATCH`
- **Authentication**: Required
- **Request Body** (Student):

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "specialization": "Information Systems",
  "gpa": 3.75,
  "portfolio": "https://portfolio.example.com",
  "skills": [1, 2, 3]
}
```

- **Request Body** (Supervisor):

```json
{
  "first_name": "Professor",
  "last_name": "Smith",
  "degree": "Ph.D. in Computer Science",
  "skills": [1, 2, 3, 4, 5]
}
```

- **Request Body** (Dean Office):

```json
{
  "first_name": "Admin",
  "last_name": "User",
  "job_role": "dean"
}
```

- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "specialization": "Information Systems",
      "gpa": 3.75,
      "portfolio": "https://portfolio.example.com",
      "skills": [1, 2, 3]
    }
    ```
  - **400 Bad Request**: Error details for invalid input
  - **401 Unauthorized**: Authentication credentials not provided

### Get Skills List

Retrieves a list of all available skills.

- **URL**: `/skills/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "name": "Python"
      },
      {
        "id": 2,
        "name": "Machine Learning"
      },
      {
        "id": 3,
        "name": "Data Science"
      }
    ]
    ```

### Get Student Profile Details

Retrieves details of a specific student profile.

- **URL**: `/students/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the student profile
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "user": {
        "email": "student@example.com",
        "role": "Student"
      },
      "first_name": "John",
      "last_name": "Doe",
      "specialization": "Information Systems",
      "gpa": 3.75,
      "portfolio": "https://portfolio.example.com",
      "skills": [
        {
          "id": 1,
          "name": "Python"
        },
        {
          "id": 2,
          "name": "Machine Learning"
        }
      ]
    }
    ```
  - **404 Not Found**: Student profile not found

### List Supervisors

Retrieves a list of all supervisors.

- **URL**: `/supervisors/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "user": {
          "email": "supervisor@example.com",
          "role": "Supervisor"
        },
        "first_name": "Professor",
        "last_name": "Smith",
        "degree": "Ph.D. in Computer Science",
        "skills": [
          {
            "id": 1,
            "name": "Python"
          },
          {
            "id": 2,
            "name": "Machine Learning"
          }
        ]
      }
    ]
    ```

### Get Supervisor Profile Details

Retrieves details of a specific supervisor profile.

- **URL**: `/supervisors/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the supervisor profile
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "user": {
        "email": "supervisor@example.com",
        "role": "Supervisor"
      },
      "first_name": "Professor",
      "last_name": "Smith",
      "degree": "Ph.D. in Computer Science",
      "skills": [
        {
          "id": 1,
          "name": "Python"
        },
        {
          "id": 2,
          "name": "Machine Learning"
        }
      ]
    }
    ```
  - **404 Not Found**: Supervisor profile not found

## Models

### StudentProfile

Profile model for student users.

Fields:

- `user`: One-to-one relationship to User (primary key)
- `first_name`: Student's first name
- `last_name`: Student's last name
- `specialization`: Student's major/specialization (choices: "Automation and Control", "Information Systems", "Computer Systems and Software", "IT Management", "Robotics and Mechatronics")
- `gpa`: Student's grade point average
- `portfolio`: URL to student's portfolio (optional)
- `photo`: Profile photo (optional)
- `skills`: Many-to-many relationship to Skill (maximum 5)

### SupervisorProfile

Profile model for supervisor users.

Fields:

- `user`: One-to-one relationship to User (primary key)
- `first_name`: Supervisor's first name
- `last_name`: Supervisor's last name
- `degree`: Supervisor's academic degree
- `photo`: Profile photo (optional)
- `skills`: Many-to-many relationship to Skill (maximum 10)

### DeanOfficeProfile

Profile model for dean office users.

Fields:

- `user`: One-to-one relationship to User (primary key)
- `first_name`: User's first name
- `last_name`: User's last name
- `job_role`: User's role in the dean office (choices: "manager", "dean")
- `photo`: Profile photo (optional)

### Skill

Model for skills that users can select.

Fields:

- `id`: Auto-generated primary key
- `name`: Name of the skill (unique)

## Business Logic

- Profiles are automatically created when a user is registered, based on the user's role
- A user's `is_profile_completed` field is automatically updated when their profile is updated
- Student profiles have a maximum of 5 skills
- Supervisor profiles have a maximum of 10 skills
- Required fields for profile completion:
  - Students: first_name, last_name, specialization, gpa, and at least one skill
  - Supervisors: first_name, last_name, degree, and at least one skill
  - Dean Office: first_name, last_name, job_role
