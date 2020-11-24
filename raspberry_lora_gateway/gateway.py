from gateway_rhrf95 import GatewayLoRaRF95
from gateway_mqtt import GatewayMQTT

def main():
    lora_device = GatewayLoRaRF95()
    lora_device.start()

    mqtt_client = GatewayMQTT(lora_device.message_queue)
    mqtt_client.start("192.168.1.2")

    print("Start listening")

    i = 0

    for msg in lora_device.listen_lora():
        print(msg)
        mqtt_client.publish_sensor_value(msg)
        i = i + 1

        #if i % 2 == 0:
        #    lora_device.add_message("KKK" + str(i))
        #    lora_device.add_message("KKM" + str(i))

if __name__ == "__main__":
    main()
