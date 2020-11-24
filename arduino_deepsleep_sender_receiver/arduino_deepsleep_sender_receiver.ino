#include <SPI.h>
#include <RH_RF95.h>
#include <LowPower.h>

#define uS_TO_S_FACTOR 1000000ULL
#define TIME_TO_SLEEP  10
#define RF95_FREQ 915.0
#define MAX_CYCLES 2


const uint8_t IS_GATEWAY_ON[] = "PRTCL1";
const uint8_t GATEWAY_ON[]    = "PRTCL1.Y";

RH_RF95 rf95;

//Teste
float valorsensor = 0.0f;
int ciclos = MAX_CYCLES;

void setup() {
    Serial.begin(9600);
    delay(1000);

    while (!Serial);
        if (!rf95.init())
            Serial.println("Init failed.");
            
    rf95.setFrequency(RF95_FREQ);
    rf95.setTxPower(20);
    rf95.setSignalBandwidth(500000);
    rf95.setSpreadingFactor(9);
    rf95.setCodingRate4(6);  
    
    delay(1000);
}

bool message_avaiable(int timeout) {
    unsigned long initialTime = millis();
    
    while ((unsigned long)(millis() - initialTime) < timeout) {
      Serial.println("loop");
      delay(200);
      if (rf95.available()) {
          Serial.println("Mensagem disponivel");
          delay(100);
          return true;
      }

      delay(100);
    }

    unsigned long mls = millis();
    Serial.println(String(mls) + " - " + String(initialTime) + " = " + String((unsigned long)(millis() - initialTime)) + "  timeout: " + String(timeout));
    Serial.println("no loop");

    return false;       
}

void send_sensor_value() {
    String value;
    uint8_t *data;

    rf95.setModeTx();
    rf95.send(IS_GATEWAY_ON, sizeof(IS_GATEWAY_ON));
    rf95.setModeRx();

    Serial.println("Server is on?");

    if (message_avaiable(10000)) {
        uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
        uint8_t len = sizeof(buf);

        if (rf95.recv(buf, &len)) {
            Serial.println((char *)buf);            
            Serial.println(RH_RF95_MAX_MESSAGE_LEN);
            
            if (strncmp((char *)buf, (char *)GATEWAY_ON, sizeof(GATEWAY_ON)) == 0) {
                delay(1500);
                
                value = "V-" + String(++valorsensor, 2) + "\0";
                //data = reinterpret_cast<uint8_t *>(&value[0]);
                char copy[10];
                value.toCharArray(copy, value.length()+1);
            
                uint8_t data[value.length()+1] = {0};
                
                for(uint8_t i = 0; i<= value.length(); i++) 
                  data[i] = (uint8_t)copy[i];

                rf95.setModeTx();
                rf95.send(data, sizeof(data));
                rf95.waitPacketSent();
                rf95.setModeIdle();

                Serial.print("Sent: ");
                Serial.println((char *)data);
            }
        }
    }
    else {
        Serial.println("Nope");
    }

    delay(100);
}

void loop() {
    send_sensor_value();    

    rf95.sleep();
    Serial.println("Domindo");
    delay(500);

    while (ciclos > 0) {
        LowPower.idle(SLEEP_8S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF,
                     SPI_OFF, USART0_OFF, TWI_OFF);

        Serial.println(ciclos--);
        delay(500);
    }

    rf95.setModeIdle();    
    ciclos = MAX_CYCLES;

    delay(500);
}
