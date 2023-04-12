import schedule
import time
import os

from extract_email import job_process_invalid_rageshake
from ConversationIdStorage import ConversationIdStorage

#this script is started by the container
#https://doc.scalingo.com/platform/app/task-scheduling/custom-clock-processes

#stores processed conversations id
processConversationIds = ConversationIdStorage()

def start_cron():
    cron_shedule = os.environ["SCHEDULE_CRISP_INVALID_RAGESHAKE"]
    schedule.every(cron_shedule).seconds.do(job_process_invalid_rageshake, processConversationIds=processConversationIds)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_cron()