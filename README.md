# 🌊 Silay DRRMO Flood Management System with Web GIS

A comprehensive flood monitoring and management system for Silay City DRRMO (Disaster Risk Reduction and Management Office) featuring real-time weather data integration, GIS visualization, and intelligent flood prediction.

## 🌟 Features

### Core Functionality
- **Real-time Weather Monitoring** - Integration with Open-Meteo API for current weather data
- **Tide Level Tracking** - WorldTides API integration for coastal flood risk assessment
- **GIS Visualization** - Interactive maps with barangay boundaries and flood zones using OpenLayers
- **Flood Risk Assessment** - Multi-factor analysis combining rainfall, tide levels, and historical data
- **Intelligent Predictions** - AI-powered flood forecasting with 7-day weather outlook
- **Activity Tracking** - Comprehensive audit logs for all user actions

### User Management
- **Multi-level Authentication** - Admin and staff roles with approval workflow
- **Profile Management** - User profiles with contact information and emergency contacts
- **Login Security** - Failed attempt tracking and rate limiting
- **Activity History** - Personal and system-wide activity logs

### Reporting & Documentation
- **Assessment Records** - Location-based flood risk assessments
- **Certificate Generation** - Flood susceptibility certificates for establishments
- **Detailed Reports** - Comprehensive flood risk analysis with recommendations
- **Historical Data** - Flood event records with damage and casualty tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12+ with PostGIS extension
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd -CAPSTONE-FMSWGIS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/Mac
   
   # Edit .env and add your actual credentials
   ```

5. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb silaydrrmo_db
   
   # Enable PostGIS extension
   psql -d silaydrrmo_db -c "CREATE EXTENSION postgis;"
   
   # Run migrations
   python manage.py migrate
   ```

6. **Load GIS data**
   ```bash
   python manage.py load_shapefiles
   ```

7. **Create admin account**
   ```bash
   # Use the admin registration page or create superuser
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    ```
    http://localhost:8000/
    ```

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=silaydrrmo_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# API Keys
WORLDTIDES_API_KEY=your-worldtides-api-key

# Security
ADMIN_REGISTRATION_KEY=your-admin-key
```

### Generate Secret Key

```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 📊 Technology Stack

### Backend
- **Django 5.2.7** - Web framework
- **PostgreSQL with PostGIS** - Spatial database
- **GeoDjango** - Geographic framework
- **Python 3.x** - Programming language

### Frontend
- **Bootstrap 5** - UI framework
- **OpenLayers** - Web mapping library
- **Chart.js** - Data visualization
- **JavaScript** - Client-side scripting

### APIs & Services
- **Open-Meteo API** - Weather data (free)
- **WorldTides API** - Tide predictions

## 📁 Project Structure

```
-CAPSTONE-FMSWGIS/
├── maps/                   # GIS and mapping functionality
│   ├── models.py          # Barangay, FloodSusceptibility models
│   ├── views.py           # Map views, reports, certificates
│   └── management/        # Management commands
├── monitoring/            # Weather and flood monitoring
│   ├── models.py         # RainfallData, WeatherData, FloodRecord
│   ├── views.py          # Monitoring dashboard, predictions
│   └── forms.py          # FloodRecord form with validation
├── users/                # User authentication and management
│   ├── models.py        # CustomUser, UserLog, LoginAttempt
│   ├── views.py         # Auth views, profile management
│   └── forms.py         # User registration and profile forms
├── silay_drrmo/         # Project settings
│   ├── settings.py      # Configuration
│   └── urls.py          # URL routing
├── static/              # Static files (CSS, JS, images)
├── staticfiles/         # Collected static files
├── media/               # User uploads
└── logs/                # Application logs
```

## 🔐 Security Features

- ✅ Environment variable configuration
- ✅ Failed login attempt tracking
- ✅ User approval workflow
- ✅ CSRF protection
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection
- ✅ Secure password hashing
- ✅ Session security

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test maps
python manage.py test monitoring

# Check code coverage
coverage run manage.py test
coverage report
```

## 📝 Management Commands

### Load GIS Data
```bash
python manage.py load_shapefiles
```

### Create Admin User
```bash
python manage.py createsuperuser
```

### Database Operations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

### Check for Issues
```bash
# Development check
python manage.py check

# Production readiness check
python manage.py check --deploy
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Generate new `SECRET_KEY`
- [ ] Set up SSL/HTTPS
- [ ] Configure static files serving (nginx/Apache)
- [ ] Set up database backups
- [ ] Configure email settings
- [ ] Enable logging
- [ ] Set up monitoring (Sentry)

### Recommended Deployment Platforms
- **Heroku** - Easy deployment with PostgreSQL add-on
- **DigitalOcean** - Droplets with full control
- **AWS** - Elastic Beanstalk or EC2
- **PythonAnywhere** - Simple Python hosting

## 👥 User Roles

### Administrator
- Full system access
- User approval and management
- System configuration
- View all activities

### Staff
- Create assessments and reports
- Generate certificates
- Record flood events
- View monitoring data
- Access personal activity history

## 📈 Features by Module

### Maps Module
- Interactive GIS visualization
- Barangay boundary display
- Flood susceptibility zones
- Location-based assessments
- Risk reports generation
- Certificate issuance

### Monitoring Module
- Real-time weather data
- Rainfall monitoring
- Tide level tracking
- 7-day weather forecast
- Flood event records
- Historical data analysis
- Intelligent predictions

### Users Module
- User registration
- Admin approval workflow
- Profile management
- Activity tracking
- Login security
- Audit logs

## 🐛 Troubleshooting

### Common Issues

**Issue**: Can't import psycopg2
```bash
pip install psycopg2-binary
```

**Issue**: PostGIS not found
```bash
# Install PostGIS on your PostgreSQL installation
# Windows: Download from PostgreSQL Application Stack Builder
# Linux: sudo apt-get install postgis
```

**Issue**: Static files not loading
```bash
python manage.py collectstatic --noinput
```

**Issue**: Migration conflicts
```bash
python manage.py migrate --fake-initial
```

## 📞 Support

For issues or questions:
1. Check the `CODE_REVIEW_REPORT.md` for detailed information
2. See `QUICK_FIX_CHECKLIST.md` for common fixes
3. Contact the development team

## 📄 License

This project is developed as a capstone project for educational purposes.

## 🙏 Acknowledgments

- Silay City DRRMO for project requirements
- Open-Meteo for free weather API
- WorldTides for tide data API
- OpenLayers community for GIS tools
- Django community for excellent documentation

---

**Version**: 1.0.0  
**Last Updated**: November 15, 2025  
**Status**: ✅ Production Ready (with environment configuration)

Made with ❤️ for Silay City DRRMO
