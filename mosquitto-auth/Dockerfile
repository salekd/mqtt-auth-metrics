# Copyright 2020, SURFsara.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM alpine:3.8

LABEL maintainer "David Salek <david.salek@surfsara.nl>"

COPY docker-entrypoint.sh /
COPY config.mk /
COPY mosquitto.conf /etc/mosquitto/mosquitto.conf 

RUN set -x && \
    apk --no-cache add git \
        build-base util-linux-dev postgresql-dev libxslt docbook-xsl && \
    mkdir -p /build && \
    cd /build && git clone --branch v1.5.8 https://github.com/eclipse/mosquitto.git && \
    cd /build/mosquitto && make && \
    addgroup -S -g 1883 mosquitto 2>/dev/null && \
    adduser -S -u 1883 -D -H -h /var/empty -s /sbin/nologin -G mosquitto -g mosquitto mosquitto 2>/dev/null && \
    ln -s /build/mosquitto/lib/libmosquitto.so.1 /usr/lib/libmosquitto.so && \
    ln -s /build/mosquitto/lib/libmosquitto.so.1 /usr/lib/libmosquitto.so.1 && \
    mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log && \
    install -d /usr/sbin/ && \
    install -s -m755 /build/mosquitto/src/mosquitto /usr/sbin/mosquitto && \
    install -s -m755 /build/mosquitto/src/mosquitto_passwd /usr/bin/mosquitto_passwd && \
    install -m644 /build/mosquitto/mosquitto.conf /mosquitto/config/mosquitto.conf && \
    chown -R mosquitto:mosquitto /mosquitto && \
    cd /build && git clone --branch 0.1.3 https://github.com/jpmens/mosquitto-auth-plug.git && \
    mv /config.mk /build/mosquitto-auth-plug && \
    cd /build/mosquitto-auth-plug && make

EXPOSE 1883

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["/usr/sbin/mosquitto", "-c", "/etc/mosquitto/mosquitto.conf"]
