# Select your backends from this list
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
CFG_LDFLAGS =  -L/usr/lib
CFG_CFLAGS = -I/usr/include/openssl -I/build/mosquitto/include