# pgQueue App

## Implements a message broker (FIFO) using Postgresql

**Involved technologies:**
1. Postgres / PL/pgSQL <img src="https://skillicons.dev/icons?i=postgres" alt="icon" width="30" height="30"/>
2. Python - FastAPI <img src="https://skillicons.dev/icons?i=py" alt="icon" width="30" height="30"/>
3. Docker <img src="https://skillicons.dev/icons?i=docker" alt="icon" width="30" height="30"/>
   
After running ***docker compose up -d*** in the project root directory, you can run ***python support/load.py*** script to insert messages in the Postgresql. Adjust the Postgres connection string variables before running.

## Endpoints

***/message (POST)***

Inserts a new message at the end of the queue. Body must contain a json with two keys, channel (str) and message (json). 
Ex.:
*{
    "channel": "abcd",
    "message": { "seq": 7}
}*

Returns a join containing the operation status and the id of the message. If the insert operation goes wrong, HTTP_STATUS_CODE is set to 503.

*{"status":"Message inserted!", "id": 15472}*

***/queue/{channel:str} (GET)***

Consumes the first (oldest) available message.

Ex.: *localhost:8000/queue/two*

Returns a json containing the oldest message of the informed channel. If there isn't anyone, HTTP_STATUS_CODE is set to 204. 

*{
    "id": 10000,
    "channel": "two",
    "message": {
        "seq": 1
    },
    "created_at": "2025-01-24 21:33:17.988107"
}*

***/messages?channel=<channel>&offset=<offset>&limit=<limit> (GET)***

Returns a json array containing a list of *limit* messages, without consuming them. Useful to use in a front end tool built to monitor the queued messages. *Channel* query param is mandatory while *offset* defaults to 0 and *limit*  defaults to 25, with a maximum value of 300. If there is no message in the specified channel, HTTP_STATUS_CODE is set to 204.

Ex.: *localhost:8000/messages?channel=one&offset=0&limit=5*

Returns: *[
    {
        "id": 29,
        "channel": "one",
        "message": {
            "seq": 29
        },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 30,
        "channel": "one",
        "message": {
            "seq": 30
        },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 31,
        "channel": "one",
        "message": {
            "seq": 31
        },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 32,
        "channel": "one",
        "message": {
            "seq": 32
        },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 33,
        "channel": "one",
        "message": {
            "seq": 33
        },
        "created_at": "2025-01-24 18:56:59.83374"
    }
]*

***/channels (GET)***

Returns a json array containing a list with existing channels in queued messages. If there isn't anyone, HTTP_STATUS_CODE is set to 204.

Ex.: *[
    {
        "channel": "abcd"
    },
    {
        "channel": "one"
    },
    {
        "channel": "two"
    }
]*










