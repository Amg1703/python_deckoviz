# Production Readiness Plan - Deckoviz Backend

## Executive Summary
**Current Status:** ❌ NOT production-ready for 100+ concurrent users  
**Estimated Time to Production:** 2-3 weeks  
**Priority:** HIGH - Critical performance and security issues identified

---

## Critical Issues (Must Fix Before Launch)

### 1. ❌ RefreshTokenView Performance Disaster

**Current Code Problem:**
```python
# Line 105-122 in views.py - O(n) complexity!
for device in DeviceLink.objects.all():  # Loads ALL records!
    if bcrypt.checkpw(refresh_token_trunc.encode(), device.refresh_token_hash.encode()):
        # Each bcrypt check: ~100-300ms
```

**Impact:** 
- With 100 devices: 10-30 seconds per request
- With 1000 devices: 100-300 seconds (TIMEOUT!)
- Database memory overload

**Solution:** Add hash-indexed lookup
```python
# Add to DeviceLink model:
refresh_token_prefix = models.CharField(max_length=32, db_index=True)

# Update RefreshTokenView to:
1. Extract first 32 chars as prefix
2. Query only devices with matching prefix
3. Then bcrypt check on small subset (1-5 records typically)
```

**Performance Gain:** 10-30s → 100-200ms (99% faster)

---

### 2. ❌ No Caching Layer

**Problem:** Every request hits PostgreSQL
- User profile lookups: 50-100ms per request
- Metadata queries: 100-200ms per request
- 100 concurrent users = database overload

**Solution:** Implement Redis caching

**Configuration Needed:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'deckoviz',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Enable cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Add first
    # ... existing middleware ...
    'django.middleware.cache.FetchFromCacheMiddleware',  # Add last
]

CACHE_MIDDLEWARE_SECONDS = 60
```

**Cache Strategy:**
- User profiles: 5 minutes
- Public content: 15 minutes
- Authentication tokens: Until expiry
- API responses: 1-5 minutes

---

### 3. ❌ Database Connection Pooling Missing

**Problem:** Django creates new DB connection per request
- Connection overhead: 50-100ms
- Max connections limit reached quickly
- Connection leaks under load

**Solution:** Implement PgBouncer + Django persistent connections

**docker-compose.yml addition:**
```yaml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  container_name: pgbouncer
  environment:
    - DATABASES_HOST=postgres
    - DATABASES_PORT=5432
    - DATABASES_USER=postgres
    - DATABASES_PASSWORD=${DB_PASSWORD}
    - DATABASES_DBNAME=${DB_NAME}
    - PGBOUNCER_POOL_MODE=transaction
    - PGBOUNCER_MAX_CLIENT_CONN=1000
    - PGBOUNCER_DEFAULT_POOL_SIZE=25
  ports:
    - "6432:6432"
  networks:
    - decoviz_common_default
```

**settings.py update:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'pgbouncer',  # Changed from 'postgres'
        'PORT': '6432',  # Changed from '5432'
        'CONN_MAX_AGE': 600,  # Keep connections alive 10 min
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}
```

---

### 4. ❌ Missing Database Indexes

**Problem:** Slow queries on foreign keys and lookups

**Required Migrations:**
```python
# Create migration file
class Migration(migrations.Migration):
    operations = [
        # DeviceLink indexes
        migrations.AddIndex(
            model_name='devicelink',
            index=models.Index(fields=['user', 'device_type'], name='device_user_type_idx'),
        ),
        migrations.AddIndex(
            model_name='devicelink',
            index=models.Index(fields=['expires_at'], name='device_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='devicelink',
            index=models.Index(fields=['refresh_token_hash'], name='device_token_hash_idx'),
        ),
        
        # User indexes (if not exists)
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='user_email_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_active', 'email_verified'], name='user_active_verified_idx'),
        ),
    ]
```

---

### 5. ❌ No Query Optimization

**Problem:** N+1 queries everywhere

**Examples Found:**
```python
# BAD - N+1 query
users = User.objects.all()
for user in users:
    print(user.profile.age)  # Separate query per user!
    print(user.addresses.count())  # Another query!

# GOOD - Use select_related & prefetch_related
users = User.objects.select_related('profile').prefetch_related('addresses').all()
```

**Fix Required in Views:**
- UserView: Add `select_related('profile')`
- AddressView: Add `select_related('user')`
- All relationship queries: Use prefetch_related

---

### 6. ❌ JWT Token Strategy (Security Risk)

**Problem:**
- 365-day token lifetime (HUGE security risk!)
- No token refresh strategy
- No token revocation

**Solution:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Changed from 365 days!
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,  # Generate new refresh token
    'BLACKLIST_AFTER_ROTATION': True,  # Invalidate old tokens
    'UPDATE_LAST_LOGIN': True,
}

# Add to INSTALLED_APPS
INSTALLED_APPS += ['rest_framework_simplejwt.token_blacklist']
```

**Migration Required:**
```bash
python manage.py migrate token_blacklist
```

---

## High Priority Improvements

### 7. Rate Limiting (DDoS Protection)

**Current:** Only 5 endpoints have throttling  
**Required:** All endpoints need protection

**Implementation:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users
        'user': '1000/hour',  # Authenticated users
        'login': '5/minute',
        'register': '3/hour',
        'password-reset-request': '3/hour',
        'password-reset-confirm': '5/hour',
        'verify-email': '10/hour',
        'resend-verification': '3/hour',
    },
}
```

---

### 8. Application Monitoring (Observability)

**Add Sentry for Error Tracking:**
```python
# requirements.txt
sentry-sdk[django]==1.40.0

# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
    environment=config('ENVIRONMENT', 'production'),
    send_default_pii=False,
)
```

**Add Prometheus Metrics:**
```python
# requirements.txt
django-prometheus==2.3.1

# settings.py
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... existing middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
urlpatterns += [path('metrics/', include('django_prometheus.urls'))]
```

---

### 9. Health Check Endpoints

**Implementation:**
```python
# common/apps/utils/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import redis

class HealthCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        health = {
            'status': 'healthy',
            'database': self._check_database(),
            'cache': self._check_cache(),
            'celery': self._check_celery(),
        }
        
        if not all(health.values()):
            health['status'] = 'unhealthy'
            return Response(health, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(health, status=status.HTTP_200_OK)
    
    def _check_database(self):
        try:
            connection.ensure_connection()
            return True
        except Exception:
            return False
    
    def _check_cache(self):
        try:
            cache.set('health_check', 'ok', 10)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False
    
    def _check_celery(self):
        try:
            from deckoviz.celery import app
            stats = app.control.inspect().stats()
            return stats is not None
        except Exception:
            return False

# urls.py
urlpatterns += [
    path('health/', HealthCheckView.as_view()),
    path('health/ready/', HealthCheckView.as_view()),
]
```

---

### 10. Load Balancing & Horizontal Scaling

**nginx Load Balancer:**
```nginx
# nginx.conf
upstream deckoviz_backend {
    least_conn;  # Load balancing algorithm
    server common:8000 max_fails=3 fail_timeout=30s;
    server common_2:8000 max_fails=3 fail_timeout=30s;
    server common_3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.deckoviz.com;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://deckoviz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**docker-compose.yml scaling:**
```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx_lb
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./staticfiles:/app/staticfiles:ro
    depends_on:
      - common
    networks:
      - decoviz_common_default

  common:
    # ... existing config ...
    deploy:
      replicas: 3  # Run 3 instances
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

### 11. Database Read Replicas

**For Read-Heavy Operations:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_REPLICA_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Database router
class ReplicaRouter:
    def db_for_read(self, model, **hints):
        return 'replica'
    
    def db_for_write(self, model, **hints):
        return 'default'

DATABASE_ROUTERS = ['path.to.ReplicaRouter']
```

---

### 12. Async Task Processing

**Optimize Celery Configuration:**
```python
# settings.py
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_EXPIRES = 3600
```

**Move heavy operations to background:**
- Email sending
- Image processing
- Report generation
- Analytics calculations

---

### 13. Response Compression

**Enable gzip compression:**
```python
# settings.py
MIDDLEWARE.insert(0, 'django.middleware.gzip.GZipMiddleware')

# Compress responses > 1KB
GZIP_MIN_LENGTH = 1024
```

---

### 14. API Response Optimization

**Implement Pagination Everywhere:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
}
```

**Add API Response Caching:**
```python
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class MyViewSet(viewsets.ModelViewSet):
    @method_decorator(cache_page(60 * 5))  # Cache 5 minutes
    def list(self, request):
        return super().list(request)
```

---

### 15. Security Headers

**Add security middleware:**
```python
# settings.py
MIDDLEWARE += ['django.middleware.security.SecurityMiddleware']

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
```

---

## Medium Priority Improvements

### 16. CDN Integration
- CloudFront/CloudFlare for static assets
- Media file delivery optimization
- Global edge caching

### 17. Database Backup Strategy
- Automated daily backups
- Point-in-time recovery
- Backup testing procedure

### 18. Logging Enhancement
```python
# Structured logging with JSON
LOGGING['formatters']['json'] = {
    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
    'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
}
```

### 19. Automated Testing
- Load testing (Locust/k6)
- Integration tests
- CI/CD pipeline

### 20. Documentation
- API documentation (OpenAPI/Swagger)
- Runbooks for common issues
- Deployment procedures

---

## Infrastructure Checklist

- [ ] Add PgBouncer for connection pooling
- [ ] Configure Redis caching layer
- [ ] Set up nginx load balancer
- [ ] Implement horizontal scaling (3+ app instances)
- [ ] Add Sentry error tracking
- [ ] Add Prometheus metrics
- [ ] Configure health check endpoints
- [ ] Set up database read replicas
- [ ] Implement CDN (CloudFront/CloudFlare)
- [ ] Configure automated backups
- [ ] Set up monitoring dashboard (Grafana)
- [ ] Configure alerting (PagerDuty/OpsGenie)
- [ ] Implement log aggregation (ELK/Loki)
- [ ] Set up CI/CD pipeline
- [ ] Configure autoscaling policies
- [ ] Implement disaster recovery plan

---

## Performance Testing Requirements

### Load Testing Targets:
- 100 concurrent users
- 1000 requests/second
- 95th percentile response time < 500ms
- 99th percentile response time < 1000ms
- 0% error rate under normal load

### Tools:
- Locust for load testing
- Apache Bench for quick tests
- k6 for advanced scenarios

### Test Scenarios:
1. User authentication flow
2. Content browsing (read-heavy)
3. Content creation (write-heavy)
4. Mixed workload simulation

---

## Estimated Costs (Monthly)

### Minimal Production Setup:
- **Application Servers**: 3x t3.medium ($100)
- **PostgreSQL RDS**: db.t3.large ($150)
- **Redis ElastiCache**: cache.t3.medium ($50)
- **Load Balancer**: ALB ($25)
- **CDN**: CloudFront ($30)
- **Monitoring**: Sentry + DataDog ($100)
- **Backups & Storage**: ($50)
- **Total**: ~$505/month

### Recommended Production Setup:
- **Application Servers**: 3x t3.large ($200)
- **PostgreSQL RDS**: db.r5.large + read replica ($400)
- **Redis ElastiCache**: cache.r5.large ($150)
- **Load Balancer**: ALB ($25)
- **CDN**: CloudFront + WAF ($100)
- **Monitoring**: Sentry + DataDog + New Relic ($200)
- **Backups & Storage**: ($100)
- **Total**: ~$1,175/month

---

## Implementation Timeline

### Week 1 (Critical Fixes):
- Day 1-2: Fix RefreshTokenView O(n) issue
- Day 3-4: Implement Redis caching
- Day 5: Add database connection pooling

### Week 2 (Performance & Security):
- Day 1-2: Add database indexes
- Day 3: Optimize queries (select_related/prefetch_related)
- Day 4: Fix JWT token strategy
- Day 5: Implement rate limiting

### Week 3 (Infrastructure):
- Day 1-2: Set up load balancer + horizontal scaling
- Day 3: Add monitoring (Sentry + Prometheus)
- Day 4: Implement health checks
- Day 5: Load testing and optimization

### Week 4 (Polish):
- Day 1: CDN setup
- Day 2: Database backups
- Day 3: Security hardening
- Day 4-5: Documentation and runbooks

---

## Success Metrics

- ✅ 100+ concurrent users without degradation
- ✅ Average response time < 200ms
- ✅ 99.9% uptime SLA
- ✅ Zero critical security vulnerabilities
- ✅ Auto-recovery from failures
- ✅ < 5 minute deployment time
- ✅ < 1 hour MTTR (Mean Time To Recovery)

---

## Final Recommendation

**DO NOT LAUNCH** with current codebase. The RefreshTokenView alone will cause immediate outages under load.

**Minimum viable fixes** (1 week):
1. Fix RefreshTokenView performance
2. Add Redis caching
3. Implement connection pooling
4. Add rate limiting
5. Set up basic monitoring

**After these fixes**, you can handle 100 users with acceptable performance. Full production readiness requires 3-4 weeks of work.
