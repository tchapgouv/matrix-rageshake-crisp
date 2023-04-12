import schedule
import time
from extract_email import job_process_invalid_rageshake
from ConversationIdStorage import ConversationIdStorage


#stores processed conversations id
processConversationIds = ConversationIdStorage()

def start_cron():

    schedule.every(60).seconds.do(job_process_invalid_rageshake, processConversationIds=processConversationIds)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_cron()