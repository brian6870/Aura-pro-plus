from app import create_app

# Create the Flask application instance
app = create_app()

# Optional: Make it available as 'application' for WSGI servers that expect that name
application = app

# Optional: Initialize database
with app.app_context():
    from app import db
    db.create_all()

if __name__ == "__main__":
    app.run()