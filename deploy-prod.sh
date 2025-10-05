#!/bin/bash
set -e  # Exit on any error

echo "🚀 Starting Aura Production Deployment..."

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: Must run from application root directory"
    exit 1
fi

# Check environment
if [ "$FLASK_ENV" != "production" ]; then
    echo "❌ Error: Must set FLASK_ENV=production"
    echo "💡 Run: export FLASK_ENV=production"
    exit 1
fi

# Check for required files
REQUIRED_FILES=("requirements.txt" ".env.production" "run.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

APP_DIR="/var/www/aura"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/aura"

echo "📦 Stopping services..."
sudo systemctl stop aura-app || true

echo "🔧 Setting up environment..."
sudo mkdir -p $APP_DIR $LOG_DIR
sudo chown -R www-data:www-data $APP_DIR $LOG_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod 600 $APP_DIR/.env.production

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    sudo -u www-data python3 -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

echo "📚 Installing dependencies..."
sudo -u www-data $VENV_DIR/bin/pip install --upgrade pip
sudo -u www-data $VENV_DIR/bin/pip install -r requirements.txt

echo "🗄️  Initializing database..."
sudo -u www-data $VENV_DIR/bin/python database.py init

echo "⚙️  Setting up services..."
sudo cp deployment/aura-app.service /etc/systemd/system/
sudo cp deployment/gunicorn.conf.py $APP_DIR/

sudo systemctl daemon-reload
sudo systemctl enable aura-app

echo "🔒 Setting up firewall..."
sudo ufw allow 5000/tcp comment "Aura App"
sudo ufw allow 80/tcp comment "HTTP"
sudo ufw allow 443/tcp comment "HTTPS"

echo "🚀 Starting application..."
sudo systemctl start aura-app

echo "⏳ Waiting for application to start..."
sleep 5

# Check if application is running
if sudo systemctl is-active --quiet aura-app; then
    echo "✅ Application is running successfully"
    
    # Test the health endpoint
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "⚠️  Health check failed, but service is running"
    fi
else
    echo "❌ Application failed to start"
    sudo systemctl status aura-app --no-pager
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "🌐 Application should be available at: http://your-server:5000"
echo "📋 Next steps:"
echo "   - Set up Nginx reverse proxy"
echo "   - Configure SSL certificate"
echo "   - Set up domain name"
echo "   - Configure monitoring"