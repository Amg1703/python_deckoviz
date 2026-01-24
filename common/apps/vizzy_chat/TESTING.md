# Vizzy Chat API Testing Guide

## Overview

This document provides comprehensive guidance for testing the Vizzy Chat API (Phase 1.2).

## Test Structure

```
tests/
├── __init__.py
├── utils.py                          # Test utilities and fixtures
├── test_views_sessions.py            # Session CRUD tests (30+ test cases)
├── test_views_messages.py            # Message tests (25+ test cases)
├── test_views_profile.py             # Profile & context tests (20+ test cases)
└── test_views_mood_context.py        # Mood & context data tests (25+ test cases)
```

**Total Test Cases: 100+**

## Running Tests

### Run All Vizzy Chat Tests

```bash
cd python_deckoviz/common
python manage.py test apps.vizzy_chat.tests
```

### Run Specific Test Files

```bash
# Session tests only
python manage.py test apps.vizzy_chat.tests.test_views_sessions

# Message tests only
python manage.py test apps.vizzy_chat.tests.test_views_messages

# Profile tests only
python manage.py test apps.vizzy_chat.tests.test_views_profile

# Mood & context tests only
python manage.py test apps.vizzy_chat.tests.test_views_mood_context
```

### Run Specific Test Classes

```bash
python manage.py test apps.vizzy_chat.tests.test_views_sessions.VizzyChatSessionViewSetTestCase

python manage.py test apps.vizzy_chat.tests.test_views_messages.VizzyChatMessageViewSetTestCase
```

### Run Specific Test Methods

```bash
python manage.py test apps.vizzy_chat.tests.test_views_sessions.VizzyChatSessionViewSetTestCase.test_create_session_home_mode

python manage.py test apps.vizzy_chat.tests.test_views_messages.VizzyChatMessageViewSetTestCase.test_create_user_message
```

### Run with Verbose Output

```bash
python manage.py test apps.vizzy_chat.tests --verbosity=2
```

### Run with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='apps/vizzy_chat' manage.py test apps.vizzy_chat.tests

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Run with Parallel Execution

```bash
# Run tests in parallel (faster)
python manage.py test apps.vizzy_chat.tests --parallel
```

## Test Coverage by Feature

### 1. Session Management (30 tests)

**File:** `test_views_sessions.py`

- ✅ List sessions (authenticated/unauthenticated)
- ✅ Filter sessions (active only, include inactive)
- ✅ Retrieve session detail (with messages)
- ✅ Create sessions (home/enterprise mode)
- ✅ Update sessions (title, mode)
- ✅ Close sessions
- ✅ Delete sessions
- ✅ Pagination
- ✅ Permission checks (ownership validation)
- ✅ User profile integration

**Key Test Cases:**
- `test_list_sessions_authenticated` - Verify authenticated user can list their sessions
- `test_create_session_home_mode` - Test session creation
- `test_close_session_action` - Test closing active sessions
- `test_retrieve_session_not_owned` - Security: users can't access others' sessions
- `test_session_list_pagination` - Pagination works correctly

### 2. Message Management (25 tests)

**File:** `test_views_messages.py`

- ✅ List messages in session
- ✅ Retrieve message detail
- ✅ Create user messages
- ✅ Create assistant messages
- ✅ Multimodal messages (with images)
- ✅ Emotional context tracking
- ✅ Performance metrics tracking
- ✅ Validation (role, mood values)
- ✅ Session ownership checks
- ✅ Message immutability

**Key Test Cases:**
- `test_create_user_message` - Create basic user message
- `test_create_message_with_images` - Multimodal support
- `test_create_message_invalid_mood_valence` - Validation logic
- `test_message_ordering` - Messages ordered by timestamp
- `test_cannot_update_message` - Messages are immutable

### 3. User Profile & Context (20 tests)

**File:** `test_views_profile.py`

- ✅ Get user profile (auto-creation)
- ✅ Update aesthetic palette
- ✅ Update mood map
- ✅ Update story markers
- ✅ Update device context
- ✅ Read-only field protection
- ✅ Get comprehensive user context
- ✅ Context includes recent moods
- ✅ Context includes context entries
- ✅ Average mood calculation

**Key Test Cases:**
- `test_get_user_profile_auto_created` - Profile auto-creation
- `test_update_aesthetic_palette` - Update user preferences
- `test_get_user_context_authenticated` - Comprehensive context retrieval
- `test_get_user_context_includes_recent_moods` - Context aggregation

### 4. Mood History & Context Data (25 tests)

**File:** `test_views_mood_context.py`

- ✅ List mood history
- ✅ Create mood entries
- ✅ Validate mood values (valence, arousal, confidence)
- ✅ Mood pattern analysis
- ✅ List context data
- ✅ Filter context by type
- ✅ Create context data
- ✅ Delete context data
- ✅ Access count tracking
- ✅ Ownership validation

**Key Test Cases:**
- `test_create_mood_history_entry` - Record mood data
- `test_analyze_mood_patterns` - Mood analysis endpoint
- `test_create_context_data_entry` - Store context data
- `test_context_data_access_count_increment` - Access tracking

## Test Data Setup

### Using Test Utilities

```python
from apps.vizzy_chat.tests.utils import VizzyChatTestMixin, TestDataFactory

class MyTestCase(VizzyChatTestMixin, APITestCase):
    def setUp(self):
        # Quick setup with mixin
        self.setup_test_user()
        self.setup_test_session()
        self.setup_test_messages(count=10)
        self.authenticate_client()
```

### Using Test Factory

```python
from apps.vizzy_chat.tests.utils import TestDataFactory

factory = TestDataFactory()
user = factory.create_user()
session = factory.create_session(user)
messages = factory.create_messages(session, count=5)
```

## Expected Test Results

### Success Criteria

All tests should pass with:
- ✅ 100+ test cases passing
- ✅ 0 failures
- ✅ 0 errors
- ✅ Test coverage > 90%
- ✅ All API endpoints tested
- ✅ All permission checks validated
- ✅ All validation logic tested

### Sample Output

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..................................................................................................
----------------------------------------------------------------------
Ran 100 tests in 15.432s

OK
Destroying test database for alias 'default'...
```

## Testing Best Practices

### 1. Isolate Test Data

Each test should create its own data and not rely on other tests:

```python
def test_something(self):
    # Create test data
    user = User.objects.create_user(...)
    session = VizzyChatSession.objects.create(...)
    
    # Run test
    response = self.client.get(...)
    
    # Assert
    self.assertEqual(...)
```

### 2. Clean Authentication

Always authenticate before testing authenticated endpoints:

```python
def test_authenticated_endpoint(self):
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
```

### 3. Test Edge Cases

Test boundary conditions and error cases:

```python
def test_invalid_mood_valence(self):
    data = {'mood_valence': 1.5}  # Out of range [-1, 1]
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 400)
    self.assertIn('mood_valence', response.data)
```

### 4. Test Permissions

Always verify ownership and permission checks:

```python
def test_cannot_access_others_data(self):
    # user1 tries to access user2's session
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
    response = self.client.get(f'/api/vizzy-chat/sessions/{user2_session_id}/')
    self.assertEqual(response.status_code, 404)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Vizzy Chat Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd python_deckoviz/common
          python manage.py test apps.vizzy_chat.tests --verbosity=2
```

## Common Issues & Solutions

### Issue: Tests fail with "Table doesn't exist"

**Solution:** Run migrations before tests
```bash
python manage.py migrate
python manage.py test apps.vizzy_chat.tests
```

### Issue: Authentication errors

**Solution:** Check JWT configuration in settings
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

### Issue: Import errors

**Solution:** Ensure app is installed
```python
# settings.py
INSTALLED_APPS = [
    ...
    'apps.vizzy_chat',
]
```

## Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class VizzyChatUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/api/token/", {
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()['access']
    
    @task
    def list_sessions(self):
        self.client.get(
            "/api/vizzy-chat/sessions/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def create_message(self):
        self.client.post(
            f"/api/vizzy-chat/sessions/{self.session_id}/messages/",
            json={
                "role": "user",
                "content": "Test message"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

Run load test:
```bash
locust -f locustfile.py --host=http://168.231.112.236:8000
```

## Next Steps

After all tests pass:

1. ✅ **Phase 1.1 Complete** - Django models & admin
2. ✅ **Phase 1.2 Complete** - REST API & tests
3. ⏭️ **Phase 1.3** - FastAPI WebSocket integration
4. ⏭️ **Phase 1.4** - End-to-end integration testing

## Support

For issues or questions:
1. Check test output for specific error messages
2. Review test code for expected behavior
3. Verify database migrations are applied
4. Check authentication configuration
5. Review API endpoint URLs and namespaces
