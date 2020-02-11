# MQTT metrics exporter

```
export DOCKER_ID_USER="salekd"
docker login https://index.docker.io/v1/

docker build . -f ./Dockerfile -t mqtt-exporter --no-cache
docker tag mqtt-exporter $DOCKER_ID_USER/mqtt-exporter:1.2.0
docker push $DOCKER_ID_USER/mqtt-exporter:1.2.0
```

```
mkvirtualenv mqtt-exporter
workon mqtt-exporter

pip install --upgrade pip
pip install -r requirements.txt
```

```
curl http://localhost:8000/
```

http://localhost:8000/
