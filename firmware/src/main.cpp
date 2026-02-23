#include "OV2640.h"
#include <WiFi.h>
#include <WiFiClient.h>

#include "OV2640Streamer.h"
#include "CRtspSession.h"

#include "car.h"
#include "../include/wifikeys.h"

#include <WebSocketsServer.h>
#include <ArduinoJson.h>

OV2640 cam;
WiFiServer rtspServer(8554);
WebSocketsServer wsServer(81);

CStreamer *streamer;
CRtspSession *session;
WiFiClient client;

void debug(const char *message) {
    JsonDocument doc;
    doc["debug"] = message;
    String json;
    serializeJson(doc, json);
    wsServer.broadcastTXT(json);
}

void debug(String message) {
    JsonDocument doc;
    doc["debug"] = message;
    String json;
    serializeJson(doc, json);
    wsServer.broadcastTXT(json);
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    JsonDocument doc;

    switch(type) {

    case WStype_CONNECTED: {
        IPAddress ip = wsServer.remoteIP(num);
        String message = "Websocket connected: " + ip.toString();
        Serial.println(message);
        debug(message);
        break;
    };

    case WStype_TEXT: {
        DeserializationError error = deserializeJson(doc, (char*)payload);
        if(error.code() == DeserializationError::Code::Ok) {
            if(doc.containsKey("time")) {
                carSetRunTime(doc["time"]);
            }
            if(doc.containsKey("speed")) {
                carSetSpeed(doc["speed"]);
            }
            if(doc.containsKey("turn")) {
                carSetTurn(doc["turn"]);
            }
            if(doc.containsKey("ping")) {
                JsonDocument res;
                res["pong"] = doc["ping"];
                String json;
                serializeJson(res, json);
                wsServer.broadcastTXT(json);
            }
        } else {
            debug("Erro ao desserializar JSON");
            Serial.println("Erro ao desserializar JSON");
        }
        break;
    };

    default:
        break;
    }
}

void updateCarTask(void *params) {
    for(;;) {
        unsigned long now = millis();
        if (!carIsUpdated()) {
            carSetSpeed(DEF_SPEED);
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void wsLoopTask(void *params) {
    for(;;) {
        wsServer.loop();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void rtspLoopTask(void *params) {
    static uint32_t lastimage = millis();
    uint32_t msecPerFrame = 100;
    for(;;) {
        if(session) {
            session->handleRequests(0);
            uint32_t now = millis();
            if(now > lastimage + msecPerFrame || now < lastimage) {
                session->broadcastCurrentFrame(now);
                lastimage = now;
                now = millis();
                if(now > lastimage + msecPerFrame) {
                    printf("warning exceeding max frame rate of %d ms\n", now - lastimage);
                    char msg[128];
                    sprintf(msg, "Warning exceeding max frame rate. %d ms", now - lastimage);
                    debug(msg);
                }
            }
            if(session->m_stopped) {
                delete session;
                delete streamer;
                session = NULL;
                streamer = NULL;
            }
        }
        else {
            client = rtspServer.accept();
            if(client) {
                streamer = new OV2640Streamer(&client, cam);
                session = new CRtspSession(&client, streamer);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void scanNetworks() {
    int n = WiFi.scanNetworks();
    if(n == 0) {
        Serial.println("No Networks");
        return;
    }
    Serial.print(n);
    Serial.println(" networks found");
    Serial.println("Nr | SSID                             | RSSI | CH | Encryption");
    for(int i=0; i<n; i++) {
        Serial.printf("%2d",i + 1);
        Serial.print(" | ");
        Serial.printf("%-32.32s", WiFi.SSID(i).c_str());
        Serial.print(" | ");
        Serial.printf("%4d", WiFi.RSSI(i));
        Serial.print(" | ");
        Serial.printf("%2d", WiFi.channel(i));
        Serial.print(" | ");
        switch (WiFi.encryptionType(i))
        {
        case WIFI_AUTH_OPEN:
            Serial.print("open");
            break;
        case WIFI_AUTH_WEP:
            Serial.print("WEP");
            break;
        case WIFI_AUTH_WPA_PSK:
            Serial.print("WPA");
            break;
        case WIFI_AUTH_WPA2_PSK:
            Serial.print("WPA2");
            break;
        case WIFI_AUTH_WPA_WPA2_PSK:
            Serial.print("WPA+WPA2");
            break;
        case WIFI_AUTH_WPA2_ENTERPRISE:
            Serial.print("WPA2-EAP");
            break;
        case WIFI_AUTH_WPA3_PSK:
            Serial.print("WPA3");
            break;
        case WIFI_AUTH_WPA2_WPA3_PSK:
            Serial.print("WPA2+WPA3");
            break;
        case WIFI_AUTH_WAPI_PSK:
            Serial.print("WAPI");
            break;
        default:
            Serial.print("unknown");
        }
        Serial.println();
        delay(10);
    }
}

void setup() {
    carInit();

    Serial.begin(115200);

    camera_config_t config = esp32cam_aithinker_config;
    config.frame_size = FRAMESIZE_VGA;
    config.grab_mode = CAMERA_GRAB_LATEST;

    cam.init(config);

    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);

    wsServer.begin();
    wsServer.onEvent(webSocketEvent);

    rtspServer.begin();

    xTaskCreate(updateCarTask, "update car", 4096, NULL, 1, NULL);
    xTaskCreate(wsLoopTask, "websocket loop", 4096, NULL, 2, NULL);
    xTaskCreate(rtspLoopTask, "rtsp loop", 4096, NULL, 2, NULL);
}

void loop() {}
