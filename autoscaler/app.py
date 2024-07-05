import asyncio
import time

import httpx
from kr8s.objects import Deployment

from autoscaler.constants import PROMETHEUS_ENDPOINT, AVERAGE_PREDICTION_LATENCY_QUERY, SCALING_INTERVAL, \
    DESIRED_PREDICTION_LATENCY
from autoscaler.utils import calculate_replicas


async def scaling_loop():
    last_scale_time = time.time()
    while True:
        try:
            print("Autoscaler running at " + time.strftime('%Y-%m-%d %H:%M:%S'))

            query_response = httpx.get(PROMETHEUS_ENDPOINT + '/api/v1/query', params={
                'query': AVERAGE_PREDICTION_LATENCY_QUERY})

            deploy = await Deployment.get("classifier-api", namespace="default")
            current_replicas = len(deploy.pods())
            target_replicas = calculate_replicas(float(query_response.json()['data']['result'][0]['value'][1]),
                                                 DESIRED_PREDICTION_LATENCY,
                                                 current_replicas)
            print(f"Current replicas: {current_replicas}, Target replicas: {target_replicas}")

            if target_replicas == current_replicas:
                print("No scaling required.")
                time.sleep(SCALING_INTERVAL)
                continue

            if time.time() - last_scale_time >= SCALING_INTERVAL * 1.5:
                print(f"Scaling to {target_replicas} replicas")
                deploy.scale(target_replicas)
                last_scale_time = time.time()
            else:
                print("Too little time has passed since last scaling event, skipping scaling.")
                time.sleep(SCALING_INTERVAL)

        except Exception as e:
            print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(scaling_loop())
