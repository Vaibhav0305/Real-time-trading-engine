#!/bin/bash

# VittCott Trading Platform - Production Deployment Script
# This script deploys the platform to production environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="vittcott-trading"
APP_USER="vittcott"
APP_DIR="/opt/vittcott"
LOG_DIR="/var/log/vittcott"
SERVICE_DIR="/etc/systemd/system"
ENV_FILE=".env.production"

echo -e "${BLUE}🚀 Starting VittCott Trading Platform Production Deployment${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if user exists, create if not
if ! id "$APP_USER" &>/dev/null; then
    print_warning "User $APP_USER does not exist. Creating..."
    sudo useradd -r -s /bin/bash -d $APP_DIR $APP_USER
    print_status "User $APP_USER created"
fi

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR
sudo chown $APP_USER:$APP_USER $LOG_DIR

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    redis-server \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    supervisor \
    htop \
    curl \
    wget \
    git \
    build-essential \
    cmake \
    libssl-dev \
    libffi-dev

# Install Python dependencies
print_status "Installing Python dependencies..."
cd $APP_DIR
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install wheel setuptools

# Clone or update application code
if [ -d "$APP_DIR/app" ]; then
    print_status "Updating application code..."
    cd $APP_DIR/app
    git pull origin main
else
    print_status "Cloning application code..."
    cd $APP_DIR
    git clone https://github.com/yourusername/vittcott-trading.git app
    cd app
fi

# Install Python requirements
print_status "Installing Python requirements..."
pip install -r backend/requirements.txt

# Install additional production dependencies
pip install \
    gunicorn \
    uvicorn[standard] \
    psycopg2-binary \
    yfinance \
    aiohttp \
    prometheus-client \
    sentry-sdk

# Setup environment variables
print_status "Setting up environment variables..."
if [ ! -f "$APP_DIR/$ENV_FILE" ]; then
    print_warning "Environment file not found. Creating template..."
    cat > $APP_DIR/$ENV_FILE << EOF
# VittCott Trading Platform - Production Environment Variables
# Copy this file to .env and fill in your actual values

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
REDIS_PASSWORD=
REDIS_DB=0

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
EOF
    print_warning "Please edit $APP_DIR/$ENV_FILE with your actual values"
fi

# Setup PostgreSQL database
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE vittcott;
CREATE USER vittcott WITH ENCRYPTED PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE vittcott TO vittcott;
\q
EOF

# Setup Redis
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create systemd service files
print_status "Creating systemd services..."

# Backend service
cat > $SERVICE_DIR/vittcott-backend.service << EOF
[Unit]
Description=VittCott Trading Platform Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR/app/backend
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend service (if using Node.js)
cat > $SERVICE_DIR/vittcott-frontend.service << EOF
[Unit]
Description=VittCott Trading Platform Frontend
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR/app/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
print_status "Setting up Nginx..."
sudo tee /etc/nginx/sites-available/vittcott << EOF
server {
    listen 80;
    server_name vittcott.com www.vittcott.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vittcott.com www.vittcott.com;

    ssl_certificate /etc/letsencrypt/live/vittcott.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vittcott.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        root $APP_DIR/app/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site and restart Nginx
sudo ln -sf /etc/nginx/sites-available/vittcott /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL certificate (if domain is configured)
if [ -n "$DOMAIN" ]; then
    print_status "Setting up SSL certificate..."
    sudo certbot --nginx -d vittcott.com -d www.vittcott.com --non-interactive --agree-tos --email your-email@vittcott.com
fi

# Setup log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/vittcott << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload vittcott-backend
    endscript
}
EOF

# Setup monitoring and health checks
print_status "Setting up monitoring..."
sudo mkdir -p /etc/monitoring
sudo tee /etc/monitoring/vittcott-health.sh << EOF
#!/bin/bash
# Health check script for VittCott services

BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Check backend
if curl -f -s \$BACKEND_URL > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    exit 1
fi

# Check frontend
if curl -f -s \$FRONTEND_URL > /dev/null; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
    exit 1
fi

echo "All services healthy"
EOF

sudo chmod +x /etc/monitoring/vittcott-health.sh

# Setup cron job for health checks
echo "*/5 * * * * /etc/monitoring/vittcott-health.sh >> $LOG_DIR/health.log 2>&1" | sudo crontab -

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $APP_USER:$APP_USER $APP_DIR
sudo chown -R $APP_USER:$APP_USER $LOG_DIR
sudo chmod +x $APP_DIR/app/backend/main.py

# Reload systemd and enable services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable vittcott-backend
sudo systemctl start vittcott-backend

# Final status check
print_status "Performing final status check..."
sleep 5

if sudo systemctl is-active --quiet vittcott-backend; then
    print_status "Backend service is running"
else
    print_error "Backend service failed to start"
    sudo systemctl status vittcott-backend
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx failed to start"
    exit 1
fi

# Print deployment summary
echo ""
echo -e "${GREEN}🎉 VittCott Trading Platform Production Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}Application Directory:${NC} $APP_DIR"
echo -e "${BLUE}Log Directory:${NC} $LOG_DIR"
echo -e "${BLUE}Backend Service:${NC} vittcott-backend"
echo -e "${BLUE}Frontend Service:${NC} vittcott-frontend"
echo -e "${BLUE}Database:${NC} PostgreSQL (vittcott)"
echo -e "${BLUE}Cache:${NC} Redis"
echo -e "${BLUE}Web Server:${NC} Nginx"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit $APP_DIR/$ENV_FILE with your actual values"
echo "2. Configure your domain DNS to point to this server"
echo "3. Run: sudo certbot --nginx -d yourdomain.com"
echo "4. Test the application at https://yourdomain.com"
echo "5. Monitor logs: sudo journalctl -u vittcott-backend -f"
echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"
