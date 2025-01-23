# pgQueue

## Implements a kafka-like message queue (FIFO) using Postgresql

**Involved technologies:**
1. Postgres / PL/pgSQL
2. Python - FastAPI
3. Docker 
   
After running ***docker compose up -d*** in the project root directory, you can run ***python support/load.py*** script to insert messages in the Postgresql. Adjust the Postgres connection string variables before running.







