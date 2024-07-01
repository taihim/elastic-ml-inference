from prometheus_client import Summary

GET_REQUEST_LATENCY = Summary('get_latency', 'Latency of the get request')
PREDICT_REQUEST_LATENCY = Summary('predict_latency', 'Latency of the prediction request')
