# Leadex API Documentation

> **Base URL**: `http://your-domain.com/api`
>
> **Authentication**: JWT Bearer Token (for admin endpoints) or Access Token (for client endpoints)

## Table of Contents

- [Authentication](#authentication)
- [Admin Endpoints](#admin-endpoints)
  - [Auth](#admin-auth)
  - [Dashboard & Stats](#dashboard--stats)
  - [Lead Management](#lead-management)
  - [Client Management](#client-management)
  - [Reports](#reports)
  - [Analytics](#analytics)
  - [Webhooks](#webhooks)
- [Client Portal Endpoints](#client-portal-endpoints)
- [Public Endpoints](#public-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Authentication

### Admin Authentication

**POST** `/admin/auth/login`

Login as admin user and receive JWT token.

**Request Body:**
```json
{
  "email": "admin@leadex.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Usage:**
Include token in subsequent requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Client Authentication

**POST** `/client/auth/login`

Login as client using access token.

**Request Body:**
```json
{
  "token": "client_access_token",
  "password": "optional_password"
}
```

---

## Admin Endpoints

### Admin Auth

#### GET `/admin/auth/me`
Get current admin user information.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "id": "uuid",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00"
}
```

---

### Dashboard & Stats

#### GET `/admin/stats/dashboard`
Get comprehensive dashboard statistics.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "overview": {
    "total_leads": 1250,
    "today_leads": 45,
    "week_leads": 312,
    "total_clients": 8,
    "active_clients": 6,
    "total_deliveries": 1180,
    "successful_deliveries": 1156,
    "delivery_success_rate": 98.0,
    "stored_leads": 15,
    "pending_batches": 2
  },
  "leads_by_status": {
    "NEW": 15,
    "DELIVERED": 1200,
    "FAILED": 35
  },
  "clients": [
    {
      "id": "uuid",
      "name": "Client Name",
      "percentage": 50.0,
      "credits_balance": 1000.0,
      "status": "active",
      "assigned_leads": 625,
      "successful_deliveries": 610,
      "delivery_rate": 97.6
    }
  ]
}
```

---

### Lead Management

#### GET `/admin/leads/`
List all leads with pagination and filters.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 100000) - Records per page
- `status` (string, optional) - Filter by status (NEW, DELIVERED, FAILED)
- `client_id` (uuid, optional) - Filter by client ID
- `search` (string, optional) - Search in mobile, name, email

**Response:**
```json
{
  "leads": [
    {
      "id": "uuid",
      "mobile": "+1234567890",
      "name": "John Doe",
      "email": "john@example.com",
      "status": "DELIVERED",
      "created_at": "2025-01-01T10:30:00",
      "updated_at": "2025-01-01T10:31:00",
      "client": {
        "id": "uuid",
        "name": "Client Name"
      },
      "delivery_count": 1,
      "ip": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "referrer": "https://example.com",
      "geo": {
        "country": "US",
        "country_name": "United States",
        "city": "New York",
        "lat": 40.7128,
        "lon": -74.0060
      },
      "utm": {
        "source": "google",
        "medium": "cpc",
        "campaign": "spring_sale"
      }
    }
  ],
  "total": 1250
}
```

#### GET `/admin/leads/{lead_id}`
Get detailed information about a specific lead.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "id": "uuid",
  "mobile": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "status": "DELIVERED",
  "created_at": "2025-01-01T10:30:00",
  "updated_at": "2025-01-01T10:31:00",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "referrer": "https://example.com",
  "geo": { /* geo data */ },
  "utm": { /* utm data */ },
  "delivery_history": [
    {
      "id": "uuid",
      "client": {
        "id": "uuid",
        "name": "Client Name"
      },
      "delivery_method": "webhook",
      "success": true,
      "attempt_number": 1,
      "response_status": "200",
      "created_at": "2025-01-01T10:31:00"
    }
  ]
}
```

#### POST `/admin/leads/{lead_id}/resend`
Manually resend a lead to a specific client.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "client_id": "uuid"
}
```

**Response:**
```json
{
  "message": "Lead resent successfully",
  "delivery_id": "uuid"
}
```

#### DELETE `/admin/leads/{lead_id}`
Delete a specific lead.

**Headers:** `Authorization: Bearer {token}`

**Response:** `204 No Content`

#### POST `/admin/leads/bulk/delete`
Delete multiple leads at once.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "lead_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "deleted_count": 3,
  "message": "3 leads deleted successfully"
}
```

---

### Client Management

#### GET `/admin/clients/`
List all clients.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `status_filter` (string, optional) - "active" or "inactive"

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Client Name",
    "email": "client@example.com",
    "phone_number": "+1234567890",
    "percentage": 50.0,
    "credits_balance": 1000.0,
    "status": "active",
    "created_at": "2025-01-01T00:00:00",
    "password_protected_link_token": "secure_token",
    "password": "plain_password",
    "accept_webhook": true,
    "accept_email": false,
    "accept_sms": false,
    "accept_sheets": true,
    "webhook_url": "https://client.com/webhook",
    "google_sheet_id": "sheet_id_123"
  }
]
```

#### GET `/admin/clients/{client_id}`
Get detailed client information.

**Headers:** `Authorization: Bearer {token}`

**Response:** Same structure as list item above.

#### POST `/admin/clients/`
Create a new client.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "New Client",
  "email": "newclient@example.com",
  "phone_number": "+1234567890",
  "percentage": 30.0,
  "credits_balance": 500.0,
  "credit_cost_per_lead": 1.0,
  "webhook_url": "https://client.com/webhook",
  "google_sheet_id": "optional_sheet_id",
  "accept_webhook": true,
  "accept_email": false,
  "accept_sms": false,
  "accept_sheets": false,
  "priority_order": 0
}
```

**Response:** Client object (same as GET response) with status `201 Created`

#### PUT `/admin/clients/{client_id}`
Update an existing client.

**Headers:** `Authorization: Bearer {token}`

**Request Body:** Same as POST, but all fields optional.

**Response:** Updated client object

#### DELETE `/admin/clients/{client_id}`
Delete a client.

**Headers:** `Authorization: Bearer {token}`

**Response:** `204 No Content`

#### POST `/admin/clients/{client_id}/credits`
Add credits to a client's balance.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `credits` (float, required) - Amount to add

**Response:**
```json
{
  "message": "Credits added successfully",
  "new_balance": 1500.0
}
```

---

### Reports

All report endpoints return data in this format:

**Response Structure:**
```json
{
  "report_type": "string",
  "generated_at": "2025-01-01T12:00:00",
  "data": { /* report-specific data */ }
}
```

#### GET `/admin/reports/quick/lead-summary`
Generate lead summary report.

**Headers:** `Authorization: Bearer {token}`

**Response Data:**
```json
{
  "total_leads": 1250,
  "status_breakdown": {
    "NEW": 15,
    "DELIVERED": 1200,
    "FAILED": 35
  },
  "leads_by_client": [
    {
      "client": "Client Name",
      "count": 625
    }
  ],
  "recent_leads": [
    {
      "date": "2025-01-01",
      "count": 45
    }
  ]
}
```

#### GET `/admin/reports/quick/performance`
Generate performance report with success rates.

**Headers:** `Authorization: Bearer {token}`

**Response Data:**
```json
{
  "client_performance": [
    {
      "client": "Client Name",
      "total_deliveries": 625,
      "successful": 610,
      "success_rate": 97.6
    }
  ],
  "delivery_methods": [
    {
      "method": "webhook",
      "total": 800,
      "successful": 785,
      "success_rate": 98.13
    }
  ]
}
```

#### GET `/admin/reports/quick/revenue`
Generate revenue and credits report.

**Headers:** `Authorization: Bearer {token}`

**Response Data:**
```json
{
  "total_revenue": 12500.0,
  "total_credits_balance": 3500.0,
  "clients": [
    {
      "client": "Client Name",
      "credits_balance": 1000.0,
      "cost_per_lead": 1.0,
      "total_deliveries": 625,
      "total_spent": 625.0,
      "status": "active"
    }
  ]
}
```

#### GET `/admin/reports/quick/clients`
Generate detailed client report.

**Headers:** `Authorization: Bearer {token}`

**Response Data:**
```json
{
  "total_clients": 8,
  "active_clients": 6,
  "clients": [
    {
      "id": "uuid",
      "name": "Client Name",
      "email": "client@example.com",
      "phone": "+1234567890",
      "status": "active",
      "credits_balance": 1000.0,
      "cost_per_lead": 1.0,
      "delivery_methods": {
        "webhook": true,
        "sheets": true,
        "email": false,
        "sms": false
      },
      "total_deliveries": 625,
      "successful_deliveries": 610,
      "success_rate": 97.6,
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

#### GET `/admin/reports/quick/webhooks`
Generate webhook activity report.

**Headers:** `Authorization: Bearer {token}`

**Response Data:**
```json
{
  "webhook_stats_by_client": [
    {
      "client": "Client Name",
      "total": 400,
      "successful": 392,
      "success_rate": 98.0
    }
  ],
  "daily_activity": [
    {
      "date": "2025-01-01",
      "total": 45,
      "successful": 44
    }
  ]
}
```

---

### Analytics

#### GET `/admin/analytics/overview`
Get analytics overview.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `start_date` (ISO date, optional)
- `end_date` (ISO date, optional)

#### GET `/admin/analytics/conversion-funnel`
Get conversion funnel data.

**Headers:** `Authorization: Bearer {token}`

#### GET `/admin/analytics/client-performance`
Get detailed client performance analytics.

**Headers:** `Authorization: Bearer {token}`

---

## Client Portal Endpoints

### GET `/client/leads/`
Get leads assigned to the authenticated client.

**Headers:** `Authorization: Bearer {client_token}`

**Response:**
```json
[
  {
    "id": "uuid",
    "mobile": "+1234567890",
    "name": "John Doe",
    "email": "john@example.com",
    "ip": "192.168.1.1",
    "created_at": "2025-01-01T10:30:00"
  }
]
```

### GET `/client/stats/`
Get client statistics.

**Headers:** `Authorization: Bearer {client_token}`

**Response:**
```json
{
  "total_leads": 625,
  "today_leads": 23,
  "week_leads": 156,
  "credits_balance": 1000.0,
  "success_rate": 97.6
}
```

---

## Public Endpoints

### POST `/public/submit`
Submit a new lead from landing page.

**No authentication required**

**Request Body:**
```json
{
  "mobile": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "landing_id": "uuid",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "spring_sale"
}
```

**Response:**
```json
{
  "message": "Lead submitted successfully",
  "lead_id": "uuid",
  "status": "queued"
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation failed)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

**Example Error Response:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

---

## Rate Limiting

**Default Limits:**
- Anonymous: 60 requests/minute
- Authenticated Admin: 120 requests/minute
- Authenticated Client: 100 requests/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 115
X-RateLimit-Reset: 1640995200
```

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

---

## Interactive Documentation

For interactive API testing and exploration:

- **Swagger UI**: `http://your-domain.com/docs`
- **ReDoc**: `http://your-domain.com/redoc`
- **OpenAPI JSON**: `http://your-domain.com/openapi.json`

---

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in local storage without encryption)
3. **Implement token refresh logic**
4. **Handle rate limits gracefully** with exponential backoff
5. **Validate data on client side** before submission
6. **Use pagination** for large data sets
7. **Cache responses** when appropriate
8. **Monitor API usage** and errors

---

## Support

For issues, questions, or feature requests:
- GitHub: https://github.com/hamedniavand/Leadex/issues
- Email: support@leadex.com

---

**Last Updated**: December 2025
**API Version**: 1.0
**Status**: Production Ready ✅
