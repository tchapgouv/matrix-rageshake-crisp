# matrix-rageshake-crisp

This script searches for conversations on the Crisp API that have the RAGESHAKE_EMAIL as a participant. It replaces this email by the "email :" field found in the rageshake description. 

It interacts with crisp by a Plugin published here : https://marketplace.crisp.chat/plugins/
If dev tokens reach max quota (429 Client Error: Too Many Requests), they can be reset here : https://marketplace.crisp.chat/plugins/plugin/50c492e5-7175-45d0-a449-913aa8bc6cfd/tokens/

## Setup

The following environment variables must be set before running the script:

- `CRISP_IDENTIFIER`: Your Crisp API identifier.
- `CRISP_KEY`: Your Crisp API key.
- `CRISP_WEBSITE_ID`: The ID of the Crisp website to search for conversations.
- `RAGESHAKE_EMAIL`: The email address to search for in the conversations' metadata.
- `DRY_RUN`: Set to `True` if you don't want any change to append.
- `SCHEDULE_CRISP_INVALID_RAGESHAKE`: cron schedule for the job crips invalid rageshake (by default 60 seconds)
- `SCHEDULE_JOB_SLEEPY_CONVERSATION_IN_HOURS`: cron schedule for the job job_process_sleepy_conversations (by default 24 hours)

For the statistics export to the S3 OVH bucket
- `S3_ACCESS_KEY_ID` : access key to the export bucket
- `S3_SECRET_ACCESS_KEY` : secret access key to the export bucket
- `S3_BUCKET_NAME` : bucket name of the export bucket

Crisp plugin is defined here : https://marketplace.crisp.chat/plugins/plugin/50c492e5-7175-45d0-a449-913aa8bc6cfd/tokens/


## Usage

To run the script, simply run the following command:
```
pipenv install
python3 extract_email_from_rageshake_on_crisp.py
```

## deployment
Deactivate the web process in scalingo : https://doc.scalingo.com/platform/app/web-less-app

## Tests

```
python3 extract_email_from_rageshake_on_crisp.test.py
```


