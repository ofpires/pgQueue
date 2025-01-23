import psycopg2
import json

HOST = 'localhost'
DATABASE = 'pgQueue'
PORT = 5432
USER = 'postgres'
PASS = 'postgres'

INSERT_STR = "INSERT INTO message_queued (channel, message) VALUES (%s, %s);"
CHANNEL = 'one'

conn_string = f"postgres://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}"

conn = psycopg2.connect(conn_string)
cur = conn.cursor()
ins_count = 0

for index in range(1, 10000):
    message = {"seq": index}
    cur.execute(INSERT_STR, (CHANNEL, json.dumps(message)))
    ins_count += 1

    if ins_count >= 1000:
        conn.commit()
        ins_count = 0

conn.commit()
conn.close()


