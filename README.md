# 🚀 Leadex - Enterprise Lead Distribution System

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/hamedniavand/Leadex)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive, enterprise-grade lead distribution platform built with FastAPI, PostgreSQL, and Redis. Leadex automates lead capture, intelligent distribution, and multi-channel delivery with advanced reporting and real-time analytics.

**Production-Ready** | Complete Feature Set | 30+ Database Tables | 100+ API Endpoints

> **Latest Update (December 2025)**: All critical systems operational. Reports, client management, lead tracking, and multi-channel delivery fully functional and tested.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Leadex** is an enterprise-grade lead distribution platform designed to:

- **Capture leads** from landing pages with duplicate detection
- **Distribute leads** intelligently based on rules and availability
- **Deliver leads** via multiple channels (Webhook, Email, WhatsApp, Google Sheets)
- **Manage credits** with automatic deduction and tracking
- **Track performance** with real-time analytics and comprehensive reporting
- **Automate workflows** with background processing and notifications

### Use Cases

- **Marketing Agencies**: Distribute leads to multiple clients automatically
- **Real Estate**: Route property inquiries to agents based on availability
- **E-commerce**: Distribute customer inquiries to sales teams
- **Lead Generation**: Monetize leads by selling to multiple buyers
- **SaaS Platforms**: Power lead distribution features in your product

---

## ✨ Key Features

### 🎯 Core Functionality

- **Lead Capture**: Landing page forms with mobile validation and duplicate detection
- **Smart Distribution**: Rule-based allocation with credit checking
- **Batch Processing**: Automated lead distribution in configurable batches
- **Multi-Channel Delivery**: Webhook, Email, WhatsApp, Google Sheets
- **Credit System**: Automatic credit deduction and management
- **Queue Management**: Intelligent lead queue when clients unavailable

### 📊 Advanced Features

- **Comprehensive Reporting**: 6 report types with one-click generation
  - Lead Summary Report
  - Performance & Success Rate Analysis
  - Revenue & Credits Report
  - Client Detailed Report
  - Webhook Activity Report
  - Complete CSV Export

- **Analytics Dashboard**: Real-time metrics and performance tracking
- **Lead Management**: Notes, tags, custom fields, scoring
- **Bulk Operations**: Import, export, delete, resend
- **Client Portal**: Self-service dashboard for clients
- **Email Notifications**: Automated notifications for key events

### ⚡ Performance & Optimization

- **Redis Caching**: Smart caching for frequently accessed data
- **Rate Limiting**: Protect APIs with configurable rate limits
- **Background Jobs**: Async processing for heavy operations
- **Connection Pooling**: Optimized database performance
- **Performance Monitoring**: Real-time endpoint statistics

### 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin and Client role separation
- **Password Hashing**: Industry-standard bcrypt hashing
- **API Security**: Rate limiting and input validation
- **Audit Logging**: Track all critical operations

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  Landing Pages  │ → Lead Capture
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI App   │ → Business Logic
│   (Python 3.12) │
└────────┬────────┘
         │
         ├─────→ PostgreSQL (Lead Storage)
         ├─────→ Redis (Cache & Queue)
         └─────→ Delivery Services
                  ├─ Webhook
                  ├─ Email (SMTP)
                  ├─ WhatsApp (Meta API)
                  └─ Google Sheets
```

### Key Components

1. **API Layer**: FastAPI with 100+ endpoints
2. **Database**: PostgreSQL with 30+ tables
3. **Cache**: Redis for performance
4. **Delivery**: Multi-channel delivery system
5. **Admin Panel**: Full-featured web interface
6. **Client Portal**: Self-service client dashboard

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.124
- **Language**: Python 3.12
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 16
- **Cache**: Redis 7.0
- **Authentication**: JWT (PyJWT)

### Frontend
- **HTML5/CSS3/JavaScript**
- **DataTables** for table management
- **Chart.js** for analytics
- **Fetch API** for async requests

### Infrastructure
- **Web Server**: Uvicorn (ASGI)
- **Reverse Proxy**: Nginx (recommended)
- **Process Manager**: Systemd/Supervisor
- **Monitoring**: Built-in performance tracking

---

## 📦 Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7.0+
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/hamedniavand/Leadex.git
cd Leadex
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb leadex

# Run migrations
alembic upgrade head
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Start the application**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. **Access the application**
- Admin Panel: `http://localhost:8000/admin-login.html`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/leadex

# Security
SECRET_KEY=your-secure-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@leadex.com

# WhatsApp (Optional)
META_ACCESS_TOKEN=your-meta-access-token
META_PHONE_NUMBER_ID=your-phone-number-id
META_BUSINESS_ACCOUNT_ID=your-business-account-id

# Google Sheets (Optional)
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Application
ENVIRONMENT=production
DEBUG=False
```

### First Run Setup

After installation, create your first admin user:

```bash
python -m app.cli create-admin
```

---

## 📚 API Documentation

### Interactive API Docs

- **Swagger UI**: `http://your-domain/docs`
- **ReDoc**: `http://your-domain/redoc`

### Key Endpoints

#### Authentication
```
POST /api/admin/auth/login
POST /api/client/auth/login
```

#### Lead Management
```
GET    /api/admin/leads/
POST   /api/admin/leads/
GET    /api/admin/leads/{id}
DELETE /api/admin/leads/{id}
POST   /api/admin/leads/{id}/resend
POST   /api/admin/leads/bulk/delete
```

#### Client Management
```
GET    /api/admin/clients/
POST   /api/admin/clients/
GET    /api/admin/clients/{id}
PUT    /api/admin/clients/{id}
DELETE /api/admin/clients/{id}
```

#### Reports
```
GET /api/admin/reports/quick/lead-summary
GET /api/admin/reports/quick/performance
GET /api/admin/reports/quick/revenue
GET /api/admin/reports/quick/clients
GET /api/admin/reports/quick/webhooks
```

#### Analytics
```
GET /api/admin/analytics/overview
GET /api/admin/analytics/conversion-funnel
GET /api/admin/analytics/client-performance
```

---

## 📊 Features Overview

### Admin Panel Features

- **Dashboard**: Real-time metrics and charts
- **Lead Management**: View, search, filter, bulk actions
- **Client Management**: Add, edit, configure delivery methods
- **Reports**: Generate and export 6 types of reports
- **Analytics**: Performance trends and insights
- **Settings**: System configuration

### Client Portal Features

- **Dashboard**: View assigned leads and statistics
- **Lead Access**: View lead details via secure link
- **Statistics**: Track deliveries and performance
- **Self-Service**: Manage account settings

### Delivery Channels

1. **Webhook**: POST JSON to client endpoints
   - Retry logic with exponential backoff
   - Custom headers support
   - Success/failure tracking

2. **Google Sheets**: Append leads to spreadsheets
   - Service account authentication
   - Auto-row appending
   - 7-field format (clean data)

3. **Email**: Send formatted emails
   - HTML templates
   - SMTP configuration
   - Delivery tracking

4. **WhatsApp**: Send via Meta Business API
   - Template support
   - Media attachments
   - Delivery status

---

## ✅ System Status & Verified Features

### Fully Operational Components

#### Admin Panel (All Features Working)
- ✅ **Dashboard** - Real-time stats, client list, recent leads
- ✅ **Lead Management** - List, filter, view details, bulk operations, CSV export
- ✅ **Client Management** - Create, edit, view details, manage credits
- ✅ **Reports System** - All 6 report types functional:
  - Lead Summary Report (status breakdown, by client, date trends)
  - Performance Report (success rates, delivery methods)
  - Revenue Report (credits usage, client spending)
  - Client Report (detailed client information)
  - Webhook Activity Report (recent deliveries, statistics)
  - Complete CSV Export
- ✅ **Analytics** - Performance tracking and metrics

#### Core Functionality (Production Ready)
- ✅ **Lead Capture** - Landing page submissions with validation
- ✅ **Duplicate Detection** - 20-day window, silent handling
- ✅ **Credit System** - Auto-deduction, refund on failure
- ✅ **Distribution Engine** - Percentage-based allocation
- ✅ **Multi-Channel Delivery**:
  - Webhook (JSON POST with retry logic)
  - Google Sheets (service account, 7-field format)
  - Email (SMTP, HTML templates)
  - WhatsApp (setup guide available)

#### Client Portal
- ✅ **Authentication** - Token + optional password
- ✅ **Lead Access** - View assigned leads
- ✅ **Statistics** - Delivery counts and performance

### Recent Fixes & Improvements
- Fixed Delivery model timestamp references across all endpoints
- Improved API response structure consistency
- Enhanced error handling in frontend components
- Optimized database queries for reports
- Stabilized client and lead detail views

### Integration Status
- ✅ Google Sheets - Fully configured and tested
- ⚙️ WhatsApp - Setup guide available (WHATSAPP_SETUP_GUIDE.md)
- ✅ Webhooks - Production ready with retry logic
- ✅ Email - SMTP integration functional

---

## 🗄️ Database Schema

The system uses 30+ tables including:

- **Core**: assets, clients, deliveries
- **Auth**: admin_users, sessions
- **Features**: lead_notes, lead_tags, custom_fields
- **Analytics**: performance_metrics, conversion_tracking
- **Reports**: reports, report_exports
- **Webhooks**: webhook_subscriptions, webhook_logs

Full schema documentation available in `/docs/database-schema.md`

---

## 🔐 Security Best Practices

1. **Change Default Credentials**: Update all default passwords immediately
2. **Use Strong Secrets**: Generate secure random keys for SECRET_KEY
3. **Enable HTTPS**: Use SSL/TLS in production
4. **Configure CORS**: Restrict origins appropriately
5. **Rate Limiting**: Enable and configure rate limits
6. **Regular Updates**: Keep dependencies updated
7. **Backup Database**: Regular automated backups
8. **Monitor Logs**: Track suspicious activity

---

## 🚀 Production Deployment

### Recommended Setup

1. **Web Server**: Nginx as reverse proxy
2. **Application**: Uvicorn with multiple workers
3. **Process Manager**: Systemd or Supervisor
4. **Database**: PostgreSQL with replication
5. **Cache**: Redis with persistence
6. **Monitoring**: Application logs and metrics
7. **Backups**: Automated database backups

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service Example

```ini
[Unit]
Description=Leadex FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/leadex
Environment="PATH=/var/www/leadex/venv/bin"
ExecStart=/var/www/leadex/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_leads.py
```

---

## 📈 Performance Tips

1. **Enable Redis Caching**: Significantly improves response times
2. **Use Connection Pooling**: Configure appropriate pool size
3. **Optimize Queries**: Use indexes and query optimization
4. **Enable Gzip**: Compress API responses
5. **CDN**: Serve static assets via CDN
6. **Database Tuning**: Optimize PostgreSQL configuration

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Powerful database
- [Redis](https://redis.io/) - In-memory data store
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

---

## 📞 Support

For questions, issues, or feature requests:
- **Issues**: [GitHub Issues](https://github.com/hamedniavand/Leadex/issues)
- **Documentation**: Check `/docs` folder
- **API Docs**: Visit `/docs` endpoint when running

---

## 🗺️ Roadmap

- [ ] Mobile app (iOS/Android)
- [ ] Advanced AI-powered lead scoring
- [ ] Integration marketplace
- [ ] Multi-language support
- [ ] Advanced workflow automation
- [ ] Custom dashboard builder

---

**Made with ❤️ for lead management professionals**
