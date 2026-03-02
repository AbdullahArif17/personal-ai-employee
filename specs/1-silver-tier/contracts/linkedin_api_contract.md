# API Contract: LinkedIn Integration

## Overview
Contract for LinkedIn API integration in the Personal AI Employee system.

## Authentication
- OAuth2 with LinkedIn API v2
- Credentials stored in .env file
- Access token refresh handled automatically

## Endpoints

### POST /api/linkedin/create-post
**Description**: Create a new LinkedIn post
**Authentication**: Bearer token
**Request Body**:
```json
{
  "author": "string",
  "text": "string",
  "visibility": "enum(CONNECTIONS, PUBLIC)",
  "content": {
    "title": "string",
    "description": "string",
    "thumbnailUrl": "string",
    "originalUrl": "string"
  }
}
```

**Response**:
```json
{
  "success": "boolean",
  "post_id": "string",
  "created_at": "datetime"
}
```

### GET /api/linkedin/profile
**Description**: Retrieve user's LinkedIn profile information
**Authentication**: Bearer token

**Response**:
```json
{
  "profile": {
    "id": "string",
    "firstName": "string",
    "lastName": "string",
    "emailAddress": "string",
    "headline": "string"
  }
}
```

### GET /api/linkedin/rate-limit-status
**Description**: Check current rate limit status
**Authentication**: Bearer token

**Response**:
```json
{
  "current_usage": "integer",
  "limit_per_day": "integer",
  "reset_time": "datetime"
}
```

## Rate Limits
- Max 3 posts per day
- Complies with LinkedIn API v2 quotas
- Enforcement handled by application layer