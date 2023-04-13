# matrix-rageshake-crisp

This script searches for conversations on the Crisp API that have the RAGESHAKE_EMAIL as a participant. It replaces this email by the "email :" field found in the rageshake description. 

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
pipenv install
python3 extract_email_from_rageshake_on_crisp.py
```

## deployment
Deactivate the web process in scalingo : https://doc.scalingo.com/platform/app/web-less-app

## Tests

```
python3 extract_email_from_rageshake_on_crisp.test.py
```


