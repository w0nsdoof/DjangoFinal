# Notifications API Documentation

This document provides details on the notification system endpoints available in the Notifications API.

## Base URL

All endpoints are relative to the base API URL with prefix `/notifications/`.

## Authentication

All endpoints in the Notifications API use JWT (JSON Web Token) authentication. Each request requires a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

### List User Notifications

Retrieves a list of all notifications for the authenticated user.

- **URL**: `/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "message": "Your join request has been accepted",
        "is_read": false,
        "timestamp": "2025-05-10T14:30:10Z"
      },
      {
        "id": 2,
        "message": "New message from Jane Smith",
        "is_read": true,
        "timestamp": "2025-05-09T11:20:45Z"
      }
    ]
    ```
  - **401 Unauthorized**: Authentication credentials not provided

### Get Unread Notification Count

Retrieves the number of unread notifications for the authenticated user.

- **URL**: `/unread/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    {
      "unread_count": 3
    }
    ```
  - **401 Unauthorized**: Authentication credentials not provided

### Mark All Notifications as Read

Updates all unread notifications of the authenticated user to be marked as read.

- **URL**: `/mark-all-as-read/`
- **Method**: `PATCH`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    {
      "status": "all marked as read"
    }
    ```
  - **401 Unauthorized**: Authentication credentials not provided

### Delete a Notification

Removes a specific notification belonging to the authenticated user.

- **URL**: `/<id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **URL Parameters**:
  - `id`: ID of the notification
- **Response**:
  - **204 No Content**: Successfully deleted
  - **401 Unauthorized**: Authentication credentials not provided
  - **404 Not Found**: Notification not found

## Model

### Notification

The model for user notifications.

Fields:

- `user`: Foreign key to User (notification recipient)
- `message`: Text content of the notification
- `is_read`: Boolean indicating whether the notification has been read
- `timestamp`: Timestamp when the notification was created

## WebSocket Support

The notification system also supports real-time notifications through WebSockets. Connect to the WebSocket endpoint:

```
ws://<domain>/ws/notifications/
```

### WebSocket Messages (Receive)

- **Notification Format**:
  ```json
  {
    "type": "notification",
    "id": 3,
    "message": "Your supervisor request has been accepted",
    "is_read": false,
    "timestamp": "2025-05-12T09:15:30Z"
  }
  ```

## Notification Events

The system generates notifications for the following events:

1. **Team Management**

   - Join request received
   - Join request accepted/rejected
   - Member added/removed from team
   - Team approved by dean office

2. **Supervisor Management**

   - Supervisor request received
   - Supervisor request accepted/rejected

3. **Chat**

   - New message received

4. **System**
   - Account status changes
   - Password reset confirmation
