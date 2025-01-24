from fastapi import FastAPI, Response, Request
import json
import psycopg2
import os

HOST = os.getenv('POSTGRES_HOST', 'localhost')    #'pgq-db'
DATABASE = 'pgQueue'
PORT = 5432
USER = 'postgres'
PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')

app = FastAPI()

def connect_db():

    conn_string = f"postgres://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}"

    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()

    except Exception as e:
        conn = None
        cur = None

    return conn, cur 

@app.post('/message')
async def add_message(request: Request):
    try:
        body = await request.json()

    except:
        return Response(content='{"status":"Malformed json"}', media_type="application/json", status_code=400)
    
    if 'channel' not in body:
        return Response(content='{"status":"Field channel not found in json"}', media_type="application/json", status_code=400)
    
    if 'message' not in body:
        return Response(content='{"status":"Field message not found in json"}', media_type="application/json", status_code=400)

    channel = body['channel']
    message = body['message']
    
    if not isinstance(channel, str) or not isinstance(message, dict):
        return Response(content='{"status":"Check the field types. Channel must be str and Message must be a json"}', media_type="application/json", status_code=400)

    conn, cur = connect_db()

    if not conn:
        return Response(content='{"status":"Error connecting DB. Make sure POSTGRES_PASSWORD is set in the environment"}', media_type="application/json", status_code=503)

    INSERT_STR = "INSERT INTO message_queued (channel, message) VALUES (%s, %s) RETURNING id;"

    try:
        cur.execute(INSERT_STR, (channel, json.dumps(message)))
        rs = cur.fetchone()
        data = json.dumps({"status":"Message inserted!", "id": rs[0]})
    except:
        conn.rollback()
        conn.close()
        return Response(content='{"status":"Error inserting the message"}', media_type="application/json", status_code=503)
    
    conn.commit()
    conn.close()

    return Response(content=data, media_type="application/json", status_code=201)

@app.get('/queue/{channel}')
def get_message_queue(channel:str):
    conn, cur = connect_db()

    if not conn:
        return Response(content='{"status":"Error connecting DB. Try later"}', media_type="application/json", status_code=503)
    
    SELECT_STR = "SELECT * FROM get_message(%s)"

    try:
        cur.execute(SELECT_STR, (channel,))
        rs = cur.fetchone()

        if rs[0] == 0:
            data = None
            return_code = 204
            conn.rollback()
        else:
            data = json.dumps({"id": rs[0], "channel": rs[1], "message":rs[2], "created_at": rs[3]})
            return_code = 200
            conn.commit()

    except:
        data = '{"status":"Error querying DB"}'
        return_code = 503
        conn.rollback()

    conn.close()     
    return Response(content=data, media_type="application/json", status_code=return_code)

@app.get('/queues')
def get_queues():
    conn, cur = connect_db()

    if not conn:
        return Response(content='{"status":"Error connecting DB. Try later"}', media_type="application/json", status_code=503)
    
    SELECT_STR = """
        SELECT json_agg(row_to_json(mq))
          FROM (SELECT DISTINCT channel 
                  FROM message_queued
                 ORDER BY 1) mq;
    """

    try:
        cur.execute(SELECT_STR)
        rows = cur.fetchone()

        if len(rows) > 0:
            data = json.dumps(rows[0])
            return_code = 200

        else:
            data = None
            return_code = 204

    except Exception as e:
        print(e)
        data = '{"status":"Error querying DB"}'
        return_code = 503
        conn.rollback()

    conn.close()     
    return Response(content=data, media_type="application/json", status_code=return_code)

@app.get('/messages')
def get_messages(channel:str, offset:int = 0, limit:int = 25):
    conn, cur = connect_db()

    if not conn:
        return Response(content='{"status":"Error connecting DB. Try later"}', media_type="application/json", status_code=503)
    
    SELECT_STR = """
       SELECT json_agg(row_to_json(mq))
         FROM (SELECT id, channel, message, created_at::varchar
                 FROM message_queued 
                WHERE channel = (%s)
                ORDER BY id
               OFFSET (%s)
                LIMIT (%s)
    		  ) mq;
    """

    #Limit the pagination in 300 lines
    limit = min(limit, 300)

    try:
        cur.execute(SELECT_STR, (channel, offset, limit))
        rows = cur.fetchone()

        if len(rows) > 0:
            data = json.dumps(rows[0])
            return_code = 200

        else:
            data = None
            return_code = 204


    except:
        data = '{"status":"Error querying DB"}'
        return_code = 503
        conn.rollback()

    conn.close()     
    return Response(content=data, media_type="application/json", status_code=return_code)

@app.post("/test")
async def input_request(request: Request):
    # try:
    #     body = json.loads(await request.body())

    # except:
    #     pass


    return await request.body()

@app.get("/test")
async def get_test():
    # try:
    #     body = json.loads(await request.body())

    # except:
    #     pass


    return Response(content='Hello world', media_type="application/text")