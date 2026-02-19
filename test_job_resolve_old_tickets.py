import logging
from datetime import datetime
from src.job_resolve_old_tickets import job_resolve_old_tickets
from src.utils import setLogLevel

if __name__ == "__main__":
    setLogLevel('DEBUG')
    
    # Run with default dates (year 2025)
    result = job_resolve_old_tickets(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2025, 12, 31)
    )
    
    print("\n=== Execution Summary ===")
    print(f"Total processed: {result['total_processed']}")
    print(f"Already resolved: {result['already_resolved']}")
    print(f"Successfully resolved: {result['successfully_resolved']}")
    print(f"Failed resolutions: {result['failed_resolutions']}")
    
    if result['dry_run']:
        print("\nExecuted in DRY RUN mode - no actual changes made.")
        print("To apply changes, set DRY_RUN=false in your .env file")
