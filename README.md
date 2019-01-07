# liberty_monitor

## Usage

(optional) Build liberty image.

```shell
docker build -t sotoiwa540/liberty-sample:1.0 .
docker push sotoiwa540/liberty-sample:1.0
```

Build monitor image.

```shell
docker build -t sotoiwa540/liberty-monitor:1.0 .
docker push sotoiwa540/liberty-monitor:1.0
```

Deploy liberty container with sidecar container.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: liberty
spec:
  selector:
    matchLabels:
      app: liberty
  replicas: 1
  template:
    metadata:
      labels:
        app: liberty
    spec:
      containers:
      - name: liberty
        image: sotoiwa540/liberty-sample:1.0
        imagePullPolicy: Always
        ports:
        - containerPort: 9080
      - name: monitor
        image: sotoiwa540/liberty-monitor:1.0
        imagePullPolicy: Always
        command:
        - python
        - ./libertymon.py
        args:
        - --host
        - localhost
        - --port
        - "9443"
        - --interval
        - "60"
        - --timeout
        - "2"
        - --delay
        - "30"
        env:
        - name: JMX_USER
          valueFrom:
            secretKeyRef:
              name: jmx-secret
              key: JMX_USER
        - name: JMX_PASSWORD
          valueFrom:
            secretKeyRef:
              name: jmx-secret
              key: JMX_PASSWORD
```

Deploy liberty with sidecar.

```shell
kubectl apply -f liberty-deployment.yaml
```
