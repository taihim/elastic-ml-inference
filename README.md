# Elastic ML Inference

## To get started

### Install dependencies using pdm

```
pdm install
```

### Install minikube

```
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
```

```
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

### Install kubectl

```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

```
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Install helm

```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
```

```
chmod 700 get_helm.sh
```

```
./get_helm.sh
```

### Start the minikube cluster

```
minikube start
```

### Enable metrics server to allow usage of HPA with both default and custom metrics

```
minikube addons enable metrics-server
```

### Deploy the classification app to minikube according to settings in app-deployment.yaml

```
kubectl apply -f manifests/app-deployment.yaml
```

### Enable the ingress addon in minikube to allow public access to the cluster via an nginx ingress controller

```
minikube addons enable ingress
```

### Expose the web app deployment via a service of type NodePort

```
kubectl expose deployment classifier-api --type=NodePort --port=8000
```

### Create an ingress object that routes traffic to the service via nginx

```
kubectl apply -f manifests/app-ingress.yaml
```

### Get a public ip to access the service

```
minikube service classifier-api --url
```

### (Optional) Add an entry into your /etc/hosts file

Using the IP from the previous step and the value of the 'host' field in
the manifests/app-ingress.yaml file, add an entry in your /etc/hosts file to allow
access to the cluster via the url specified as 'host'. You can choose any value for host
by modifying the value in the manifests/app-ingress.yaml file.

### (Optional) Enable HPA for autoscaling

```
kubectl apply -f manifests/app-hpa-default.yaml
```

### Install prometheus to collect metrics

```
helm install prometheus prometheus-community/prometheus
```

### Expose prometheus service via Nodeport

```
kubectl expose service prometheus-server --type=NodePort --target-port=9090 --name=prometheus-server-np
```

### Edit the prometheus configmap (prometheus-server by default)

```
kubectl edit configmap prometheus-server
```

Note: this command opens vim by default. You can pass in your preferred editor via the
EDITOR prefix e.g.
EDITOR=nano kubectl edit configmap prometheus-server (opens the configmap in the nano editor instead)

### Add the following target to the scrape config to allow prometheus to get logs from our classification app

```
scrape_configs:
- job_name: classifier-api
  scrape_interval: 900ms
  kubernetes_sd_configs:
    - role: endpoints
      relabel_configs:
    - source_labels: [__meta_kubernetes_namespace]
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_endpoint_address_target_name]
      target_label: kubernetes_pod_name
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: classifier-api
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      target_label: __address__
      regex: (.+)(?::\d+);(\d+)
      replacement: $1:$2
```

Restart prometheus-server to apply the new configs:

```
kubectl rollout restart deployment prometheus-server
```

### (optional) Install prometheus adapter to send prometheus logs to Kubernetes

This allows us to use our metrics from prometheus with the HPA from k8s.

Specify the prometheus url and port. the ip is the CLUSTER-IP of the prometheus-server service (don't need nodeport
since adapter is also in the cluster)

Get the cluster-ip using this command:

```
kubectl get service prometheus-server
```

Then paste it into this command and run it:

```
helm install --set prometheus.url=http://CLUSTER-IP --set prometheus.port=80 prometheus-adapter
prometheus-community/prometheus-adapter
```

### Apply adapter configs

```
kubectl apply -f manifests/prom-adapter.yaml
```

Restart to apply the new config

```
kubectl rollout restart deployment prometheus-adapter
```

### Create an api service to make our custom metrics available via the k8s api

```
kubectl create -f api-service.yaml
```

### We can now list our available custom metrics

```
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta2"
```

To get a specific metric:

```
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta2/namespaces/default/pods/*/predict_latency_average"
```

### We can use the default HPA with any custom metrics from prometheus now

There is a sample config in the manifests folder that can be used to demonstrate this:

```
kubectl apply -f manifests/app-hpa-custom.yaml
```

### Run a custom autoscaler

There is a custom implementation of an autoscaler in the autoscaler directory.

First, if you are running any instance of HPA, delete it using

```
kubectl delete hpa YOUR-HPA-NAME
```

Then just run app.py in the autoscaler directory:

```
python autoscaler/app.py
```