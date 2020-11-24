#!/usr/bin/python

'''
arduino led
	aguardar por pacote
	se o pacote for para ligar ou desligar
		executar comando
'''

'''
	arduino sensor
		ler sensor
		enviar dados do sensor para o gateway
'''





import time, sys, os, random
from datetime import datetime
# Add path to pyRadioHeadRF95 module
sys.path.append(os.path.dirname(__file__) + "/../")

import pyRadioHeadRF95 as radio
import paho.mqtt.client as mqtt

# SetUp Geral

# Configurando RadioHead
rf95 = radio.RF95()
rf95.init()
rf95.setTxPower(20, False)
rf95.setFrequency(915)
rf95.setSpreadingFactor(rf95.SpreadingFactor9)
rf95.setCodingRate4(rf95.CodingRate4_6)
rf95.setSignalBandwidth(500000)

# Metodo para quando o cliente recebe uma resposta CONNACK do servidor MQTT
def on_connect(client, userdata, flags, rc):
	print("Conexao com o Broker estabelida com sucesso com codigo " + str(rc))
	# subscribes to the topic
	client.subscribe("arduino/led")
	print("Gateway escrito no topico: arduino/led")

# Metodo para lidar quando o servidor publica uma mensagem em um topico que o cliente esta inscrito	
def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))
	rf95.send(str(msg.payload), len(msg.payload))
	rf95.waitPacketSent()
	print("pacote enviado, dormindo..")
	sys.stdout.flush()

	# na realidade, aqui o comando eh repassado para o arduino
	# chamar funcoes da radiohead para enviar o comando para o arduino

# Configurando o cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("10.208.3.226") # 1883, 60


# Iniciando a thread que ira escutar e lidar com o canal do MQTT
#client.loop_start()
print('Conexao com o broker estabelecida. Thread do Broker iniciada...Aguardando mensagens do topico')
# client.loop_forever()


bw = 0
print("Rasp Iniciado! em:")
print(datetime.now())
print("-"*50)
sys.stdout.flush()

msg = 'LED-0'
msg2 = 'LED-1'
#while True:
#	continue

'''while True:
	rf95.send(msg, len(msg))
	rf95.waitPacketSent()
	print("LED-0 enviado, dormindo..")
	time.sleep(5)
	rf95.send(msg2, len(msg2))
	rf95.waitPacketSent()
	print("LED-1 enviado, dormindo..")
	time.sleep(5)'''

#'''
while bw < 10:
	rf95.setSignalBandwidth(500000)
	while True:
		# escutando	
		#if rf95.available() or random.randint(0,4) == 1:
		if rf95.available():
			print("trying listening LoRa")
			(msg, l) = rf95.recv()
			if(msg):
				valor = msg.split('-')
				valor[1]
				client.publish("arduino/sensor", valor[1])				
				# client.publish("arduino/sensor", msg)				
				print('msg:', msg, l)
				print(valor[1])
				# print(msg)
				print('finish\n')
				sys.stdout.flush()
			#time.sleep(1)
		else:
			print("Waiting mqtt response")
			client.loop_start()
			time.sleep(1)
#'''
