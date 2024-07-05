from typing import Final

PROMETHEUS_ENDPOINT: Final[str] = 'http://192.168.49.2:32624'
AVERAGE_PREDICTION_LATENCY_QUERY: Final[
    str] = 'sum(avg_over_time(predict_latency_sum[1m])) / sum(avg_over_time(predict_latency_count[1m]))'
SCALING_INTERVAL: Final[int] = 15
DESIRED_PREDICTION_LATENCY: Final[float] = 0.25  # seconds
MIN_REPLICAS: Final[int] = 1
MAX_REPLICAS: Final[int] = 10
