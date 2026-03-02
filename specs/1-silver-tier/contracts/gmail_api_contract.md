# API Contract: Gmail Integration

## Overview
Contract for Gmail API integration in the Personal AI Employee system.

## Authentication
- OAuth2 with Gmail API
- Credentials stored in .env file
- Token refresh handled automatically

## Endpoints

### GET /api/gmail/unread
**Description**: Retrieve unread emails from Gmail account
**Authentication**: OAuth2 token
**Parameters**:
- `max_results` (integer, optional): Maximum number of emails to return (default: 10)
- `importance_threshold` (string, optional): Filter by importance level (default: all)

**Response**:
```json
{
  "emails": [
    {
      "id": "string",
      "sender": "string",
      "subject": "string",
      "date_received": "datetime",
      "body_snippet": "string",
      "importance_level": "enum(low, medium, high, critical)"
    }
  ],
  "next_page_token": "string"
}
```

### POST /api/gmail/mark-read
**Description**: Mark emails as read in Gmail
**Authentication**: OAuth2 token
**Request Body**:
```json
{
  "email_ids": ["string"]
}
```

**Response**:
```json
{
  "success": "boolean",
  "processed_count": "integer"
}
```

### POST /api/gmail/send-reply
**Description**: Send email reply via Gmail
**Authentication**: OAuth2 token
**Request Body**:
```json
{
  "to": "string",
  "subject": "string",
  "body": "string",
  "thread_id": "string"
}
```

**Response**:
```json
{
  "success": "boolean",
  "message_id": "string"
}
```

## Rate Limits
- Max 10 emails processed per run
- Complies with Gmail API quotas