#!/usr/bin/env python3
"""
Database cleanup script - removes all test/mock data
Keeps only the admin user
"""
import sys
import os

# Add project root to path
sys.path.insert(0, '/root/leadex-project')

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def cleanup_database():
    db = SessionLocal()

    try:
        print("Starting database cleanup...")
        print("=" * 60)

        # Count records before
        print("\nBefore cleanup:")
        result = db.execute(text("SELECT COUNT(*) FROM clients")).scalar()
        print(f"  Clients: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM assets")).scalar()
        print(f"  Assets (Leads): {result}")

        result = db.execute(text("SELECT COUNT(*) FROM deliveries")).scalar()
        print(f"  Deliveries: {result}")

        # Delete in correct order (respecting foreign keys)
        print("\nDeleting records...")

        # Delete child tables first
        result = db.execute(text("DELETE FROM deliveries"))
        print(f"  ✓ Deleted {result.rowcount} deliveries")

        result = db.execute(text("DELETE FROM stored_leads"))
        print(f"  ✓ Deleted {result.rowcount} stored leads")

        result = db.execute(text("DELETE FROM lead_notes"))
        print(f"  ✓ Deleted {result.rowcount} lead notes")

        result = db.execute(text("DELETE FROM lead_scores"))
        print(f"  ✓ Deleted {result.rowcount} lead scores")

        result = db.execute(text("DELETE FROM lead_tags"))
        print(f"  ✓ Deleted {result.rowcount} lead tags")

        result = db.execute(text("DELETE FROM asset_tags"))
        print(f"  ✓ Deleted {result.rowcount} asset tags")

        result = db.execute(text("DELETE FROM custom_field_values"))
        print(f"  ✓ Deleted {result.rowcount} custom field values")

        result = db.execute(text("DELETE FROM webhook_logs"))
        print(f"  ✓ Deleted {result.rowcount} webhook logs")

        result = db.execute(text("DELETE FROM dlq"))
        print(f"  ✓ Deleted {result.rowcount} DLQ entries")

        result = db.execute(text("DELETE FROM batch_queue"))
        print(f"  ✓ Deleted {result.rowcount} batch queue entries")

        # Delete assets (leads)
        result = db.execute(text("DELETE FROM assets"))
        print(f"  ✓ Deleted {result.rowcount} assets (leads)")

        # Delete clients
        result = db.execute(text("DELETE FROM clients"))
        print(f"  ✓ Deleted {result.rowcount} clients")

        # Delete notifications
        result = db.execute(text("DELETE FROM notifications"))
        print(f"  ✓ Deleted {result.rowcount} notifications")

        # Delete reports data
        result = db.execute(text("DELETE FROM report_exports"))
        print(f"  ✓ Deleted {result.rowcount} report exports")

        result = db.execute(text("DELETE FROM report_schedules"))
        print(f"  ✓ Deleted {result.rowcount} report schedules")

        result = db.execute(text("DELETE FROM reports"))
        print(f"  ✓ Deleted {result.rowcount} reports")

        # Delete landing pages (references campaigns)
        result = db.execute(text("DELETE FROM landing_pages"))
        print(f"  ✓ Deleted {result.rowcount} landing pages")

        # Delete campaigns and imports
        result = db.execute(text("DELETE FROM campaigns"))
        print(f"  ✓ Deleted {result.rowcount} campaigns")

        result = db.execute(text("DELETE FROM import_history"))
        print(f"  ✓ Deleted {result.rowcount} import history entries")

        # Commit all changes
        db.commit()

        print("\n" + "=" * 60)
        print("✓ Database cleanup completed successfully!")
        print("=" * 60)

        # Count records after
        print("\nAfter cleanup:")
        result = db.execute(text("SELECT COUNT(*) FROM clients")).scalar()
        print(f"  Clients: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM assets")).scalar()
        print(f"  Assets (Leads): {result}")

        result = db.execute(text("SELECT COUNT(*) FROM deliveries")).scalar()
        print(f"  Deliveries: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM admin_users")).scalar()
        print(f"  Admin Users: {result} (preserved)")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error during cleanup: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_database()
