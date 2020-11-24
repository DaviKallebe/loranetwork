import time
import queue
import threading

from pyRadioHeadRF95 import RF95

class GatewayLoRaRF95:

    __is_gateway_on = "PRTCL1"
    __gateway_on    = "PRTCL1.Y"

    def start(self, 
              frequency        = RF95.Frequency915Mhz, 
              spreading_factor = RF95.SpreadingFactor9, 
              coding_rate4     = RF95.CodingRate4_6, 
              signal_bandwidth = RF95.Bandwidth500KHZ, 
              tx_power         = 20):
                   
        self.__rf95.init()
        self.__rf95.setTxPower(tx_power, False)
        self.__rf95.setFrequency(frequency)
        self.__rf95.setSpreadingFactor(spreading_factor)
        self.__rf95.setCodingRate4(coding_rate4)
        self.__rf95.setSignalBandwidth(signal_bandwidth)
        
        threading.Thread(target=self.__start_sending, daemon=True).start()
        
    #add a message to a waiting list
    #send messages as soon as possible
    def add_message(self, message):
        self.__queue.put(message)
        
    def start_listening(self):                
        while not self.__stop:
            received = False
            
            with self.__lora_available: #lock                                
                if self.__rf95.available():                    
                    (msg, l) = self.__rf95.recv() #message avaiable
                    
                    received = True
                    
            if received:
                yield msg.decode()
                
            time.sleep(1)
            
    def __message_available(self, timeout):
        initial_time = time.monotonic()
        
        while time.monotonic() - initial_time < timeout:
            if self.__rf95.available():
                return True
                
            time.sleep(.300)
                
        return False
            
    def listen_lora(self):
        #self.__rf95.setModeRx()
        
        while not self.__stop:            
            with self.__lora_available:            
                if self.__message_available(self.__timeout):
                    (msg, l) = self.__rf95.recv()
                    
                    print("Primeira Mensagem:", msg.decode(), "é igual?", msg.decode() == GatewayLoRaRF95.__is_gateway_on)
                    
                    if msg.decode() == GatewayLoRaRF95.__is_gateway_on:
                        resp = GatewayLoRaRF95.__gateway_on + '\0'
                        
                        print("Respondendo:", resp)
                        
                        self.__rf95.setModeTx()
                        time.sleep(.100)
                        self.__rf95.send(resp.encode("ascii"), len(resp))
                        time.sleep(.100)
                        self.__rf95.waitPacketSent()
                        time.sleep(.100)
                        self.__rf95.setModeRx()
                        
                        if self.__message_available(self.__timeout):
                            (value, l) = self.__rf95.recv() 

                            print("Recebido:", value.decode())
                            
                            yield value.decode()
               
            time.sleep(1)
                    
    def __start_sending(self):
        while not self.__stop:
            message = self.__queue.get()
            
            with self.__lora_available: #lock
                if not message.endswith('\0'):
                    message = message + '\0'
                    
                self.__rf95.send(message.encode("ascii"), len(message))
                
                time.sleep(.5)
                
                self.__rf95.waitPacketSent()
                
                self.__queue.task_done() 

            time.sleep(10)
                
    @property
    def message_queue(self):
        return self.__queue       
            
    def __init__(self):
        self.__rf95           = RF95()
        self.__queue          = queue.Queue()
        self.__stop           = False
        self.__timeout        = 3000 #in miliseconds
        self.__lora_available = threading.Lock()
