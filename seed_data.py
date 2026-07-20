"""
Seed script to create initial data for Leadex
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash, generate_token
from app.models import AdminUser, Campaign, LandingPage
import uuid


def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(AdminUser).filter(AdminUser.email == "admin@leadex.com").first()
        
        if not existing_admin:
            # Create default admin user
            admin_user = AdminUser(
                id=uuid.uuid4(),
                email="admin@leadex.com",
                password=get_password_hash("admin123"),  # Change this in production!
                role="super_admin"
            )
            db.add(admin_user)
            print("✅ Created admin user: admin@leadex.com / admin123")
        else:
            print("ℹ️  Admin user already exists")
        
        # Check if default campaign exists
        existing_campaign = db.query(Campaign).filter(Campaign.name == "Default Campaign").first()
        
        if not existing_campaign:
            # Create default campaign
            campaign = Campaign(
                id=uuid.uuid4(),
                name="Default Campaign",
                active=True,
                default_credit_cost=1.0,
                rules={}
            )
            db.add(campaign)
            db.flush()  # Get the campaign ID
            print("✅ Created default campaign")
            
            # Create default landing page
            landing_page = LandingPage(
                id=uuid.uuid4(),
                slug="default",
                name="Default Landing Page",
                captcha_type="reCAPTCHA_v3",
                campaign_id=campaign.id
            )
            db.add(landing_page)
            print("✅ Created default landing page: /landing/default")
        else:
            print("ℹ️  Default campaign already exists")
        
        # Commit all changes
        db.commit()
        print("\n🎉 Database seeded successfully!")
        print("\n📝 Login credentials:")
        print("   Email: admin@leadex.com")
        print("   Password: admin123")
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database...")
    seed_database()
