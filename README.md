# matrix-rageshake-crisp

This script searches for conversations on the Crisp API with the state "pending" and metadata "email" set to a specific value. For each conversation matching these criteria, it parses the first message to find an email address and/or a user ID, and converts any user IDs found to email addresses. The resulting email address is then set as the conversation's email.

## Setup

The following environment variables must be set before running the script:

- `CRISP_IDENTIFIER`: Your Crisp API identifier.
- `CRISP_KEY`: Your Crisp API key.
- `CRISP_WEBSITE_ID`: The ID of the Crisp website to search for conversations.
- `RAGESHAKE_EMAIL`: The email address to search for in the conversations' metadata.
- `DRY_RUN`: Set to `True` if you don't want any change to append.
- `SCHEDULE_CRISP_INVALID_RAGESHAKE`: cron schedule for the job crips invalid rageshake (by default 60 seconds)

## Usage

To run the script, simply run the following command:
```
python3 -m venv matrix-rageshake-crisp
source matrix-rageshake-crisp/bin/activate
pip install -r requirements.txt
python3 extract_email_from_rageshake_on_crisp.py
```

## Tests

```
pip install unittest
python extract_email_from_rageshake_on_crisp.test.py
```


