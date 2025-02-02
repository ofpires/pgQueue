# pgQueue App

## Implements a message broker (FIFO) using Postgresql

**Involved technologies:**
1. **Postgres / PL/pgSQL** <img src="https://skillicons.dev/icons?i=postgres" alt="icon" width="30" height="30"/>
2. **Python - FastAPI** <img src="https://skillicons.dev/icons?i=py" alt="icon" width="30" height="30"/>
3. **Docker** <img src="https://skillicons.dev/icons?i=docker" alt="icon" width="30" height="30"/>

After running ***docker compose up -d*** in the project root directory, you can run the ***python support/load.py*** script to insert messages into Postgresql. Adjust the Postgres connection string variables before running.

---

## Endpoints

### **POST** `/message`
Inserts a new message at the end of the queue. The request body must contain a JSON with two keys, `channel` (str) and `message` (json).

**Example:**
```json
{
    "channel": "abcd",
    "message": { "seq": 7 }
}
```

**Response:**  
Returns a JSON containing the operation status and the id of the message. If the insert operation fails, the HTTP status code is set to 503.
```json
{"status": "Message inserted!", "id": 15472}
```

---

### **GET** `/queue/{channel}`
Consumes the first (oldest) available message from the specified channel.

**Example:**  
`GET http://localhost:8000/queue/two`

**Response:**  
Returns a JSON with the oldest message of the informed channel. If there are no messages, the HTTP status code is set to 204.
```json
{
    "id": 10000,
    "channel": "two",
    "message": { "seq": 1 },
    "created_at": "2025-01-24 21:33:17.988107"
}
```

---

### **GET** `/messages?channel=<channel>&offset=<offset>&limit=<limit>`
Returns a JSON array with a list of `limit` messages (without consuming them).  
*Notes:*
- The query parameter `channel` is mandatory.
- `offset` defaults to 0.
- `limit` defaults to 25, with a maximum value of 300.
- If there are no messages for the specified channel, the HTTP status code is set to 204.

**Example:**  
`GET http://localhost:8000/messages?channel=one&offset=0&limit=5`

**Response:**
```json
[
    {
        "id": 29,
        "channel": "one",
        "message": { "seq": 29 },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 30,
        "channel": "one",
        "message": { "seq": 30 },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 31,
        "channel": "one",
        "message": { "seq": 31 },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 32,
        "channel": "one",
        "message": { "seq": 32 },
        "created_at": "2025-01-24 18:56:59.83374"
    },
    {
        "id": 33,
        "channel": "one",
        "message": { "seq": 33 },
        "created_at": "2025-01-24 18:56:59.83374"
    }
]
```

---

### **GET** `/channels`
Returns a JSON array containing a list of existing channels in queued messages. If there are no messages, the HTTP status code is set to 204.

**Example Response:**
```json
[
    { "channel": "abcd" },
    { "channel": "one" },
    { "channel": "two" }
]
```

---

## Instrumentation & Monitoring

This application is instrumented with [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator). The instrumentator automatically collects and exposes various metrics about HTTP requests and system performance. These metrics are available at the `/metrics` endpoint.

**Key Metrics Collected:**
- `http_requests_total`: Total number of HTTP requests received.
- `http_request_duration_seconds`: Histogram for the duration of HTTP requests.
- Additional process and Python-related metrics (e.g., garbage collection, memory usage).

These metrics can be scraped by Prometheus and visualized in Grafana for monitoring and performance analysis.

---

## Load Testing with k6

A load test script (`load-test.js`) is provided in the `performance` folder to simulate load on the following API endpoints:

- **GET** `http://localhost:8000/queue/two`
- **POST** `http://localhost:8000/message`

**How to Run the Load Test:**

1. **Install k6:**  
   Follow the installation instructions available at: [Install k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)

2. **Execute the Test:**  
   From the project root, run:
   ```bash
   k6 run performance/load-test.js
   ```
   This will generate load on the specified endpoints, allowing you to monitor real-time metrics (such as the request rate and average response time) via Prometheus and Grafana.

---

## Monitoring Specific Endpoints in Grafana

To monitor only the endpoints `/queue/two` and `/message`, you can use the following queries in your Grafana dashboards:

- **Total Requests (filtered):**
  ```promql
  http_requests_total{status="2xx", handler=~"/queue/two|/message"}
  ```
- **Average Response Time (filtered):**
  ```promql
  rate(http_request_duration_seconds_sum{handler=~"/queue/two|/message"}[1m])
    /
  rate(http_request_duration_seconds_count{handler=~"/queue/two|/message"}[1m])
  ```

For real-time monitoring (i.e., to see the current load instead of a cumulative counter), consider using functions such as `irate()` or `increase()`. For example, to view the current request rate:
```promql
irate(http_requests_total{status="2xx", handler=~"/queue/two|/message"}[1m])
```

---

## Docker Compose

Ensure you run `docker compose up -d` to start all services (Postgres, API, Prometheus, and Grafana).  
- **Prometheus** is available at: [http://localhost:9090](http://localhost:9090)
- **Grafana** is available at: [http://localhost:3000](http://localhost:3000)  
  In Grafana, configure the Prometheus data source with the URL `http://prometheus:9090` (within the Docker network).

---

Happy monitoring and load testing!
