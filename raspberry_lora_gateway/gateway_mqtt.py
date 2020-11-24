import paho.mqtt.client as mqtt
import traceback

class GatewayMQTT:
    __sensor_value_topic = "arduino/sensor"

    def start(self, ip_address):
        # Configurando o cliente MQTT
        
        try:
            self.__client.on_connect = self.on_connect
            self.__client.on_message = self.on_message
            self.__client.connect(ip_address)
        except ConnectionRefusedError:
            print("MQTT: Connection Refused")
            quit(0)

    # Metodo para quando o cliente recebe uma resposta CONNACK do servidor MQTT
    def on_connect(client, userdata, flags, rc):
        print("Conexao com o Broker estabelida com sucesso com codigo " + str(rc))
        # subscribes to the topic
        client.subscribe("arduino/led")
        print("Gateway escrito no topico: arduino/led")

    # Metodo para lidar quando o servidor publica uma mensagem em um topico que o cliente esta inscrito	
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        sys.stdout.flush()
        
        self.__queue.put(msg.payload)

    def publish_sensor_value(self, value):
        self.__client.publish(self.__sensor_value_topic, value)

    def __init__(self, queue):
        self.__client = mqtt.Client()
        self.__queue = queue               