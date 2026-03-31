import os
import logging
from datetime import datetime
import time
from typing import List, Dict
from dotenv import load_dotenv

from src.utils import get_conversations, change_conversation_state, get_conversation_state, crisp_url

# Load environment variables
load_dotenv()

# Configuration
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

def job_resolve_old_tickets(start_date: datetime = None, end_date: datetime = None, max_to_process: int = 0):
    """
    Resolve all tickets with last activity between start_date and end_date
    
    Args:
        start_date: Start date (inclusive). If None, defaults to Jan 1, 2025.
        end_date: End date (exclusive). If None, defaults to Jan 1, 2026.
        max_to_process: Maximum number of tickets to process (0 = no limit)
    
    Returns:
        Dict with execution statistics
    """
    # Default dates
    if start_date is None:
        start_date = datetime(2025, 1, 1)
    
    if end_date is None:
        end_date = datetime(2026, 1, 1)
    
    logging.info(f'Starting job_resolve_old_tickets from {start_date.isoformat()} to {end_date.isoformat()}, max_to_process={max_to_process}')
    
    # Get unresolved conversations within date range
    params = {
        "filter_not_resolved": 1,
        "order_date_updated": 1,
        "filter_date_start": start_date.isoformat(),
        "filter_date_end": end_date.isoformat()
    }
    
    all_conversations = get_conversations(params)
    logging.info(f'Total unresolved conversations in date range: {len(all_conversations)}')
    
    # Limit number of conversations if needed
    if max_to_process > 0 and len(all_conversations) > max_to_process:
        all_conversations = all_conversations[:max_to_process]
        logging.info(f'Limited to {max_to_process} conversations')
    
    # Stats counters
    total_processed = 0
    already_resolved = 0
    successfully_resolved = 0
    failed_resolutions = 0
    
    # Process conversations
    for conversation in all_conversations:
        conversation_id = conversation["session_id"]
        
        try:
            current_state = get_conversation_state(conversation_id)
            
            if current_state == "resolved":
                logging.info(f'Conversation already resolved: {crisp_url(conversation_id)}')
                already_resolved += 1
            else:
                if not DRY_RUN:
                    change_conversation_state(conversation_id, "resolved")
                    logging.info(f'Conversation resolved: {crisp_url(conversation_id)}')
                else:
                    logging.info(f'[DRY RUN] Would resolve: {crisp_url(conversation_id)}')
                
                successfully_resolved += 1
            
            total_processed += 1
            time.sleep(2)
            
        except Exception as e:
            logging.error(f'Error processing conversation {crisp_url(conversation_id)}: {str(e)}')
            failed_resolutions += 1
    
    # Final report
    logging.info("==== Old Conversations Resolution Report ====")
    logging.info(f"- Total processed: {total_processed}")
    logging.info(f"- Already resolved: {already_resolved}")
    logging.info(f"- Successfully resolved: {successfully_resolved}")
    logging.info(f"- Failed resolutions: {failed_resolutions}")
    if DRY_RUN:
        logging.info("NOTE: Executed in DRY RUN mode - no actual changes made!")
    logging.info("=============================================")
    
    return {
        "total_processed": total_processed,
        "already_resolved": already_resolved,
        "successfully_resolved": successfully_resolved,
        "failed_resolutions": failed_resolutions,
        "dry_run": DRY_RUN
    }

# Script execution entry point
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Default: process conversations from 2025
    job_resolve_old_tickets(
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 1, 1)
    )
