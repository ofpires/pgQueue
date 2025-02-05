import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
    scenarios: {
        open_model: {
            executor: 'constant-arrival-rate',
            rate: 100,
            timeUnit: '1s',
            duration: '3m', 
            preAllocatedVUs: 1000, 
        },
    },
    thresholds: {
        http_req_failed: ['rate<0.01'], 
        http_req_duration: ['p(95)<500'], 
    },
};

export default function () {
  const endpoints = [
    { method: 'GET', url: 'http://localhost:8000/queue/two' },
    { method: 'POST', url: 'http://localhost:8000/message', 
      body: JSON.stringify({ channel: 'two', message: { seq: 7 } }),
      params: { headers: { 'Content-Type': 'application/json' } }
    },
  ];
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

  let response;
  if (endpoint.method === 'GET') {
    response = http.get(endpoint.url);
  } else if (endpoint.method === 'POST') {
    response = http.post(endpoint.url, endpoint.body, endpoint.params);
  }


  check(response, {
    'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
  });

  sleep(0.5);
}
