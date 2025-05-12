# Topics API Documentation

This document provides details on the thesis topics management endpoints available in the Topics API.

## Base URL

All endpoints are relative to the base API URL with prefix `/topics/`.

## Authentication

Most endpoints in the Topics API use JWT (JSON Web Token) authentication. Protected endpoints require a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Create Thesis Topic

Creates a new thesis topic and automatically creates a team associated with it.

- **URL**: `/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:

```json
{
  "title": "Machine Learning Application in Healthcare",
  "title_kz": "Денсаулық сақтаудағы машиналық оқыту қолданбасы",
  "title_ru": "Применение машинного обучения в здравоохранении",
  "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
  "required_skills": [1, 2, 3]
}
```

- **Response**:

  - **201 Created**:
    ```json
    {
      "id": 1,
      "title": "Machine Learning Application in Healthcare",
      "title_kz": "Денсаулық сақтаудағы машиналық оқыту қолданбасы",
      "title_ru": "Применение машинного обучения в здравоохранении",
      "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
      "required_skills": [1, 2, 3],
      "created_by_student": 1,
      "created_by_supervisor": null
    }
    ```
  - **400 Bad Request**: Error details for invalid input
  - **401 Unauthorized**: Authentication credentials not provided

- **Validation Rules**:
  - For Students:
    - Can create only one thesis topic
    - Cannot create a new topic if already part of a team
    - Cannot create a new topic if has a pending join request
  - For Supervisors:
    - Limited to 10 total topics/teams combined
  - Only students and supervisors can create thesis topics

### List Thesis Topics

Retrieves a list of all thesis topics.

- **URL**: `/`
- **Method**: `GET`
- **Authentication**: None
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "title": "Machine Learning Application in Healthcare",
        "title_kz": "Денсаулық сақтаудағы машиналық оқыту қолданбасы",
        "title_ru": "Применение машинного обучения в здравоохранении",
        "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
        "required_skills": [1, 2, 3],
        "created_by_student": 1,
        "created_by_supervisor": null
      },
      {
        "id": 2,
        "title": "Blockchain for Supply Chain Management",
        "title_kz": "Жеткізу тізбегін басқаруға арналған блокчейн",
        "title_ru": "Блокчейн для управления цепочками поставок",
        "description": "This thesis explores blockchain applications in supply chain management.",
        "required_skills": [4, 5],
        "created_by_student": null,
        "created_by_supervisor": 1
      }
    ]
    ```

### Get Thesis Topic Details

Retrieves details of a specific thesis topic.

- **URL**: `/<id>/`
- **Method**: `GET`
- **Authentication**: None
- **URL Parameters**:
  - `id`: ID of the thesis topic
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "title": "Machine Learning Application in Healthcare",
      "title_kz": "Денсаулық сақтаудағы машиналық оқыту қолданбасы",
      "title_ru": "Применение машинного обучения в здравоохранении",
      "description": "This thesis will explore applications of machine learning algorithms in healthcare diagnostics.",
      "required_skills": [1, 2, 3],
      "created_by_student": 1,
      "created_by_supervisor": null
    }
    ```
  - **404 Not Found**: Thesis topic not found

### Update Thesis Topic

Updates an existing thesis topic. Only available to the team owner.

- **URL**: `/<id>/edit/`
- **Method**: `GET`, `PUT`, `PATCH`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the thesis topic
- **Request Body** (PUT - Full update):
  ```json
  {
    "title": "Updated Machine Learning Application in Healthcare",
    "title_kz": "Updated Денсаулық сақтаудағы машиналық оқыту қолданбасы",
    "title_ru": "Updated Применение машинного обучения в здравоохранении",
    "description": "Updated description for this thesis.",
    "required_skills": [1, 2, 3, 4]
  }
  ```
- **Request Body** (PATCH - Partial update):
  ```json
  {
    "title": "Updated Machine Learning Application in Healthcare",
    "description": "Updated description for this thesis."
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "title": "Updated Machine Learning Application in Healthcare",
      "title_kz": "Updated Денсаулық сақтаудағы машиналық оқыту қолданбасы",
      "title_ru": "Updated Применение машинного обучения в здравоохранении",
      "description": "Updated description for this thesis.",
      "required_skills": [1, 2, 3, 4],
      "created_by_student": 1,
      "created_by_supervisor": null
    }
    ```
  - **400 Bad Request**: Error details for invalid input
  - **403 Forbidden**: You do not own this topic
  - **404 Not Found**: Thesis topic not found

## Models

### ThesisTopic

The main model for thesis topics.

Fields:

- `id`: Auto-generated primary key
- `title`: Title of the thesis topic in English (required)
- `title_kz`: Title in Kazakh (optional)
- `title_ru`: Title in Russian (optional)
- `description`: Detailed description of the thesis topic (required)
- `required_skills`: Many-to-many relationship to Skill model
- `created_by_student`: One-to-one relationship to StudentProfile (null if created by supervisor)
- `created_by_supervisor`: Foreign key to SupervisorProfile (null if created by student)

## Business Logic

- When a thesis topic is created, a team is automatically created with the creator as the owner
- If a student creates a topic, they are automatically added as a member of the team
- If a supervisor creates a topic, they are automatically set as the team's supervisor
- Access control ensures only the team owner can edit the thesis topic
