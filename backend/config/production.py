import os
from typing import Optional

class ProductionConfig:
    """Production configuration for VittCott Trading Platform"""
    
    # Application Settings
    APP_NAME = "VittCott Trading Platform"
    VERSION = "2.0.0"
    DEBUG = False
    ENVIRONMENT = "production"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    WORKERS = int(os.getenv("WORKERS", "4"))
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/vittcott")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # External API Keys (Market Data)
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    YAHOO_FINANCE_ENABLED = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    
    # Trading Engine Configuration
    TRADING_ENGINE_HOST = os.getenv("TRADING_ENGINE_HOST", "localhost")
    TRADING_ENGINE_PORT = int(os.getenv("TRADING_ENGINE_PORT", "9000"))
    MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))
    
    # Risk Management
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "100000"))
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "50000"))
    MAX_LEVERAGE = float(os.getenv("MAX_LEVERAGE", "2.0"))
    
    # Performance Settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    MAX_CONCURRENT_STRATEGIES = int(os.getenv("MAX_CONCURRENT_STRATEGIES", "50"))
    STRATEGY_TIMEOUT = int(os.getenv("STRATEGY_TIMEOUT", "30"))  # seconds
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "/var/log/vittcott/app.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring & Health Checks
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Email Configuration (for OTP and notifications)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@vittcott.com")
    
    # SMS Configuration (for OTP)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # CORS Settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://vittcott.com,https://app.vittcott.com").split(",")
    
    # SSL/TLS Configuration
    SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "")
    SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "")
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate production configuration and return any issues"""
        issues = []
        
        if cls.SECRET_KEY == "change-this-in-production":
            issues.append("SECRET_KEY must be changed from default value")
        
        if not cls.ALPHA_VANTAGE_API_KEY and not cls.POLYGON_API_KEY and not cls.FINNHUB_API_KEY:
            issues.append("At least one market data API key must be configured")
        
        if not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD:
            issues.append("SMTP credentials must be configured for OTP emails")
        
        if not cls.TWILIO_ACCOUNT_SID or not cls.TWILIO_AUTH_TOKEN:
            issues.append("Twilio credentials must be configured for SMS OTP")
        
        return issues

# Production configuration instance
config = ProductionConfig()
