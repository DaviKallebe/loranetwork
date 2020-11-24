#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <SSD1306Wire.h>


#define OLED_SDA 4
#define OLED_SCL 15
#define OLED_RST 16

#define SCK  5
#define MISO 19
#define MOSI 27
#define SS   18
#define RST  14
#define DI0  26

#define uS_TO_S_FACTOR 1000000ULL
#define TIME_TO_SLEEP  10
#define RF95_FREQ 915.0


const uint8_t IS_GATEWAY_ON[] = "PRTCL1";
const uint8_t GATEWAY_ON[]    = "PRTCL1.Y";

RH_RF95 rf95(SS, DI0);
SSD1306Wire display(0x3C, OLED_SDA, OLED_SCL);

//Teste
RTC_DATA_ATTR float valorsensor = 0.0f;

void setup() {
    Serial.begin(115200);
    delay(1000);

    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

    SPI.begin(SCK, MISO, MOSI, SS);
    while (!Serial);
        if (!rf95.init())
            Serial.println("Init failed.");
            
    rf95.setFrequency(RF95_FREQ);
    rf95.setTxPower(20);
    rf95.setSignalBandwidth(500000);
    rf95.setSpreadingFactor(9);
    rf95.setCodingRate4(6);  
    
    delay(1000);

    send_sensor_value();

    Serial.println("Dormindo");

    esp_deep_sleep_start();
}

void send_sensor_value() {
    String value;
    uint8_t *data;

    rf95.setModeTx();
    rf95.send(IS_GATEWAY_ON, sizeof(IS_GATEWAY_ON));
    rf95.setModeRx();

    Serial.println("Server is on?");

    if (rf95.waitAvailableTimeout(3000)) {
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
    //
}
