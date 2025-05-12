# Chat API Documentation

This document provides details on the chat functionality endpoints available in the Chat API.

## Base URL

All endpoints are relative to the base API URL with prefix `/chat/`.

## Authentication

All endpoints in the Chat API use JWT (JSON Web Token) authentication. Each request requires a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

### List User Chats

Retrieves a list of all chats where the authenticated user is a participant.

- **URL**: `/chats/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "participants": [
          {
            "id": 2,
            "email": "user1@example.com",
            "role": "Student",
            "profile": {
              "first_name": "John",
              "last_name": "Doe",
              "photo": null
            }
          },
          {
            "id": 3,
            "email": "user2@example.com",
            "role": "Supervisor",
            "profile": {
              "first_name": "Jane",
              "last_name": "Smith",
              "photo": "http://example.com/media/profile_pics/user2.jpg"
            }
          }
        ],
        "created_at": "2025-05-10T15:30:45Z"
      }
    ]
    ```
  - **401 Unauthorized**: Authentication credentials not provided

### Get Chat Details

Retrieves details of a specific chat where the authenticated user is a participant.

- **URL**: `/chats/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the chat
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "participants": [
        {
          "id": 2,
          "email": "user1@example.com",
          "role": "Student",
          "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "photo": null
          }
        },
        {
          "id": 3,
          "email": "user2@example.com",
          "role": "Supervisor",
          "profile": {
            "first_name": "Jane",
            "last_name": "Smith",
            "photo": "http://example.com/media/profile_pics/user2.jpg"
          }
        }
      ],
      "created_at": "2025-05-10T15:30:45Z"
    }
    ```
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: Chat not found or user not a participant

### List Chat Messages

Retrieves all messages from a specific chat where the authenticated user is a participant.

- **URL**: `/chats/<id>/messages/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the chat
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "sender": {
          "id": 2,
          "email": "user1@example.com",
          "role": "Student",
          "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "photo": null
          }
        },
        "content": "Hello, how are you?",
        "timestamp": "2025-05-10T15:35:21Z",
        "is_read": true
      },
      {
        "id": 2,
        "sender": {
          "id": 3,
          "email": "user2@example.com",
          "role": "Supervisor",
          "profile": {
            "first_name": "Jane",
            "last_name": "Smith",
            "photo": "http://example.com/media/profile_pics/user2.jpg"
          }
        },
        "content": "I'm doing well, thanks! How about you?",
        "timestamp": "2025-05-10T15:36:05Z",
        "is_read": false
      }
    ]
    ```
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: Chat not found or user not a participant

### Create Message

Creates a new message in a specific chat where the authenticated user is a participant.

- **URL**: `/chats/<id>/messages/`
- **Method**: `POST`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the chat
- **Request Body**:
  ```json
  {
    "content": "This is my message"
  }
  ```
- **Response**:
  - **201 Created**:
    ```json
    {
      "id": 3,
      "sender": {
        "id": 2,
        "email": "user1@example.com",
        "role": "Student",
        "profile": {
          "first_name": "John",
          "last_name": "Doe",
          "photo": null
        }
      },
      "content": "This is my message",
      "timestamp": "2025-05-10T15:40:12Z",
      "is_read": false
    }
    ```
  - **400 Bad Request**: Invalid data
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: Chat not found or user not a participant

### Mark Message as Read

Updates a message to be marked as read.

- **URL**: `/messages/<id>/read/`
- **Method**: `PATCH`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the message
- **Response**:
  - **200 OK**:
    ```json
    {
      "status": "marked as read"
    }
    ```
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: Message not found or user not a participant in the associated chat

### Get User Online Status

Retrieves the online status and last activity timestamp of a specific user.

- **URL**: `/users/<id>/status/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the user
- **Response**:
  - **200 OK**:
    ```json
    {
      "is_online": true,
      "last_seen": "2025-05-10T15:45:30Z"
    }
    ```
  - **404 Not Found**: User status not found

### Start or Get Chat

Creates a new chat between the authenticated user and another user if one doesn't exist, or returns an existing chat if it does.

- **URL**: `/chats/start/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_id": 3
  }
  ```
- **Response**:
  - **200 OK** (if chat already exists):
    ```json
    {
      "id": 1,
      "participants": [
        {
          "id": 2,
          "email": "user1@example.com",
          "role": "Student",
          "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "photo": null
          }
        },
        {
          "id": 3,
          "email": "user2@example.com",
          "role": "Supervisor",
          "profile": {
            "first_name": "Jane",
            "last_name": "Smith",
            "photo": "http://example.com/media/profile_pics/user2.jpg"
          }
        }
      ],
      "created_at": "2025-05-10T15:30:45Z"
    }
    ```
  - **201 Created** (if new chat created): Same structure as 200 OK
  - **400 Bad Request**: Missing user_id
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: User not found

## Models

### Chat

The main model for conversations between users.

Fields:

- `participants`: Many-to-many relationship to User
- `created_at`: Timestamp when the chat was created

### Message

Model for individual messages within a chat.

Fields:

- `chat`: Foreign key to Chat
- `sender`: Foreign key to User
- `content`: Text content of the message
- `timestamp`: Timestamp when the message was sent
- `is_read`: Boolean indicating whether the message has been read

### UserStatus

Model for tracking user online status.

Fields:

- `user`: One-to-one relationship to User
- `is_online`: Boolean indicating whether the user is currently online
- `last_seen`: Timestamp of the user's last activity

## WebSocket Support

The chat system also supports real-time messaging through WebSockets. Connect to the WebSocket endpoint:

```
ws://<domain>/ws/chat/<chat_id>/
```

### WebSocket Messages

- **Message Format (Send)**:

  ```json
  {
    "type": "message",
    "content": "Hello there!"
  }
  ```

- **Message Format (Receive)**:
  ```json
  {
    "type": "message",
    "sender": {
      "id": 2,
      "email": "user1@example.com",
      "role": "Student",
      "profile": {
        "first_name": "John",
        "last_name": "Doe",
        "photo": null
      }
    },
    "content": "Hello there!",
    "timestamp": "2025-05-10T15:40:12Z",
    "is_read": false
  }
  ```
