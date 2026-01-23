# Deckoviz Backend Repository - Complete Overview

## 📋 Table of Contents
1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Architecture](#architecture)
4. [Key Components](#key-components)
5. [Technology Stack](#technology-stack)
6. [API Services](#api-services)
7. [Database Schema](#database-schema)
8. [Authentication & Security](#authentication--security)
9. [Deployment](#deployment)
10. [Development Setup](#development-setup)

---

## 🎯 Overview

**Deckoviz** is a next-generation AI-powered art and decor device platform that transforms living and working spaces through dynamic, intelligent visual experiences. The backend powers a sophisticated ecosystem that includes:

- **Smart Display Devices**: Large-format ambient screens for walls and installations
- **AI Engine**: Deep personalization with generative AI for art and visuals
- **Companion App**: Mobile application for device control and content management
- **Content Ecosystem**: Curated art collections, themed scenes, and memory reels

### Project Status
⚠️ **NOT Production-Ready** - See [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) for critical issues

---

## 📁 Folder Structure

```
python_deckoviz/
│
├── api/                              # FastAPI WebSocket & Real-time Services
│   ├── core/                         # Core utilities
│   │   ├── __init__.py
│   │   └── logger.py                 # Logging configuration
│   ├── databases/
│   │   ├── __init__.py
│   │   └── configs.py                # Redis and database configs
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── logging.py                # Request logging middleware
│   ├── routers/                      # API route handlers
│   │   ├── curations.py              # Content curation endpoints
│   │   ├── device_pairing.py         # Device pairing via QR codes
│   │   ├── device_ws.py              # Device WebSocket connections
│   │   ├── qr_code_redis.py          # QR code management
│   │   ├── rooms.py                  # Room/session management
│   │   └── websocket.py              # WebSocket endpoints
│   ├── schemas/                      # Pydantic data models
│   │   ├── qr_code.py
│   │   └── rooms.py
│   ├── utils/                        # Utility functions
│   │   ├── create_qr.py              # QR code generation
│   │   ├── enums.py                  # Enumeration types
│   │   ├── json_helpers.py           # JSON utilities
│   │   ├── mobile_pairing.py         # Mobile device pairing
│   │   ├── qr_code.py                # QR code utilities
│   │   ├── qr_redis.py               # QR code Redis operations
│   │   ├── queue.py                  # Queue management
│   │   ├── settings.py               # Configuration settings
│   │   ├── storage.py                # File storage utilities
│   │   ├── token.py                  # Token management
│   │   ├── tv_pairing.py             # TV device pairing
│   │   └── websocket_manager.py      # WebSocket connection manager
│   ├── views/                        # View templates (if any)
│   ├── Dockerfile                    # API container configuration
│   ├── entryPoint.sh                 # API startup script
│   ├── main.py                       # FastAPI application entry point
│   ├── Readme.md                     # API documentation
│   └── requirements.txt              # API Python dependencies
│
├── common/                           # Django REST Framework Main Application
│   ├── apps/                         # Django applications
│   │   ├── ai_integration/           # AI model integration
│   │   │   ├── admin.py
│   │   │   ├── middleware.py         # AI operation middleware
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── ai_montage/               # AI-generated montages
│   │   ├── analytics/                # Usage analytics & tracking
│   │   ├── authentication/           # User authentication & authorization
│   │   │   ├── models.py             # User, DeviceLink, tokens
│   │   │   ├── serializers.py        # API serializers
│   │   │   ├── views.py              # Auth endpoints
│   │   │   └── urls.py
│   │   ├── before_after/             # Before/after image comparisons
│   │   ├── blogs/                    # Blog/content management
│   │   ├── carts/                    # Shopping cart functionality
│   │   ├── chats/                    # Chat/messaging system
│   │   ├── collection_with_narration/ # Narrated art collections
│   │   ├── credits/                  # Credit/payment system
│   │   ├── curations/                # Content curation engine
│   │   ├── dashboard/                # Admin dashboard
│   │   ├── event_scheduler/          # Event scheduling system
│   │   ├── gallery/                  # Image gallery management
│   │   ├── iterative_artwork/        # Iterative art generation
│   │   ├── marketplace/              # Marketplace functionality
│   │   ├── market_material/          # Marketing materials
│   │   ├── metaaudios/               # Audio metadata management
│   │   ├── metacollections/          # Collection metadata
│   │   ├── metaimages/               # Image metadata management
│   │   ├── modes/                    # Display modes
│   │   ├── music_generator/          # AI music generation
│   │   ├── notifications/            # Push notifications
│   │   ├── orders/                   # Order management
│   │   ├── payments/                 # Payment processing (Stripe)
│   │   ├── quote_poster/             # Quote poster generation
│   │   ├── reviews/                  # Review system
│   │   ├── sculpture/                # 3D sculpture generation
│   │   ├── sequential_artwork/       # Sequential art generation
│   │   ├── social/                   # Social features
│   │   ├── utils/                    # Shared utilities
│   │   │   ├── exceptions.py         # Custom exception handlers
│   │   │   ├── google_sheet.py       # Google Sheets integration
│   │   │   └── middleware.py         # Request logging middleware
│   │   ├── visual_audiobook/         # Visual audiobook creation
│   │   └── visual_chat/              # Visual chat interface
│   │
│   ├── deckoviz/                     # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py                   # ASGI configuration
│   │   ├── celery.py                 # Celery task queue config
│   │   ├── settings.py               # Main Django settings
│   │   ├── urls.py                   # URL routing
│   │   └── wsgi.py                   # WSGI configuration
│   │
│   ├── staticfiles/                  # Static files (CSS, JS, images)
│   │   ├── admin/
│   │   ├── ckeditor/
│   │   └── rest_framework/
│   │
│   ├── Dockerfile                    # Common service container config
│   ├── entryPoint.sh                 # Startup script
│   ├── manage.py                     # Django management script
│   ├── Readme.md                     # Common service documentation
│   ├── requirements.txt              # Django Python dependencies
│   ├── scripts.sh                    # Deployment scripts
│   └── supervisord.conf              # Supervisor configuration for workers
│
├── logs/                             # Application logs
│   ├── celery/                       # Celery worker logs
│   ├── django_app.log                # Django application logs
│   └── django_requests.log           # HTTP request logs
│
├── .env                              # Environment variables (not in repo)
├── .gitignore                        # Git ignore rules
├── .python-version                   # Python version specification
├── docker-compose.yml                # Docker orchestration
├── entryPoint.sh                     # Root startup script
├── monitor_logs.sh                   # Log monitoring script
│
├── API_DOCUMENTATION.md              # API endpoint documentation
├── LOGGING_ENHANCEMENT.md            # Logging system documentation
├── METADATA_FIXES_SUMMARY.md         # Metadata improvements
├── PRODUCTION_READINESS_PLAN.md      # Production deployment plan
├── README.md                         # Main project documentation
├── SECURITY.md                       # Security policy
├── STORAGE_README.md                 # Storage configuration guide
├── TEST_SETUP.md                     # Testing setup guide
├── TODO                              # Development roadmap
├── USAGE_TRACKING_ENHANCEMENT.md     # Analytics tracking docs
├── USER_FILTERING_API_DOCUMENTATION.md # API filtering documentation
│
├── DeckViz_Sharing_APIs_with_Filtering.postman_collection.json  # Postman tests
└── LICENSE                           # Project license
```

---

## 🏗️ Architecture

### Multi-Service Architecture

The Deckoviz backend uses a **microservices architecture** with the following services:

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer / nginx                    │
└────────────┬──────────────────────────────────┬─────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────┐           ┌───────────────────────┐
│   FastAPI (api/)       │           │  Django REST (common/) │
│   - WebSocket Server   │           │  - REST API           │
│   - Real-time Comms    │◄─────────►│  - Business Logic     │
│   - Device Pairing     │           │  - User Management    │
│   - QR Code System     │           │  - Content Management │
└──────────┬─────────────┘           └───────────┬───────────┘
           │                                      │
           │                                      │
           └──────────────┬───────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐   ┌────────────┐
    │  Redis  │    │PostgreSQL│   │  AWS S3    │
    │  Cache  │    │ Database │   │  Storage   │
    │  Queue  │    │          │   │            │
    └────┬────┘    └──────────┘   └────────────┘
         │
         ▼
    ┌─────────┐
    │ Celery  │
    │ Workers │
    └─────────┘
```

### Communication Flow

1. **Client → Django REST API**: Authentication, user management, content CRUD
2. **Client → FastAPI**: WebSocket connections, real-time updates, device pairing
3. **Django ↔ FastAPI**: Internal service communication via HTTP
4. **Services → Redis**: Caching, session management, QR code storage
5. **Services → PostgreSQL**: Persistent data storage
6. **Celery Workers**: Async task processing (emails, AI generation, analytics)

---

## 🔑 Key Components

### 1. Authentication System (`common/apps/authentication/`)

**Features:**
- JWT-based authentication with access/refresh tokens
- Email verification with token-based system
- Password reset flow
- OAuth2 integration (Google)
- Device pairing for TV/mobile apps
- Multi-device support with bcrypt token hashing

**Critical Models:**
- `User`: Custom user model with email verification
- `DeviceLink`: Device pairing with refresh token management
- `PasswordResetToken`: Time-limited password reset tokens
- `EmailVerificationToken`: Email verification tokens
- `Address`: User address management
- `UserProfile`: Extended user profile information

**⚠️ Known Issues:**
- RefreshTokenView has O(n) performance issue (see PRODUCTION_READINESS_PLAN.md)
- JWT tokens have 365-day lifetime (security risk)
- No token blacklist/revocation system

### 2. WebSocket System (`api/routers/`)

**Features:**
- Real-time bidirectional communication
- Room-based message broadcasting
- Device connection management
- QR code-based device pairing
- Session management via Redis

**Key Endpoints:**
- `/ws/{room_id}`: WebSocket connection for rooms
- `/ws/device/{device_id}`: Device-specific WebSocket
- `/rooms/`: Room management
- `/qr/`: QR code generation and validation

### 3. Content Management

**Gallery System** (`common/apps/gallery/`):
- Image upload and storage
- Collection management
- Metadata tracking

**Curations** (`common/apps/curations/`):
- AI-powered content curation
- Personalized recommendations
- Collection organization

**Metacollections** (`common/apps/metacollections/`):
- Collection metadata management
- Tags and categorization

### 4. AI Integration (`common/apps/ai_integration/`)

**Features:**
- AI model integration middleware
- Credit-based usage tracking
- Multiple AI services:
  - Image generation (Stable Diffusion)
  - Style transfer
  - Montage creation
  - Music generation
  - Visual audiobooks
  - Quote posters

**AI Services:**
- `ai_montage/`: AI-generated photo montages
- `music_generator/`: AI music composition
- `iterative_artwork/`: Iterative art generation
- `sequential_artwork/`: Sequential art creation
- `sculpture/`: 3D sculpture generation
- `before_after/`: Before/after image processing
- `quote_poster/`: AI-powered quote posters
- `visual_audiobook/`: Visual audiobook generation
- `visual_chat/`: Visual chat interface

### 5. E-commerce System

**Components:**
- `marketplace/`: Product listings
- `carts/`: Shopping cart management
- `orders/`: Order processing
- `payments/`: Stripe payment integration
- `credits/`: Credit system for AI operations
- `reviews/`: Product/content reviews

### 6. Analytics & Monitoring

**Analytics** (`common/apps/analytics/`):
- User behavior tracking
- Usage statistics
- Content performance metrics

**Logging**:
- Structured logging with rotation
- Request/response logging
- Separate log files for different services
- Log files: `/app/logs/django_app.log`, `/app/logs/django_requests.log`

### 7. Social Features (`common/apps/social/`)

**Features:**
- User interactions
- Content sharing
- Social feed
- Follow/follower system

### 8. Background Tasks (Celery)

**Celery Configuration:**
- Worker: Processes async tasks
- Flower: Web-based task monitoring (port 5555)
- Redis: Message broker and result backend

**Common Tasks:**
- Email sending (verification, password reset)
- AI model processing
- Image processing
- Analytics aggregation
- Report generation

---

## 🛠️ Technology Stack

### Backend Frameworks
- **Django 5.1.7**: Main web framework
- **Django REST Framework**: RESTful API
- **FastAPI**: WebSocket and real-time services
- **Celery**: Distributed task queue
- **Flower**: Celery monitoring

### Databases & Caching
- **PostgreSQL**: Primary database
- **Redis**: Caching, sessions, Celery broker

### Storage
- **AWS S3**: File and media storage
- **WhiteNoise**: Static file serving

### Authentication & Security
- **Simple JWT**: JWT token authentication
- **bcrypt**: Password hashing
- **django-cors-headers**: CORS handling
- **social-auth-app-django**: OAuth2 (Google)

### API Documentation
- **drf-spectacular**: OpenAPI/Swagger documentation
- **Postman**: API testing collection included

### DevOps & Monitoring
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Supervisor**: Process management
- **Sentry** (planned): Error tracking

### Python Libraries
- **Pillow**: Image processing
- **boto3**: AWS SDK
- **django-storages**: Cloud storage backends
- **django-ckeditor**: Rich text editor
- **decouple**: Configuration management

---

## 🔌 API Services

### Django REST API (`common:8000`)

**Authentication Endpoints:**
- `POST /auth/register/`: User registration
- `POST /auth/login/`: JWT login (custom token obtain pair)
- `POST /auth/token/refresh/`: Refresh access token
- `POST /auth/verify-email/`: Verify email with token
- `POST /auth/resend-verification/`: Resend verification email
- `POST /auth/forgot-password/`: Request password reset
- `POST /auth/reset-password/`: Reset password with token
- `GET /auth/login/google/`: Initiate Google OAuth
- `GET /auth/login/google/callback/`: Google OAuth callback

**Device Management:**
- `POST /auth/device-link/`: Create device link
- `POST /auth/refresh-token/`: Validate refresh token
- `POST /auth/logout-device/`: Remove device link

**User Management:**
- `GET /users/`: List users (current user only)
- `GET /users/{id}/`: Get user details
- `PATCH /users/{id}/`: Update user
- `GET /users/profile/`: Get user profile
- `PATCH /users/profile/`: Update user profile

**Address Management:**
- `GET /addresses/`: List user addresses
- `POST /addresses/`: Create address
- `GET /addresses/{id}/`: Get address
- `PATCH /addresses/{id}/`: Update address
- `DELETE /addresses/{id}/`: Delete address

**Newsletter:**
- `POST /newsletter/subscribe/`: Subscribe to newsletter

**Content Endpoints:**
- `/gallery/`: Image and gallery management
- `/curations/`: Content curation
- `/metacollections/`: Collection metadata
- `/metaimages/`: Image metadata
- `/metaaudios/`: Audio metadata

**Marketplace Endpoints:**
- `/marketplace/`: Product listings
- `/carts/`: Shopping cart
- `/orders/`: Order management
- `/payments/`: Payment processing
- `/reviews/`: Product reviews

**AI Endpoints:**
- `/ai/`: AI integration
- `/ai-montage/`: Montage generation
- `/music-generator/`: Music generation
- `/visual-chat/`: Visual chat
- `/visual-audiobook/`: Audiobook creation
- `/sculpture/`: 3D sculpture
- `/quote-poster/`: Quote posters

**Analytics:**
- `/analytics/`: Usage analytics

**Social:**
- `/social/`: Social features

### FastAPI WebSocket Service (Port varies)

**WebSocket Endpoints:**
- `WS /ws/{room_id}`: Join room for real-time updates
- `WS /ws/device/{device_id}`: Device-specific WebSocket

**QR Code & Pairing:**
- `POST /qr/generate/`: Generate QR code for pairing
- `GET /qr/{qr_id}/`: Get QR code status
- `POST /pairing/mobile/`: Pair mobile device
- `POST /pairing/tv/`: Pair TV device

**Room Management:**
- `POST /rooms/`: Create room
- `GET /rooms/{room_id}/`: Get room details
- `DELETE /rooms/{room_id}/`: Delete room

**Curations:**
- `GET /curations/`: List curations
- `POST /curations/`: Create curation

### API Documentation

**Swagger UI:**
- URL: `http://localhost:8000/api/schema/swagger-ui/`
- Interactive API documentation with authentication

**ReDoc:**
- URL: `http://localhost:8000/api/schema/redoc/`
- Alternative API documentation view

**OpenAPI Schema:**
- URL: `http://localhost:8000/api/schema/`
- Raw OpenAPI JSON schema

---

## 🗄️ Database Schema

### Core Tables

**authentication_user:**
- `id`: UUID (primary key)
- `email`: Unique email address
- `password`: Hashed password
- `first_name`, `last_name`: User name
- `is_active`: Account status
- `email_verified`: Email verification status
- `date_joined`, `last_login`: Timestamps

**authentication_devicelink:**
- `id`: UUID (primary key)
- `user_id`: Foreign key to User
- `device_type`: 'tv' | 'mobile' | 'tablet'
- `refresh_token_hash`: bcrypt hash of refresh token
- `expires_at`: Token expiration
- `created_at`: Timestamp

**authentication_passwordresettoken:**
- `id`: Auto-increment
- `user_id`: Foreign key to User
- `token`: Hashed reset token
- `created_at`: Timestamp
- `is_used`: Boolean flag
- `expires_at`: Token expiration

**authentication_emailverificationtoken:**
- Similar structure to PasswordResetToken
- Used for email verification

**authentication_address:**
- `id`: UUID (primary key)
- `user_id`: Foreign key to User
- Address fields (street, city, state, zip, country)
- `is_default`: Boolean flag

**authentication_userprofile:**
- `id`: Auto-increment
- `user_id`: OneToOne with User
- Extended profile fields

### Content Tables

**gallery_image:**
- Image metadata and storage paths

**metacollections_collection:**
- Collection metadata
- Tags and categorization

**curations_curation:**
- AI-curated content sets

### E-commerce Tables

**marketplace_product:**
- Product listings

**carts_cart, carts_cartitem:**
- Shopping cart management

**orders_order, orders_orderitem:**
- Order processing

**payments_payment:**
- Payment transactions

**credits_credit:**
- AI credit system

### Analytics Tables

**analytics_event:**
- User event tracking

**analytics_usage:**
- Usage statistics

---

## 🔐 Authentication & Security

### Authentication Flow

**User Registration:**
1. User submits email/password
2. System creates user account (inactive)
3. System sends verification email with 6-digit code
4. User verifies email
5. Account becomes active

**Login Flow:**
1. User submits credentials
2. System validates and returns JWT tokens
3. Access token (15 minutes recommended, currently 365 days)
4. Refresh token (7 days recommended, currently 365 days)

**Device Pairing:**
1. Mobile app requests device pairing
2. System generates QR code with pairing data
3. TV scans QR code
4. System creates DeviceLink with bcrypt-hashed refresh token
5. TV stores refresh token locally
6. TV uses refresh token for authentication

### Security Features

**Implemented:**
- JWT authentication
- bcrypt password hashing
- Email verification
- CSRF protection
- CORS configuration
- HTTPS redirect (production)
- Secure cookies
- Rate limiting on auth endpoints

**⚠️ Security Issues (See PRODUCTION_READINESS_PLAN.md):**
- JWT tokens have 365-day lifetime (should be 15 minutes)
- No token blacklist/revocation
- RefreshTokenView has O(n) performance vulnerability
- Missing comprehensive rate limiting
- No token rotation strategy

### Environment Variables

Required in `.env` file:
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=api.deckoviz.com,localhost
DATABASE_URL=postgresql://user:pass@host/db

# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=deckoviz-media
AWS_REGION=us-east-1

# Stripe
STRIPE_SECRET_KEY=sk_test_...

# Email (SendGrid)
EMAIL_HOST_PASSWORD=sendgrid-api-key
DEFAULT_FROM_EMAIL=no-reply@deckoviz.com

# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn

# Celery Flower
FLOWER_USERNAME=admin
FLOWER_PASSWORD=secure-password
```

---

## 🚀 Deployment

### Docker Compose Services

```yaml
services:
  common:           # Django REST API
    - Port 8000
    - Runs Gunicorn/Uvicorn
    - Depends on: postgres, redis
  
  celery_worker:    # Background task processor
    - Runs Celery worker
    - Uses Supervisor for process management
  
  flower:           # Celery monitoring
    - Port 5555
    - Web UI for task monitoring
  
  postgres:         # PostgreSQL database
    - Port 5432
  
  redis:            # Redis cache/broker
    - Port 6379
  
  api:              # FastAPI WebSocket service
    - Port configured separately
```

### Deployment Commands

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run migrations
docker-compose exec common python manage.py migrate

# Create superuser
docker-compose exec common python manage.py createsuperuser

# Collect static files
docker-compose exec common python manage.py collectstatic --noinput
```

### Production Deployment Checklist

See [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) for complete checklist.

**Critical Items:**
- [ ] Fix RefreshTokenView O(n) performance issue
- [ ] Implement Redis caching layer
- [ ] Add PgBouncer connection pooling
- [ ] Add database indexes
- [ ] Fix JWT token strategy (reduce lifetime)
- [ ] Implement rate limiting on all endpoints
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure load balancer
- [ ] Set up horizontal scaling
- [ ] Implement health check endpoints
- [ ] Configure automated backups
- [ ] Security hardening (see SECURITY.md)

---

## 💻 Development Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+
- AWS Account (for S3)
- SendGrid Account (for emails)

### Local Setup

```bash
# Clone repository
git clone <repo-url>
cd python_deckoviz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd common
pip install -r requirements.txt

cd ../api
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
cd ../common
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server (Django)
python manage.py runserver

# In another terminal, run FastAPI
cd ../api
uvicorn main:app --reload --port 8001
```

### Docker Development

```bash
# Build and start all services
docker-compose up --build

# Access Django admin
# http://localhost:8000/admin/

# Access API docs
# http://localhost:8000/api/schema/swagger-ui/

# Access Flower (Celery monitor)
# http://localhost:5555/
```

### Running Tests

```bash
# Django tests
cd common
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Management

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create database backup
docker-compose exec postgres pg_dump -U postgres deckoviz > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres deckoviz < backup.sql
```

---

## 📊 Monitoring & Logging

### Log Files

- **Django Application**: `/app/logs/django_app.log`
- **Django Requests**: `/app/logs/django_requests.log`
- **Celery Workers**: `/app/logs/celery/`

### Log Rotation

- Max file size: 10MB
- Backup count: 5 files
- Format: Timestamp, Level, Logger Name, Message

### Monitoring Tools

**Flower (Celery Monitoring):**
- URL: `http://localhost:5555`
- Username/Password: Set in .env

**Django Admin:**
- URL: `http://localhost:8000/admin/`

**API Metrics** (Planned):
- Prometheus metrics: `/metrics/`
- Grafana dashboards

---

## 🔄 API Rate Limiting

### Current Throttle Rates

| Endpoint                | Rate Limit        |
|-------------------------|-------------------|
| Login                   | 5/minute          |
| Register                | 20/hour           |
| Password Reset Request  | 5/hour            |
| Password Reset Confirm  | 5/hour            |
| Email Verification      | 10/hour           |
| Resend Verification     | 3/hour            |

### Planned Improvements

- Global rate limiting for all endpoints
- Per-user rate limiting
- Anonymous user restrictions
- DDoS protection via nginx

---

## 📚 Additional Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md): Detailed API endpoint documentation
- [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md): Production deployment plan
- [SECURITY.md](SECURITY.md): Security policy and vulnerability reporting
- [STORAGE_README.md](STORAGE_README.md): Storage configuration guide
- [LOGGING_ENHANCEMENT.md](LOGGING_ENHANCEMENT.md): Logging system documentation
- [USAGE_TRACKING_ENHANCEMENT.md](USAGE_TRACKING_ENHANCEMENT.md): Analytics tracking
- [USER_FILTERING_API_DOCUMENTATION.md](USER_FILTERING_API_DOCUMENTATION.md): API filtering
- [TEST_SETUP.md](TEST_SETUP.md): Testing setup guide
- [TODO](TODO): Development roadmap

---

## 🐛 Known Issues

### Critical

1. **RefreshTokenView O(n) Performance**
   - Iterates through all devices on every request
   - Causes timeouts with 1000+ devices
   - Solution: Add indexed prefix field

2. **JWT Token Security**
   - 365-day token lifetime is a security risk
   - No token revocation mechanism
   - Solution: Reduce to 15 minutes, add blacklist

3. **No Caching Layer**
   - Every request hits database
   - Performance degrades with load
   - Solution: Implement Redis caching

### High Priority

4. Missing database connection pooling
5. Missing database indexes on foreign keys
6. N+1 query issues in multiple views
7. No comprehensive rate limiting
8. No monitoring/alerting system

See [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) for complete list and solutions.

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch from `main`
2. Make changes with descriptive commits
3. Write/update tests
4. Update documentation
5. Submit pull request

### Code Style

- Python: PEP 8
- Django: Django best practices
- FastAPI: FastAPI conventions
- Use type hints where applicable
- Write docstrings for public functions

### Commit Message Format

```
type(scope): subject

body

footer
```

Types: feat, fix, docs, style, refactor, test, chore

---

## 📞 Support & Contact

- **Security Issues**: security@forofuselabs.com
- **Bug Reports**: GitHub Issues
- **Feature Requests**: GitHub Issues
- **General Questions**: Documentation first, then GitHub Discussions

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🎯 Roadmap (from TODO)

### V1 Features
- [ ] Transform images to GIF/video
- [ ] Style transfer to any art style
- [ ] Basic recommendation engine
- [ ] Queue mechanism for TV app updates
- [ ] Voice journal transcription and AI insights

### Future Features
- [ ] Creator marketplace
- [ ] Advanced AI personalization
- [ ] Multi-room synchronization
- [ ] Smart home integrations
- [ ] Mobile AR preview mode

---

**Last Updated**: January 22, 2026  
**Version**: 1.0.0  
**Status**: Development / NOT Production-Ready
