import os
import json
import uuid
import datetime

import azure.functions as func
import logging
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
IOTHUB_CONNECTION_STRING_NAME = os.getenv("IOTHUB_CONNECTION_STRING_NAME")

app = func.FunctionApp()
con = psycopg2.connect(DATABASE_URL)


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name=EVENT_HUB_NAME,  # FIXME: Change to your own iothub event_hub_name
    connection=IOTHUB_CONNECTION_STRING_NAME,  # Remember to add the IOTHUB_CONNECTION_STRING environment variable in your Function App
)
def eventhub_trigger1(azeventhub: func.EventHubEvent):
    logging.info(
        "Python EventHub trigger processed an event: %s",
        azeventhub.get_body().decode("utf-8"),
    )

    msg = json.loads(azeventhub.get_body().decode("utf-8"))
    msg["id"] = str(uuid.uuid4())
    logging.info(f"Message: {msg.get('device_id')}")

    with con:
        with con.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS temperature (id UUID PRIMARY KEY, device_id TEXT, temperature FLOAT, created_at TIMESTAMP)""")
            cur.execute(
                """INSERT INTO temperature (id, device_id, temperature, created_at) VALUES (%s, %s, %s, %s)""",
                (
                    msg["id"],
                    msg["device_id"],
                    msg["temperature"],
                    datetime.datetime.now(),
                ),
            )
