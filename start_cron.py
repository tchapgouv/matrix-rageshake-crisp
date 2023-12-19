import schedule
import time
import os
import logging

from src.job_process_invalid_rageshake import job_process_invalid_rageshake
from src.job_process_sleepy_conversations import job_process_sleepy_conversations
from src.job_export_crips_conversation_segments_s3 import job_export_crips_conversation_segments_s3
from src.job_process_all_incoming_messages import job_process_all_incoming_messages
from src.utils import setLogLevel
from src.ConversationIdStorage import ConversationIdStorage

#this script is started by the container
#https://doc.scalingo.com/platform/app/task-scheduling/custom-clock-processes

#stores processed conversations id
processConversationIds = ConversationIdStorage()



def start_cron():

    setLogLevel()
    #cron_shedule:str = os.environ["SCHEDULE_CRISP_INVALID_RAGESHAKE"]
    cron_process_all_incoming_messages:str = os.environ["SCHEDULE_PROCESS_ALL_MESSAGES_IN_SECONDS"]
    cron_sleepy_conversation:str = os.environ["SCHEDULE_JOB_SLEEPY_CONVERSATION_IN_HOURS"]
    cron_export_segments_to_stat:str = os.environ["SCHEDULE_JOB_EXPORT_SEGMENTS_IN_DAYS"]
    logging.info(f'Configure cron_process_all_incoming_messages with : {cron_process_all_incoming_messages}')
    logging.info(f'Configure cron_sleepy_conversation with : {cron_sleepy_conversation}')
    logging.info(f'Configure cron_export_segments_to_stat with : {cron_export_segments_to_stat}')

    # every 'cron_shedule' seconds process new conversations
    #schedule.every(int(cron_shedule)).seconds.do(job_process_invalid_rageshake, processConversationIds=processConversationIds)
    schedule.every(int(cron_process_all_incoming_messages)).seconds.do(job_process_all_incoming_messages, 10, processConversationIds=processConversationIds)

    # process 10 sleepy conversations every 'cron_sleepy_conversation' hours
    schedule.every(int(cron_sleepy_conversation)).hours.do(job_process_sleepy_conversations, 10)

    # every 'cron_export_segments_to_stat' days export the conversations from last 10 days
    schedule.every(int(cron_export_segments_to_stat)).days.do(job_export_crips_conversation_segments_s3, 10)


    while True:
        schedule.run_pending()
        time.sleep(30)# the cron will check every 30 seconds if there is a job to run


if __name__ == "__main__":
    start_cron()