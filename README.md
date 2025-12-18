# matrix-rageshake-crisp

This script searches for conversations on the Crisp API that have the RAGESHAKE_EMAIL as a participant. It replaces this email by the "email :" field found in the rageshake description. 

It interacts with crisp by a Plugin published here : https://marketplace.crisp.chat/plugins/
If dev tokens reach max quota (429 Client Error: Too Many Requests), they can be reset here : https://marketplace.crisp.chat/plugins/plugin/50c492e5-7175-45d0-a449-913aa8bc6cfd/tokens/

## Logs

https://dashboard.scalingo.com/apps/osc-secnum-fr1/tchap-rageshake-crisp/logs

## Setup

The following environment variables must be set before running the script:

- `CRISP_IDENTIFIER`: Your Crisp API identifier.
- `CRISP_KEY`: Your Crisp API key.
- `CRISP_WEBSITE_ID`: The ID of the Crisp website to search for conversations.
- `RAGESHAKE_EMAIL`: The email address to search for in the conversations' metadata.
- `DRY_RUN`: Set to `True` if you don't want any change to append.
- `SCHEDULE_CRISP_INVALID_RAGESHAKE`: cron schedule for the job crips invalid rageshake (by default 60 seconds)
- `SCHEDULE_JOB_SLEEPY_CONVERSATION_IN_HOURS`: cron schedule for the job job_process_sleepy_conversations (by default 24 hours)
- `SCHEDULE_JOB_EXPORT_SEGMENTS_IN_DAYS`: CRON schedule for the job job_export_crips_conversation_segments_s3 in days  (by default 1 day)
- `JOB_EXPORT_SEGMENTS_HISTORY_IN_DAYS`: configure how days of history to export in job job_export_crips_conversation_segments_s3 (default 10 days)
- `SCHEDULE_PROCESS_ALL_MESSAGES_IN_SECONDS`: CRON schedule for the job job_process_all_recent_conversations in seconds (by default 120 seconds)
- `LOGLEVEL`: Set LogLevel (WARNING, INFO, DEBUG..), default to DEBUG

For the statistics export to the S3 OVH bucket
- `S3_ACCESS_KEY_ID` : access key to the export bucket
- `S3_SECRET_ACCESS_KEY` : secret access key to the export bucket
- `S3_BUCKET_NAME` : bucket name of the export bucket

Crisp plugin is defined here : https://marketplace.crisp.chat/plugins/plugin/50c492e5-7175-45d0-a449-913aa8bc6cfd/tokens/


## Usage

To run the script, simply run the following command:

Use this version of boto3 with ovh else we get a `parsed_response, operation_name)
botocore.exceptions.ClientError: An error occurred (InvalidArgument) when calling the PutObject operation: x-amz-content-sha256 must be UNSIGNED-PAYLOAD, or a valid sha256 value.`

```
boto3= "1.33.11"
```

```
pipenv install
pipenv run python3 ./test_int_job_export_crisp_conversation_segments_s3.py
```

## deployment
Deactivate the web process in scalingo : https://doc.scalingo.com/platform/app/web-less-app

## Tests

```
python3 -m unittest test_int_job_process_all_incoming_messages.py -v
```

