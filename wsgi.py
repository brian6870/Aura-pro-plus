from app import create_app, db

# Create the Flask application instance
app = create_app()

# Optional: Make it available as 'application' for WSGI servers that expect that name
application = app

# Do NOT auto-create tables here during imports.
# Flask-Migrate handles schema creation via `flask db upgrade`.

if __name__ == "__main__":
    with app.app_context():
        # Only create tables automatically when running locally (optional)
        try:
            db.create_all()
            print("✅ Database tables verified/created successfully.")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

    print("🚀 Starting Aura Carbon Footprint Tracker...")
    app.run(host="0.0.0.0", port=5000, debug=True)
