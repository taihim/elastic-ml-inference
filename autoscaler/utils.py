from autoscaler.constants import MIN_REPLICAS, MAX_REPLICAS


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def calculate_replicas(metric_value: float, desired_value: float, current_replicas: int) -> int:
    return clamp(int(current_replicas * int(metric_value / desired_value)), MIN_REPLICAS, MAX_REPLICAS)
