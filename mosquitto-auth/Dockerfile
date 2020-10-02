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

FROM alpine:3.12

LABEL maintainer "David Salek <david.salek@surfsara.nl>"

RUN apk --no-cache --update add git build-base util-linux-dev postgresql-dev libxslt docbook-xsl \
    mosquitto-dev>1.6.9-r0 mosquitto>1.6.9-r0 mosquitto-clients>1.6.9-r0

# Clone the master branch instead of the latest tag 0.1.3.
# There have been some important updates after this tag and the repository is archived.
# RUN git clone --branch 0.1.3 https://github.com/jpmens/mosquitto-auth-plug.git
RUN git clone https://github.com/jpmens/mosquitto-auth-plug.git
COPY config.mk /mosquitto-auth-plug/
COPY auth-plug.c /mosquitto-auth-plug/
RUN cd /mosquitto-auth-plug && make

EXPOSE 1883

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# COPY mosquitto.conf /etc/mosquitto/mosquitto.conf
CMD ["/usr/sbin/mosquitto", "-c", "/etc/mosquitto/mosquitto.conf"]
