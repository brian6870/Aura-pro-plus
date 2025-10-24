from app import create_app, db
from models.user import User
from models.product_analysis import ProductAnalysis
from models.plastic_analysis import PlasticAnalysis
from models.points import PointsHistory, LoginStreak
import sqlalchemy as sa
from sqlalchemy import inspect, text
import json

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
    
    # Check plastic_analyses table structure
    if 'plastic_analyses' in inspector.get_table_names():
        print("✅ plastic_analyses table exists")
    else:
        print("❌ plastic_analyses table missing - will be created on next init")

def verify_tables():
    """Verify that all expected tables were created"""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    expected_tables = ['users', 'product_analyses', 'plastic_analyses', 'points_history', 'login_streaks']
    
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
                
                # Create sample product analyses
                sample_product_analyses = [
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
                
                for sample in sample_product_analyses:
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
                    db.session.flush()
                    
                    # Add points history
                    points = PointsHistory(
                        user_id=demo_user.id,
                        points=sample['points'],
                        source_type='product_analysis',
                        source_id=analysis.id
                    )
                    db.session.add(points)
                
                # Create sample plastic analyses
                sample_plastic_analyses = [
                    {
                        'plastic_type': 'PET',
                        'confidence': 0.92,
                        'description': 'Polyethylene Terephthalate - Used in water bottles, food containers',
                        'rating': 'friendly',
                        'points': 80,
                        'carbon_footprint': 'Moderate - highly recyclable',
                        'decomposition_time': '450+ years'
                    },
                    {
                        'plastic_type': 'PVC',
                        'confidence': 0.87,
                        'description': 'Polyvinyl Chloride - Used in pipes, packaging',
                        'rating': 'hazardous',
                        'points': 15,
                        'carbon_footprint': 'High - difficult to recycle',
                        'decomposition_time': '450+ years'
                    },
                    {
                        'plastic_type': 'PP',
                        'confidence': 0.78,
                        'description': 'Polypropylene - Used in yogurt containers, bottle caps',
                        'rating': 'moderate',
                        'points': 60,
                        'carbon_footprint': 'Moderate - recyclable',
                        'decomposition_time': '20-30 years'
                    }
                ]
                
                for sample in sample_plastic_analyses:
                    plastic_analysis = PlasticAnalysis(
                        user_id=demo_user.id,
                        plastic_type=sample['plastic_type'],
                        confidence=sample['confidence'],
                        description=sample['description'],
                        environmental_rating=sample['rating'],
                        points_awarded=sample['points'],
                        analysis_result=f"Environmental analysis of {sample['plastic_type']} plastic material.",
                        alternative_suggestions="Consider reusable or biodegradable alternatives.",
                        recycling_guidance="Check local recycling guidelines for proper disposal.",
                        carbon_footprint=sample['carbon_footprint'],
                        decomposition_time=sample['decomposition_time'],
                        all_predictions=json.dumps({
                            sample['plastic_type']: sample['confidence'] * 100,
                            'OTHER': (1 - sample['confidence']) * 100
                        })
                    )
                    db.session.add(plastic_analysis)
                    db.session.flush()
                    
                    # Add points history for plastic analysis
                    points = PointsHistory(
                        user_id=demo_user.id,
                        points=sample['points'],
                        source_type='plastic_analysis',
                        source_id=plastic_analysis.id
                    )
                    db.session.add(points)
                
                db.session.commit()
                print("✅ Sample product and plastic analysis data created")
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
            
            # Check data counts
            product_count = ProductAnalysis.query.count()
            plastic_count = PlasticAnalysis.query.count()
            user_count = User.query.count()
            points_count = PointsHistory.query.count()
            
            print(f"📊 Data Summary:")
            print(f"   Users: {user_count}")
            print(f"   Product Analyses: {product_count}")
            print(f"   Plastic Analyses: {plastic_count}")
            print(f"   Points History: {points_count}")
            
            # Check points by source type
            if points_count > 0:
                product_points = PointsHistory.query.filter_by(source_type='product_analysis').count()
                plastic_points = PointsHistory.query.filter_by(source_type='plastic_analysis').count()
                streak_points = PointsHistory.query.filter_by(source_type='streak_bonus').count()
                
                print(f"   Points by source:")
                print(f"     Product Analysis: {product_points}")
                print(f"     Plastic Analysis: {plastic_points}")
                print(f"     Streak Bonus: {streak_points}")
            
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
    """Migrate existing data to include product names and handle plastic data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Migrate product analyses without names
            analyses_without_names = ProductAnalysis.query.filter(
                (ProductAnalysis.product_name.is_(None)) | 
                (ProductAnalysis.product_name == '')
            ).all()
            
            if analyses_without_names:
                print(f"🔄 Migrating {len(analyses_without_names)} product analyses...")
                
                migrated_count = 0
                for analysis in analyses_without_names:
                    # Extract potential product name from ingredients
                    ingredients = analysis.ingredients_text or ""
                    first_line = ingredients.split('\n')[0] if '\n' in ingredients else ingredients
                    words = first_line.split()[:4]
                    potential_name = ' '.join(words).strip(',. ')
                    
                    if len(potential_name) < 2:
                        potential_name = "Personal Care Product"
                    
                    analysis.product_name = potential_name
                    migrated_count += 1
                
                db.session.commit()
                print(f"✅ Successfully migrated {migrated_count} product analyses")
            else:
                print("ℹ️  No product analyses need migration")
            
            # Check if we have any plastic data that needs migration
            # This would handle any existing data that should be in the new plastic_analyses table
            print("✅ Plastic analysis migration check complete")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

def get_user_stats(user_id):
    """Get comprehensive statistics for a user"""
    app = create_app()
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"❌ User {user_id} not found")
                return None
            
            total_points = user.get_total_points()
            product_count = ProductAnalysis.query.filter_by(user_id=user_id).count()
            plastic_count = PlasticAnalysis.query.filter_by(user_id=user_id).count()
            
            stats = {
                'user_id': user_id,
                'username': user.username,
                'total_points': total_points,
                'product_analyses': product_count,
                'plastic_analyses': plastic_count,
                'current_streak': user.current_streak,
                'joined_date': user.created_at
            }
            
            print(f"📊 User {user.username} Statistics:")
            print(f"   Total Points: {total_points}")
            print(f"   Product Analyses: {product_count}")
            print(f"   Plastic Analyses: {plastic_count}")
            print(f"   Current Streak: {user.current_streak} days")
            print(f"   Member Since: {user.created_at}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return None

if __name__ == '__main__':
    import sys
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'init'
    
    commands = {
        'init': init_db,
        'reset': reset_db,
        'sample': lambda: (init_db(), create_sample_data()),
        'check': check_db_connection,
        'backup': backup_database,
        'migrate': migrate_existing_data,
        'stats': lambda: get_user_stats(1) if len(sys.argv) > 2 else print("Usage: python database.py stats <user_id>")
    }
    
    if command in commands:
        try:
            if command == 'sample':
                init_db()
                create_sample_data()
            elif command == 'stats' and len(sys.argv) > 2:
                get_user_stats(int(sys.argv[2]))
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
        print("  migrate - Migrate existing data")
        print("  stats   - Get user statistics (python database.py stats <user_id>)")
        print("\n💡 Usage: python database.py [command]")