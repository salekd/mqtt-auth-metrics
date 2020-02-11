# Deployment

```
# Cluster domain name
export CLUSTER=
# Admin password
export PASSWORD=

# Install mustache templates.
# https://mustache.github.io/
#curl -sSL https://git.io/get-mo -o mo
#chmod +x mo
#mv mo /usr/local/bin/

mo mosquitto-cm.yaml_template > mosquitto-cm.yaml
mo mqtt-exporter-cm.yaml_template > mqtt-exporter-cm.yaml
mo postgresql-values.yaml_template > postgresql-values.yaml
```

```
kubectl apply -f tcp-configmap.yaml

./install-postgresql.sh
./boostrap-postgresql.sh

kubectl apply -f mosquitto-cm.yaml
kubectl apply -f mosquitto-dep.yaml
kubectl apply -f mosquitto-svc.yaml
kubectl apply -f mqtt-exporter-cm.yaml
kubectl apply -f mqtt-exporter-svc.yaml
```

```
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth

PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "\dt"
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "\du"

PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "SELECT * FROM account"
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "SELECT * FROM acls"
```

```
mosquitto_sub -t public -h mosquitto.$CLUSTER -p 9999 -u bob -P bob1234
mosquitto_pub -t public -h mosquitto.$CLUSTER -p 9999 -u bob -P bob1234 -m 42

mosquitto_sub -t "\$SYS/#" -h mosquitto.$CLUSTER -p 9999 -u alice -P alice1234
mosquitto_sub -t "\$SYS/#" -h mosquitto.$CLUSTER -p 9999 -u admin -P $PASSWORD
```
