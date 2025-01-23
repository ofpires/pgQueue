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

    except:
        conn = None
        cur = None

    return conn, cur 

# @app.post('/message')
# def add_message(channel: str, message: str):
#     conn, cur = connect_db()

#     if not conn:
#         return Response(content={"status":"Error connecting DB. Try later"}, media_type="application/json", status_code=503)

#     INSERT_STR = "INSERT INTO message_queued (channel, message) VALUES (%s, %s) RETURNING id;"

#     try:
#         cur.execute(INSERT_STR, (channel, message))
#         rs = cur.fetchone()
#         data = json.dumps({"status":"Message inserted!", "id": rs[0]})
#     except:
#         conn.rollback()
#         conn.close()
#         return Response(content='{"status":"Error inserting the message"}', media_type="application/json", status_code=503)
    
#     conn.commit()
#     conn.close()

#     return Response(content=data, media_type="application/json", status_code=201)

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

@app.get('/message/{channel}')
def get_message(channel:str):
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

#@app.post('/test')
# async def update_item(payload: Any = Body(None)):
#     return payload

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