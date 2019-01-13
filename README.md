# liberty_monitor

## Monitor by restConnector

Build liberty image.

```shell
cd ./liberty-restconnector
docker build -t sotoiwa540/liberty-restconnector:1.0 .
docker push sotoiwa540/liberty-restconnector:1.0
```

Build monitor image.

```shell
cd ./monitor-restconnector
docker build -t sotoiwa540/monitor-restconnector:1.0 .
docker push sotoiwa540/monitor-restconnector:1.0
```

Create secret.

```shell
kubectl create secret generic jmx-secret --from-literal=JMX_USER=jmxadmin --from-literal=JMX_PASSWORD=password
```

Deploy liberty with sidecar.

```shell
kubectl apply -f liberty-deployment-restConnector.yaml
```

## Monitor by mpMetrics

Build liberty image.

```shell
cd ./liberty-mpmetrics
docker build -t sotoiwa540/liberty-mpmetrics:1.0 .
docker push sotoiwa540/liberty-mpmetrics:1.0
```

Build monitor image.

```shell
cd ./monitor-mpmetrics
docker build -t sotoiwa540/monitor-mpmetrics:1.0 .
docker push sotoiwa540/monitor-mpmetrics:1.0
```

Deploy liberty with sidecar.

```shell
kubectl apply -f liberty-mpmetrics-deployment.yaml.yaml
```
