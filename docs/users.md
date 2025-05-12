# Users API Documentation

This document provides details on the authentication and user management endpoints available in the User Management API.

## Base URL

All endpoints are relative to the base API URL.

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require a valid token included in the Authorization header as:

```
Authorization: Bearer <access_token>
```

## Endpoints

Creates a new user account.

- **URL**: `/register/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "confirm_password": "securepassword"
}
```

- **Response**:

  - **201 Created**:
    ```json
    {
      "message": "User registered successfully.",
      "role": "Student"
    }
    ```
  - **400 Bad Request**: Error details for invalid input

- **Notes**:
  - Role is automatically determined from the email format:
    - `-` in the username part: Dean Office
    - `.` in the username part: Supervisor
    - `_` in the username part: Student
    - Default: Student

### User Login

Authenticates a user and returns JWT tokens.

- **URL**: `/login/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

- **Response**:

  - **200 OK**:
    ```json
    {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
  - **401 Unauthorized**: Authentication failed

- **Security Features**:
  - Account lockout after 3 failed attempts
  - IP-based rate limiting
  - IP address tracking for login attempts
  - Progressive lockout durations (starting at 5 minutes, increasing by 5 minutes each time)
  - Login events are logged in the AccessLog model

### Refresh Access Token

Use a refresh token to obtain a new access token.

- **URL**: `/token/refresh/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

- **Response**:
  - **200 OK**:
    ```json
    {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
  - **401 Unauthorized**: Invalid refresh token

### User Logout

Records a user logout event.

- **URL**: `/logout/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**: None
- **Response**:

  - **200 OK**:
    ```json
    {
      "message": "Logout logged"
    }
    ```

- **Notes**:
  - This endpoint doesn't invalidate tokens, it only logs the logout event
  - The client should discard the tokens after logging out

### Get Current User Details

Returns the profile of the currently authenticated user.

- **URL**: `/me/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "role": "Student",
      "is_profile_completed": false
    }
    ```
  - **401 Unauthorized**: Authentication credentials not provided

### Request Password Reset

Sends a password reset email to the user's registered email address.

- **URL**: `/forgot-password/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:

```json
{
  "email": "user@example.com"
}
```

- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "If your email is registered, you will receive a password reset link."
    }
    ```
  - **500 Internal Server Error**: Failed to send email

### Confirm Password Reset

Validates the reset token and sets a new password for the user.

- **URL**: `/reset-password/<uidb64>/<token>/`
- **Method**: `PUT`
- **Authentication**: None
- **URL Parameters**:
  - `uidb64`: URL-safe base64 encoded user ID
  - `token`: Password reset token
- **Request Body**:

```json
{
  "new_password": "newsecurepassword",
  "confirm_password": "newsecurepassword"
}
```

- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Password has been reset successfully."
    }
    ```
  - **400 Bad Request**: Invalid token or user not found

## Models

### CustomUser

The main user model for authentication and user information.

Fields:

- `email`: Email address (unique)
- `role`: User role (Student, Supervisor, Dean Office)
- `is_profile_completed`: Boolean indicating if user has completed their profile
- `is_active`: Boolean indicating if the user account is active
- `is_staff`: Boolean indicating admin status
- `failed_login_attempts`: Count of consecutive failed login attempts
- `is_blocked`: Boolean indicating if account is currently blocked
- `blocked_until`: Timestamp when the block expires
- `block_duration`: Duration in minutes for the next block
- `last_failed_login`: Timestamp of the last failed login attempt
- `last_login_ip`: IP address of the last login

### AccessLog

Records user login and logout events.

Fields:

- `user`: Foreign key to CustomUser
- `action`: Action type (login, logout)
- `ip_address`: IP address of the user
- `user_agent`: User agent string from the request
- `timestamp`: Timestamp when the action occurred
