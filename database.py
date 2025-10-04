from app import create_app, db
from models.user import User
from models.product_analysis import ProductAnalysis
from models.points import PointsHistory, LoginStreak
import sqlalchemy as sa
from sqlalchemy import inspect, text

def init_db():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Enable foreign key constraints (works for SQLite and others)
            enable_foreign_keys()
            
            # Add missing columns if needed
            add_missing_columns()
            
            # Verify tables were created
            verify_tables()
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

def enable_foreign_keys():
    """Enable foreign key constraints for supported databases"""
    try:
        if db.engine.url.drivername == 'sqlite':
            db.session.execute(text('PRAGMA foreign_keys = ON'))
        db.session.commit()
        print("✅ Foreign key constraints enabled")
    except Exception as e:
        print(f"⚠️  Could not enable foreign keys: {e}")

def add_missing_columns():
    """Add missing columns to existing tables"""
    inspector = inspect(db.engine)
    
    # Check and add product_name column if missing
    if 'product_analyses' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('product_analyses')]
        
        if 'product_name' not in existing_columns:
            print("🔄 Adding product_name column to product_analyses table...")
            try:
                db.session.execute(text('ALTER TABLE product_analyses ADD COLUMN product_name VARCHAR(200)'))
                db.session.commit()
                print("✅ Successfully added product_name column")
            except Exception as e:
                print(f"❌ Failed to add product_name column: {e}")
                db.session.rollback()
        else:
            print("✅ product_name column already exists")

def verify_tables():
    """Verify that all expected tables were created"""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    expected_tables = ['users', 'product_analyses', 'points_history', 'login_streaks']
    
    created_tables = [table for table in expected_tables if table in tables]
    missing_tables = [table for table in expected_tables if table not in tables]
    
    if created_tables:
        print(f"✅ Created tables: {', '.join(created_tables)}")
    if missing_tables:
        print(f"❌ Missing tables: {', '.join(missing_tables)}")

def reset_db():
    """Drop and recreate all tables (for development)"""
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("🗑️  All tables dropped")
            
            # Create all tables
            db.create_all()
            print("✅ Database recreated successfully!")
            
            # Enable foreign key constraints
            enable_foreign_keys()
            
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
            db.session.rollback()
            raise

def create_sample_data():
    """Create sample data for testing (optional)"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if sample user already exists
            if not User.query.filter_by(email='demo@aura.com').first():
                # Create sample user
                demo_user = User(
                    username='demo',
                    email='demo@aura.com'
                )
                demo_user.set_password('demo123')
                db.session.add(demo_user)
                db.session.commit()
                print("✅ Sample user created: demo@aura.com / demo123")
                
                # Create sample analyses with product names
                sample_analyses = [
                    {
                        'product_name': 'Organic Aloe Vera Shampoo',
                        'ingredients': 'Organic Aloe Vera Leaf Juice, Citric Acid, Potassium Sorbate, Sodium Benzoate',
                        'rating': 'friendly',
                        'points': 85
                    },
                    {
                        'product_name': 'Commercial Body Wash',
                        'ingredients': 'Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Fragrance, DMDM Hydantoin',
                        'rating': 'harmful',
                        'points': 25
                    },
                    {
                        'product_name': 'Natural Coconut Lotion',
                        'ingredients': 'Organic Coconut Oil, Shea Butter, Essential Oils, Vitamin E',
                        'rating': 'friendly',
                        'points': 95
                    }
                ]
                
                for sample in sample_analyses:
                    analysis = ProductAnalysis(
                        user_id=demo_user.id,
                        product_name=sample['product_name'],
                        ingredients_text=sample['ingredients'],
                        environmental_rating=sample['rating'],
                        points_awarded=sample['points'],
                        analysis_result=f"Sample analysis for {sample['product_name']}.",
                        alternative_suggestions="Consider these eco-friendly alternatives for better environmental impact."
                    )
                    db.session.add(analysis)
                    db.session.flush()  # Get the analysis ID without committing
                    
                    # Add points history
                    points = PointsHistory(
                        user_id=demo_user.id,
                        points=sample['points'],
                        source_type='analysis',
                        source_id=analysis.id
                    )
                    db.session.add(points)
                
                db.session.commit()
                print("✅ Sample analysis data created with product names")
            else:
                print("ℹ️  Sample data already exists")
                
        except Exception as e:
            print(f"❌ Sample data creation failed: {e}")
            db.session.rollback()
            raise

def check_db_connection():
    """Check if database connection is working"""
    app = create_app()
    
    try:
        with app.app_context():
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            
            # Check tables exist
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Found {len(tables)} tables")
            
            # Check if product_name column exists and has data
            if 'product_analyses' in tables:
                try:
                    analysis_count = ProductAnalysis.query.count()
                    analysis_with_name = ProductAnalysis.query.filter(
                        ProductAnalysis.product_name.isnot(None)
                    ).count()
                    print(f"✅ Product analyses: {analysis_count} total, {analysis_with_name} with product names")
                except Exception as e:
                    print(f"⚠️  Error querying product analyses: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def backup_database():
    """Create a backup of the database (simple file copy for SQLite)"""
    import shutil
    import os
    from datetime import datetime
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/aura_backup_{timestamp}.db"
    
    try:
        # Get database URL from config
        app = create_app()
        database_url = app.config['SQLALCHEMY_DATABASE_URI']
        
        if database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_file)
                print(f"✅ Database backed up to: {backup_file}")
                return backup_file
            else:
                print(f"❌ Database file not found: {db_path}")
                return None
        else:
            print("⚠️  Backup currently only supported for SQLite databases")
            return None
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def migrate_existing_data():
    """Migrate existing data to include product names"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all existing analyses without product names
            analyses_without_names = ProductAnalysis.query.filter(
                (ProductAnalysis.product_name.is_(None)) | 
                (ProductAnalysis.product_name == '')
            ).all()
            
            if analyses_without_names:
                print(f"🔄 Migrating {len(analyses_without_names)} existing analyses...")
                
                migrated_count = 0
                for analysis in analyses_without_names:
                    # Extract potential product name from ingredients (first few words)
                    ingredients = analysis.ingredients_text or ""
                    first_line = ingredients.split('\n')[0] if '\n' in ingredients else ingredients
                    words = first_line.split()[:4]  # Take first 4 words
                    potential_name = ' '.join(words).strip(',. ')
                    
                    # Set a generic name if extraction fails
                    if len(potential_name) < 2:
                        potential_name = "Personal Care Product"
                    
                    analysis.product_name = potential_name
                    migrated_count += 1
                
                db.session.commit()
                print(f"✅ Successfully migrated {migrated_count} analyses with product names")
            else:
                print("ℹ️  No existing data needs migration")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    import sys
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'init'
    
    commands = {
        'init': init_db,
        'reset': reset_db,
        'sample': lambda: (init_db(), create_sample_data()),
        'check': check_db_connection,
        'backup': backup_database,
        'migrate': migrate_existing_data
    }
    
    if command in commands:
        try:
            if command == 'sample':
                init_db()
                create_sample_data()
            else:
                commands[command]()
        except Exception as e:
            print(f"❌ Command '{command}' failed: {e}")
            exit(1)
    else:
        print("Available commands:")
        print("  init    - Initialize database")
        print("  reset   - Reset database (drop and recreate)")
        print("  sample  - Initialize with sample data")
        print("  check   - Check database connection")
        print("  backup  - Create database backup")
        print("  migrate - Migrate existing data to include product names")
        print("\n💡 Usage: python database.py [init|reset|sample|check|backup|migrate]")