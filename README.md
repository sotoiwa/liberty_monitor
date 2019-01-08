# liberty_monitor

## Monitor by restConnector

Build liberty image.

```shell
cd ./liberty-restConnector
docker build -t sotoiwa540/liberty-restConnector:1.0 .
docker push sotoiwa540/liberty-restConnector:1.0
```

Build monitor image.

```shell
cd ./monitor-restConnector
docker build -t sotoiwa540/monitor-restConnector:1.0 .
docker push sotoiwa540/monitor-restConnector:1.0
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
cd ./liberty-mpMetrics
docker build -t sotoiwa540/liberty-mpMetrics:1.0 .
docker push sotoiwa540/liberty-mpMetrics:1.0
```

Build monitor image.

```shell
cd ./monitor-mpMetrics
docker build -t sotoiwa540/monitor-mpMetrics:1.0 .
docker push sotoiwa540/monitor-mpMetrics:1.0
```

Deploy liberty with sidecar.

```shell
kubectl apply -f liberty-deployment-mpMetrics.yaml
```
