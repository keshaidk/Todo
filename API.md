# API Documentation

## Authentication

All API endpoints require Telegram WebApp authentication via the `X-Init-Data` header.

**Example**:
```bash
curl http://localhost:8000/api/tasks \
  -H "X-Init-Data: <telegram_init_data>"
```

## Health Check

### GET /health

Check if the API is running.

**Response** (200 OK):
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Tasks

### GET /tasks

Get all tasks for the authenticated user.

**Query Parameters**:
- `completed` (boolean, optional): Filter by completion status
- `skip` (integer, default: 0): Pagination offset
- `limit` (integer, default: 100): Items per page (max: 1000)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "text": "Buy groceries",
      "completed": false,
      "reminder_date": "2024-12-25T10:00:00",
      "created_at": "2024-12-20T15:30:00",
      "updated_at": "2024-12-20T15:30:00"
    }
  ],
  "total": 10,
  "completed_count": 3
}
```

**Errors**:
- 401: Missing or invalid authentication
- 500: Server error

---

### POST /tasks

Create a new task.

**Request Body**:
```json
{
  "text": "Buy milk",
  "reminder_date": "2024-12-25T10:00:00" // Optional
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "text": "Buy milk",
  "completed": false,
  "reminder_date": "2024-12-25T10:00:00",
  "created_at": "2024-12-20T15:30:00",
  "updated_at": "2024-12-20T15:30:00"
}
```

**Validation**:
- `text`: Required, 1-500 characters
- `reminder_date`: Optional, valid ISO datetime

**Errors**:
- 422: Validation error
- 401: Missing or invalid authentication
- 500: Server error

---

### GET /tasks/{task_id}

Get a specific task.

**Path Parameters**:
- `task_id` (integer): Task ID

**Response** (200 OK):
```json
{
  "id": 1,
  "text": "Buy milk",
  "completed": false,
  "reminder_date": "2024-12-25T10:00:00",
  "created_at": "2024-12-20T15:30:00",
  "updated_at": "2024-12-20T15:30:00"
}
```

**Errors**:
- 404: Task not found
- 401: Missing or invalid authentication
- 500: Server error

---

### PUT /tasks/{task_id}

Update a task.

**Path Parameters**:
- `task_id` (integer): Task ID

**Request Body** (all optional):
```json
{
  "text": "New task text",
  "completed": true,
  "reminder_date": "2024-12-26T10:00:00"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "text": "New task text",
  "completed": true,
  "reminder_date": "2024-12-26T10:00:00",
  "created_at": "2024-12-20T15:30:00",
  "updated_at": "2024-12-20T16:45:00"
}
```

**Errors**:
- 404: Task not found
- 422: Validation error
- 401: Missing or invalid authentication
- 500: Server error

---

### DELETE /tasks/{task_id}

Delete a task.

**Path Parameters**:
- `task_id` (integer): Task ID

**Response** (204 No Content):
No response body.

**Errors**:
- 404: Task not found
- 401: Missing or invalid authentication
- 500: Server error

---

### POST /tasks/{task_id}/complete

Mark a task as completed.

**Path Parameters**:
- `task_id` (integer): Task ID

**Response** (200 OK):
```json
{
  "id": 1,
  "text": "Buy milk",
  "completed": true,
  "reminder_date": "2024-12-25T10:00:00",
  "created_at": "2024-12-20T15:30:00",
  "updated_at": "2024-12-20T16:45:00"
}
```

**Errors**:
- 404: Task not found
- 401: Missing or invalid authentication
- 500: Server error

---

## Error Responses

All errors return JSON with `detail` field:

```json
{
  "detail": "Task not found",
  "error_code": "NOT_FOUND"
}
```

### Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no content
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation failed
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently no built-in rate limiting, but it's recommended to use a reverse proxy (nginx, Cloudflare) for protection.

---

## Examples

### JavaScript/TypeScript

```typescript
// Get all tasks
const response = await fetch('http://localhost:8000/api/tasks', {
  headers: {
    'X-Init-Data': tg.initData,
  },
});
const { tasks } = await response.json();

// Create task
const newTask = await fetch('http://localhost:8000/api/tasks', {
  method: 'POST',
  headers: {
    'X-Init-Data': tg.initData,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Buy milk',
    reminder_date: '2024-12-25T10:00:00',
  }),
});
const task = await newTask.json();
```

### Python/httpx

```python
import httpx

client = httpx.AsyncClient()

# Get tasks
response = await client.get(
    'http://localhost:8000/api/tasks',
    headers={'X-Init-Data': init_data},
)
tasks_data = response.json()

# Create task
response = await client.post(
    'http://localhost:8000/api/tasks',
    headers={
        'X-Init-Data': init_data,
        'Content-Type': 'application/json',
    },
    json={
        'text': 'Buy milk',
        'reminder_date': '2024-12-25T10:00:00',
    },
)
task = response.json()
```

### cURL

```bash
# Get tasks
curl -H "X-Init-Data: YOUR_INIT_DATA" \
     http://localhost:8000/api/tasks

# Create task
curl -X POST \
     -H "X-Init-Data: YOUR_INIT_DATA" \
     -H "Content-Type: application/json" \
     -d '{"text":"Buy milk"}' \
     http://localhost:8000/api/tasks

# Complete task
curl -X POST \
     -H "X-Init-Data: YOUR_INIT_DATA" \
     http://localhost:8000/api/tasks/1/complete

# Delete task
curl -X DELETE \
     -H "X-Init-Data: YOUR_INIT_DATA" \
     http://localhost:8000/api/tasks/1
```
