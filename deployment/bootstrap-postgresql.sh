#!/bin/bash
cowsay "Bootstrap PostgreSQL"

# Wait for PostgreSQL to be ready.
echo "Waiting for PostgreSQL to become ready."
export POD_NAME=$(kubectl get pods -l app=postgresql -l role=master -o jsonpath='{ .items[0].metadata.name}')
kubectl wait --for=condition=ready pod/$POD_NAME

# Wait for the service to become available.
while [ -n "$(PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -c '\l' 2>&1 > /dev/null)" ]; do
  echo "Waiting for PostgreSQL to become accessible externally."
  sleep 1
done


# Create authorization table.
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c """
CREATE TABLE account(
   id SERIAL PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   pw VARCHAR(255) NOT NULL,
   super INTEGER
);"""

# Create authentication table.
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c """
CREATE TABLE acls(
   id SERIAL PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   topic VARCHAR(255) NOT NULL,
   rw INTEGER
);"""


# Create users alice (admin) and bob (normal user).
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c """
INSERT INTO account(username, pw, super)
VALUES
  ('alice', '$(docker run salekd/mosquitto-auth:0.0.1 -- /build/mosquitto-auth-plug/np -p alice1234)', 1),
  ('bob', '$(docker run salekd/mosquitto-auth:0.0.1 -- /build/mosquitto-auth-plug/np -p bob1234)', 0);
"""

PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "SELECT * FROM account"
#PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "DELETE FROM account"


# Give bob read-write access to the public topic.
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c """
INSERT INTO acls(username, topic, rw)
VALUES
  ('bob', 'public/#', 7);
"""

PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "SELECT * FROM acls"
#PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth -c "DELETE FROM acls"
