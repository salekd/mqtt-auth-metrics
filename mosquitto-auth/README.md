# Mosquitto with authentication plugin

https://github.com/jpmens/mosquitto-auth-plug

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

mo mosquitto.conf_template > mosquitto.conf
```

```
export DOCKER_ID_USER="salekd"
docker login https://index.docker.io/v1/

docker build . -f ./Dockerfile -t mosquitto-auth --no-cache
docker tag mosquitto-auth $DOCKER_ID_USER/mosquitto-auth:0.0.2
docker push $DOCKER_ID_USER/mosquitto-auth:0.0.2
```

## Build mosquitto and mosquito-auth-plug in Ubuntu

```
apt-get update
apt-get install -y git vim
apt-get install -y build-essential uuid-dev libssl-dev libpq-dev xsltproc docbook-xsl

#apt list -a libmosquitto-dev
# We need to build mosquitto ourselves because this is the latest version
# available as an Ubunutu package: libmosquitto-dev=1.4.15-2

mkdir /build
cd /build
git clone --branch v1.5.8 https://github.com/eclipse/mosquitto.git
cd /build/mosquitto
make
ln -s /build/mosquitto/lib/libmosquitto.so.1 /usr/lib/x86_64-linux-gnu/libmosquitto.so

cd /build
git clone --branch 0.1.3 https://github.com/jpmens/mosquitto-auth-plug.git
cd /build/mosquitto-auth-plug
echo """# Select your backends from this list
BACKEND_CDB ?= no
BACKEND_MYSQL ?= no
BACKEND_SQLITE ?= no
BACKEND_REDIS ?= no
BACKEND_POSTGRES ?= yes
BACKEND_LDAP ?= no
BACKEND_HTTP ?= no
BACKEND_JWT ?= no
BACKEND_MONGO ?= no
BACKEND_FILES ?= yes
BACKEND_MEMCACHED ?= no

# Specify the path to the Mosquitto sources here
# MOSQUITTO_SRC = /usr/local/Cellar/mosquitto/1.4.12
MOSQUITTO_SRC = /build/mosquitto

# Specify the path the OpenSSL here
OPENSSLDIR = /usr/include/openssl/

# Add support for django hashers algorithm name
SUPPORT_DJANGO_HASHERS ?= no

# Specify optional/additional linker/compiler flags here
# On macOS, add
#	CFG_LDFLAGS = -undefined dynamic_lookup
# as described in https://github.com/eclipse/mosquitto/issues/244
#
# CFG_LDFLAGS = -undefined dynamic_lookup  -L/usr/local/Cellar/openssl/1.0.2l/lib
# CFG_CFLAGS = -I/usr/local/Cellar/openssl/1.0.2l/include -I/usr/local/Cellar/mosquitto/1.4.12/include
CFG_LDFLAGS =  -L/usr/lib/x86_64-linux-gnu
CFG_CFLAGS = -I/usr/include/openssl -I/build/mosquitto/include""" > config.mk
make

mkdir /etc/mosquitto
echo """pid_file /var/run/mosquitto.pid

persistence false
#persistence_location /mosquitto/data

#log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
log_type all

sys_interval 10

auth_plugin /build/mosquitto-auth-plug/auth-plug.so
auth_opt_backends postgres
auth_opt_host localhost
auth_opt_port 5432
auth_opt_dbname mosquitto-auth
auth_opt_user postgres
auth_opt_pass $PASSWORD
auth_opt_userquery SELECT pw FROM account WHERE username = $1 limit 1
auth_opt_superquery SELECT COALESCE(COUNT(*),0) FROM account WHERE username = $1 AND super = 1
auth_opt_aclquery SELECT topic FROM acls WHERE (username = $1) AND (rw & $2) > 0""" > /etc/mosquitto/mosquitto.conf
/build/mosquitto/src/mosquitto -c /etc/mosquitto/mosquitto.conf
```

## Generate hashes

```
cd /build/mosquitto-auth-plug
./np -p alice1234
./np -p bob1234
```

```
docker run salekd/mosquitto-auth:0.0.1 -- /build/mosquitto-auth-plug/np -p alice1234
docker run salekd/mosquitto-auth:0.0.1 -- /build/mosquitto-auth-plug/np -p bob1234
```

## PostgreSQL tables

```
PGPASSWORD=$PASSWORD psql --host postgresql.$CLUSTER --port 9998 -U postgres -d mosquitto-auth 


CREATE TABLE account(
   id SERIAL PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   pw VARCHAR(255) NOT NULL,
   super INTEGER
);

INSERT INTO account(username, pw, super)
VALUES
  ('alice', 'PBKDF2$sha256$901$ee4JHzlAW/xquAa8$a4Q343e9Y6seQSDMhEObiG2HAtAXkLIW', 1),
  ('bob', 'PBKDF2$sha256$901$zmYzFG27Dxp7kHMb$xpVsaoRJscIr4xySDjfjQ3lU3qgYcNZb', 0);

SELECT * FROM account;


CREATE TABLE acls(
   id SERIAL PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   topic VARCHAR(255) NOT NULL,
   rw INTEGER
);

INSERT INTO acls(username, topic, rw)
VALUES
  ('bob', 'public/#', 7);

SELECT * FROM acls;
```

The permission values used in Mosquitto 1.5 are 2 for write, 5 for read+subscribe, 7 for read/write.
