# Vizzy Chat API - Quick Reference

## Quick Start

### 1. Run Migrations
```bash
cd python_deckoviz/common
python manage.py makemigrations vizzy_chat
python manage.py migrate
```

### 2. Run Tests
```bash
# Quick test run
python manage.py test apps.vizzy_chat.tests

# Or use test runner script
python run_vizzy_tests.py
```

### 3. Start Development Server
```bash
python manage.py runserver
```

### 4. Access API
Base URL: `http://localhost:8000/api/vizzy-chat/`

---

## API Endpoints Cheat Sheet

### Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response:
# {"access": "eyJ...", "refresh": "eyJ..."}
```

### Sessions
```bash
# List sessions
curl http://localhost:8000/api/vizzy-chat/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create session
curl -X POST http://localhost:8000/api/vizzy-chat/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode": "home", "title": "My Chat"}'

# Get session with messages
curl http://localhost:8000/api/vizzy-chat/sessions/{SESSION_ID}/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Close session
curl -X POST http://localhost:8000/api/vizzy-chat/sessions/{SESSION_ID}/close/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Messages
```bash
# List messages in session
curl http://localhost:8000/api/vizzy-chat/sessions/{SESSION_ID}/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create message
curl -X POST http://localhost:8000/api/vizzy-chat/sessions/{SESSION_ID}/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hello Vizzy!",
    "has_images": false
  }'

# Create message with emotional context
curl -X POST http://localhost:8000/api/vizzy-chat/sessions/{SESSION_ID}/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "assistant",
    "content": "Hello! How can I help?",
    "detected_emotion": "helpful",
    "mood_valence": 0.7,
    "mood_arousal": 0.5,
    "tokens_used": 120,
    "processing_time_ms": 850
  }'
```

### User Profile
```bash
# Get profile
curl http://localhost:8000/api/vizzy-chat/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update profile
curl -X PATCH http://localhost:8000/api/vizzy-chat/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "aesthetic_palette": {
      "primary_colors": ["#FF5733", "#C70039"],
      "style": "modern"
    },
    "device_context": {
      "room_type": "living_room",
      "display_schedule": "evening"
    }
  }'
```

### User Context (for FastAPI)
```bash
# Get comprehensive user context
curl http://localhost:8000/api/vizzy-chat/users/context/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response includes:
# - User profile data
# - Recent moods
# - Average mood valence
# - Context entries
# - Usage statistics
```

### Mood History
```bash
# List mood history
curl http://localhost:8000/api/vizzy-chat/mood-history/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Record mood
curl -X POST http://localhost:8000/api/vizzy-chat/mood-history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valence": 0.8,
    "arousal": 0.6,
    "emotion_label": "excited",
    "source": "explicit_input",
    "confidence": 0.95
  }'

# Analyze mood patterns
curl http://localhost:8000/api/vizzy-chat/mood-history/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Context Data
```bash
# List context data
curl http://localhost:8000/api/vizzy-chat/context-data/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by type
curl "http://localhost:8000/api/vizzy-chat/context-data/?context_type=preference" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create context
curl -X POST http://localhost:8000/api/vizzy-chat/context-data/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_type": "preference",
    "key": "favorite_artist",
    "value": {"name": "Van Gogh", "period": "Post-Impressionism"}
  }'

# Delete context
curl -X DELETE http://localhost:8000/api/vizzy-chat/context-data/{CONTEXT_ID}/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Python Client Examples

### Create Session and Send Message
```python
import requests

BASE_URL = "http://localhost:8000/api/vizzy-chat"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create session
session_data = {
    "mode": "home",
    "title": "Design Discussion"
}
response = requests.post(f"{BASE_URL}/sessions/", json=session_data, headers=headers)
session = response.json()
session_id = session['id']

# Send message
message_data = {
    "role": "user",
    "content": "Can you help me design a modern poster?"
}
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/messages/",
    json=message_data,
    headers=headers
)
message = response.json()
print(f"Message created: {message['id']}")
```

### Get User Context for AI Processing
```python
import requests

BASE_URL = "http://localhost:8000/api/vizzy-chat"
TOKEN = "your_jwt_token_here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get comprehensive context
response = requests.get(f"{BASE_URL}/users/context/", headers=headers)
context = response.json()

print(f"User: {context['email']}")
print(f"Total Sessions: {context['total_sessions']}")
print(f"Average Mood: {context['average_mood_valence']}")
print(f"Recent Moods: {len(context['recent_moods'])}")
print(f"Aesthetic Style: {context['aesthetic_palette'].get('style')}")
```

---

## Common Query Parameters

### Pagination
```bash
# Custom page size
?page_size=50

# Specific page
?page=2

# Combine
?page=2&page_size=50
```

### Filtering
```bash
# Sessions: active only
?active_only=true

# Context data: by type
?context_type=preference
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (permission denied) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Common Error Responses

### Authentication Error
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Validation Error
```json
{
  "mood_valence": ["Ensure this value is less than or equal to 1."]
}
```

### Not Found
```json
{
  "detail": "Not found."
}
```

---

## Testing Quick Commands

```bash
# Run all tests
python manage.py test apps.vizzy_chat.tests

# Run specific test file
python manage.py test apps.vizzy_chat.tests.test_views_sessions

# Run with verbose output
python manage.py test apps.vizzy_chat.tests --verbosity=2

# Run with coverage
coverage run --source='apps/vizzy_chat' manage.py test apps.vizzy_chat.tests
coverage report

# Use test runner script
python run_vizzy_tests.py
```

---

## Database Commands

```bash
# Make migrations
python manage.py makemigrations vizzy_chat

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Shell Examples
```python
# In Django shell
from django.contrib.auth import get_user_model
from apps.vizzy_chat.models import VizzyChatSession, VizzyChatMessage

User = get_user_model()

# Get user
user = User.objects.get(email='test@example.com')

# Create session
session = VizzyChatSession.objects.create(
    user=user,
    title='Shell Test',
    mode='home'
)

# Create message
message = VizzyChatMessage.objects.create(
    session=session,
    role='user',
    content='Test from shell'
)

# Query sessions
sessions = VizzyChatSession.objects.user_sessions(user)
print(f"User has {len(sessions)} sessions")
```

---

## Admin Interface

Access: `http://localhost:8000/admin/vizzy_chat/`

Available admin panels:
- Vizzy Chat Sessions
- Vizzy Chat Messages
- Vizzy User Profiles
- Vizzy Mood Histories
- Vizzy Context Data

---

## OpenAPI Documentation

Access: `http://localhost:8000/api/schema/swagger-ui/`

Interactive API documentation with:
- All endpoints
- Request/response schemas
- Try-it-out functionality
- Authentication testing

---

## Production Checklist

Before deploying:

- [ ] All tests passing (`python manage.py test apps.vizzy_chat.tests`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Redis configured for caching
- [ ] JWT token lifetimes set appropriately
- [ ] Rate limiting configured
- [ ] CORS settings configured
- [ ] Database connection pooling enabled
- [ ] Monitoring/logging configured
- [ ] Environment variables set
- [ ] Static files collected

---

## Support & Documentation

- Full Documentation: [README.md](README.md)
- Testing Guide: [TESTING.md](TESTING.md)
- Phase 1.2 Summary: [PHASE_1.2_COMPLETE.md](PHASE_1.2_COMPLETE.md)
- Repository Overview: [REPOSITORY_OVERVIEW.md](../../../REPOSITORY_OVERVIEW.md)

---

**Quick Reference v1.0** | Phase 1.2 Complete ✅
