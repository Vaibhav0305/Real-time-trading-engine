# 🚀 VittCott Trading Platform - Production Deployment Guide

This guide covers the complete production deployment of the VittCott Trading Platform, including live market data integration, security hardening, and monitoring setup.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or later
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 100GB+ SSD
- **Network**: Stable internet connection with static IP

### Domain & SSL
- **Domain**: Registered domain (e.g., `vittcott.com`)
- **SSL Certificate**: Let's Encrypt (free) or commercial certificate
- **DNS**: Configured to point to your server

### API Keys Required
- **Alpha Vantage**: [Get API Key](https://www.alphavantage.co/support/#api-key)
- **Polygon.io**: [Get API Key](https://polygon.io/)
- **Finnhub**: [Get API Key](https://finnhub.io/)
- **Twilio**: [Get Account](https://www.twilio.com/) (for SMS OTP)
- **Email Service**: Gmail App Password or SMTP credentials

## 🛠️ Deployment Options

### Option 1: Traditional Server Deployment
```bash
# Clone the deployment script
git clone https://github.com/yourusername/vittcott-trading.git
cd vittcott-trading

# Make deployment script executable
chmod +x deploy/production_deploy.sh

# Run deployment
./deploy/production_deploy.sh
```

### Option 2: Docker Compose Deployment
```bash
# Copy environment template
cp .env.example .env.production

# Edit environment variables
nano .env.production

# Start services
docker-compose -f docker-compose.production.yml up -d
```

### Option 3: Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f deploy/kubernetes/

# Check deployment status
kubectl get pods -n vittcott
```

## 🔧 Configuration

### Environment Variables
Create `.env.production` file:

```bash
# Application Settings
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=false
ENVIRONMENT=production

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database Configuration
DATABASE_URL=postgresql://vittcott:your_password@localhost/vittcott
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# External API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
FINNHUB_API_KEY=your_finnhub_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@vittcott.com

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone

# SSL Configuration
SSL_CERT_FILE=/etc/letsencrypt/live/vittcott.com/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/vittcott.com/privkey.pem
```

### Database Setup
```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database and user
CREATE DATABASE vittcott;
CREATE USER vittcott WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vittcott TO vittcott;

-- Exit
\q
```

### Redis Configuration
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Add/modify these lines:
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Install UFW
sudo apt install ufw

# Configure firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### SSL/TLS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d vittcott.com -d www.vittcott.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Security Headers
Add to Nginx configuration:
```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

## 📊 Monitoring & Observability

### Prometheus Configuration
Create `deploy/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vittcott-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'vittcott-frontend'
    static_configs:
      - targets: ['frontend:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana Dashboards
Import these dashboard IDs:
- **System Overview**: 1860
- **PostgreSQL**: 9628
- **Redis**: 763
- **Custom VittCott Metrics**: Create custom dashboard

### Health Checks
```bash
# Backend health
curl -f http://localhost:8000/health

# Frontend health
curl -f http://localhost:3000

# Database health
pg_isready -h localhost -U vittcott

# Redis health
redis-cli ping
```

## 🚀 Live Market Data Integration

### Market Data Providers Setup

#### 1. Alpha Vantage
- **Rate Limit**: 5 requests/minute (free), 500/minute (paid)
- **Features**: Real-time quotes, historical data, technical indicators
- **Setup**: Add API key to environment variables

#### 2. Polygon.io
- **Rate Limit**: 100 requests/minute (free), 1000/minute (paid)
- **Features**: Real-time market data, options data, forex
- **Setup**: Add API key to environment variables

#### 3. Finnhub
- **Rate Limit**: 60 requests/minute (free), 1000/minute (paid)
- **Features**: Real-time quotes, news sentiment, earnings
- **Setup**: Add API key to environment variables

#### 4. Yahoo Finance (Fallback)
- **Rate Limit**: No strict limits
- **Features**: Free real-time and historical data
- **Setup**: No API key required

### Market Data Service Features
- **Multi-provider fallback**: Automatically switches between providers
- **Rate limiting**: Respects API limits and caches data
- **Real-time updates**: WebSocket streaming for live data
- **Historical data**: 1-minute to yearly intervals
- **Market sentiment**: VIX-based sentiment calculation

## 📈 Performance Optimization

### Backend Optimization
```python
# Gunicorn configuration
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5
```

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_timestamp ON orders(timestamp);

-- Enable query optimization
ANALYZE orders;
```

### Caching Strategy
```python
# Redis caching layers
CACHE_TTL = {
    'quotes': 300,        # 5 minutes
    'historical': 3600,   # 1 hour
    'user_data': 1800,   # 30 minutes
    'market_summary': 300 # 5 minutes
}
```

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Create backup script
sudo nano /opt/vittcott/backup.sh

#!/bin/bash
BACKUP_DIR="/opt/vittcott/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h localhost -U vittcott vittcott > $BACKUP_DIR/db_$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/vittcott/app

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Recovery Procedures
```bash
# Database recovery
psql -h localhost -U vittcott vittcott < backup_file.sql

# Application recovery
tar -xzf backup_file.tar.gz -C /
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status vittcott-backend

# Check logs
sudo journalctl -u vittcott-backend -f

# Check configuration
sudo nginx -t
```

#### 2. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U vittcott -d vittcott

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 3. Market Data Not Working
```bash
# Check API keys
echo $ALPHA_VANTAGE_API_KEY
echo $POLYGON_API_KEY

# Test API endpoints
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY"
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check Nginx SSL configuration
sudo nginx -t
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Check service health and logs
- **Weekly**: Review performance metrics and error logs
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and optimize database performance

### Monitoring Alerts
Set up alerts for:
- Service downtime
- High CPU/memory usage
- Database connection issues
- SSL certificate expiration
- API rate limit warnings

### Update Procedures
```bash
# Update application
cd /opt/vittcott/app
git pull origin main

# Update dependencies
source /opt/vittcott/venv/bin/activate
pip install -r backend/requirements.production.txt

# Restart services
sudo systemctl restart vittcott-backend
sudo systemctl restart nginx
```

## 🎯 Next Steps

After successful deployment:

1. **Test all functionality**:
   - User registration and login
   - OTP verification
   - Live market data
   - Algorithmic trading
   - AI chatbot

2. **Set up monitoring**:
   - Configure Grafana dashboards
   - Set up alerting
   - Monitor performance metrics

3. **Security audit**:
   - Run security scans
   - Review access logs
   - Test authentication flows

4. **Performance tuning**:
   - Optimize database queries
   - Tune caching strategies
   - Monitor response times

5. **Documentation**:
   - Update user documentation
   - Create admin procedures
   - Document troubleshooting steps

---

## 📚 Additional Resources

- [FastAPI Production Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/runtime-config-query.html)
- [Redis Best Practices](https://redis.io/topics/optimization)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [SSL/TLS Security](https://ssl-config.mozilla.org/)

---

**🎉 Congratulations!** Your VittCott Trading Platform is now production-ready with live market data integration, enterprise-grade security, and comprehensive monitoring.
