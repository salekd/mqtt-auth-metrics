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

import logging
from configparser import ConfigParser
from prometheus_client import start_http_server
from prometheus_client import Counter, Gauge
import paho.mqtt.client as mqtt


# Read config file.
config = ConfigParser()
config.read('mqtt-exporter.cfg')

mqtt_host = config.get('MQTT', 'host')
mqtt_port = config.getint('MQTT', 'port')
mqtt_user = config.get('MQTT', 'user')
mqtt_password = config.get('MQTT', 'password')
# Certificate is optional (only when TLS is required).
if config.has_option('MQTT', 'cert'):
    mqtt_cert = config.get('MQTT', 'cert')
else:
    mqtt_cert = None
mqtt_topics = config.get('MQTT', 'topics').split(',')

level_dict = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}
log_level = level_dict[config.get('Log', 'level')]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log_level)
logger = logging.getLogger(__name__)

logger.info(f"Topics to be monitored at level-2: {mqtt_topics}")


# Prometheus count with topic as a label,
# used for message traffic monitoring at a topic/project level.
count_count = Counter("mqtt_topic_count", "Number of messages per topic", ['topic'])
count_bytes = Counter("mqtt_topic_bytes", "Bytes per topic", ['topic'])

# Prometheus gauge with topic as a label,
# used for the MQTT metrics send to the $SYS topics.
gauge_sys = Gauge("mqtt_SYS", "MQTT $SYS metrics", ['topic'])


def on_connect(client, obj, flags, rc):
    logger.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe([("#", 0), ("$SYS/#", 0)])


def on_disconnect(client, obj, rc):
    if rc != 0:
        logger.warning("Unexpected disconnection.")


def on_message_topic(client, obj, msg):
    logger.debug("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    if msg.retain == 1:
        logger.debug("This is a retained message.")

    # Monitor metrics per level-1 topic, e.g. public, project1, project2.
    # If the level-1 part of a topic is mentioned in the mqtt_topics array,
    # the monitoring will is split at level-2, e.g. pipeline/project1, pipeline/project2.
    levels = msg.topic.split('/')
    topic = levels[0]
    if levels[0] in mqtt_topics and len(levels) > 1:
        topic += '/' + levels[1]

    # Export metrics.
    logger.debug("Adding " + str(len(msg.payload)) + " bytes for topic " + topic)
    count_count.labels(topic).inc()
    count_bytes.labels(topic).inc(len(msg.payload))


def on_message_sys(client, obj, msg):
    logger.debug("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    if msg.retain == 1:
        logger.debug("This is a retained message.")

    # Skip some topics.
    if msg.topic in ['$SYS/broker/version', '$SYS/broker/timestamp']:
        return

    # Convert from bytes to string.
    payload = str(msg.payload.decode("utf-8"))
    # Broker uptime is sent as '1234 seconds'. Get only the number.
    if msg.topic == '$SYS/broker/uptime':
        payload = payload[:payload.find(' ')]

    # Export metrics.
    gauge_sys.labels(msg.topic).set(float(payload))


def on_publish(client, obj, mid):
    logger.info("Messaged ID: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)

    mqttc = mqtt.Client()

    mqttc.enable_logger(logger)

    mqttc.message_callback_add("#", on_message_topic)
    mqttc.message_callback_add("$SYS/#", on_message_sys)
    #mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.username_pw_set(mqtt_user, mqtt_password)
    # Use TLS if a certificate was specified in the configuration file.
    if mqtt_cert:
        mqttc.tls_set(mqtt_cert)
    mqttc.connect(mqtt_host, mqtt_port, 60)

    mqttc.loop_forever()
