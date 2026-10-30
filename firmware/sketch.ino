#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <atomic>
#include "RingBuffer.h"

// Academic demo: all readings are simulated, never patient data.
constexpr uint32_t SAMPLE_MS = 5000;
constexpr size_t CAPACITY = 2000; // 10,000 s = 2 h 46 min 40 s without publishing.
constexpr int DHT_PIN = 15, POT_PIN = 34;
constexpr char TOPIC[] = "cardioia/rm568506/telemetry";
constexpr char BROKER[] = "broker.hivemq.com"; // Public plaintext demo ONLY.
struct Sample { uint32_t seq, uptime_ms; float temperature, humidity, acceleration; uint16_t bpm; bool sensor_error; };
RingBuffer<Sample, CAPACITY> backlog;
SemaphoreHandle_t queueMutex;
std::atomic<bool> simulatedOnline{true};
DHT dht(DHT_PIN, DHT22);
Adafruit_MPU6050 mpu;
bool mpuReady = false;
uint32_t sequence = 0;
char sessionId[9];

void numberOrNull(char *out, size_t n, float value) {
  if (isfinite(value)) snprintf(out, n, "%.2f", value);
  else snprintf(out, n, "null");
}
void collectSample() {
  Sample s{};
  s.seq = ++sequence; s.uptime_ms = millis();
  s.temperature = dht.readTemperature(); s.humidity = dht.readHumidity();
  if (!isfinite(s.temperature) || s.temperature < -40 || s.temperature > 80) s.temperature = NAN;
  if (!isfinite(s.humidity) || s.humidity < 0 || s.humidity > 100) s.humidity = NAN;
  // Potentiometer is a control for synthetic BPM, NOT a cardiac sensor.
  s.bpm = 40 + (uint32_t(analogRead(POT_PIN)) * 140 / 4095);
  sensors_event_t a, g, t;
  bool imuOK = mpuReady && mpu.getEvent(&a, &g, &t);
  s.acceleration = imuOK ? sqrtf(a.acceleration.x*a.acceleration.x + a.acceleration.y*a.acceleration.y + a.acceleration.z*a.acceleration.z) : NAN;
  s.sensor_error = !isfinite(s.temperature) || !isfinite(s.humidity) || !isfinite(s.acceleration);
  xSemaphoreTake(queueMutex, portMAX_DELAY);
  backlog.push(s); size_t queued = backlog.size(); uint32_t dropped = backlog.dropped();
  xSemaphoreGive(queueMutex);
  Serial.printf("COLLECT seq=%lu queued=%u dropped=%lu sensor_error=%d\n", (unsigned long)s.seq, unsigned(queued), (unsigned long)dropped, s.sensor_error);
}

// All potentially blocking DNS/TCP/MQTT work is isolated from the sampler task.
void networkTask(void *) {
  WiFiClient transport;
  PubSubClient mqtt(transport);
  mqtt.setServer(BROKER, 1883); mqtt.setBufferSize(768); mqtt.setSocketTimeout(1);
  uint32_t lastWifiAttempt = millis() - 10000, lastMqttAttempt = millis() - 5000;
  char clientId[48]; snprintf(clientId, sizeof(clientId), "cardioia-rm568506-%s", sessionId);
  for (;;) {
    if (!simulatedOnline.load()) {
      if (mqtt.connected()) mqtt.disconnect();
      vTaskDelay(pdMS_TO_TICKS(50)); continue;
    }
    uint32_t now = millis();
    if (WiFi.status() != WL_CONNECTED) {
      if (uint32_t(now-lastWifiAttempt) >= 10000) {
        lastWifiAttempt = now; WiFi.begin("Wokwi-GUEST", "", 6);
      }
      vTaskDelay(pdMS_TO_TICKS(50)); continue;
    }
    if (!mqtt.connected()) {
      if (uint32_t(now-lastMqttAttempt) >= 5000) {
        lastMqttAttempt = now;
        Serial.printf("MQTT connect=%d\n", mqtt.connect(clientId));
      }
      vTaskDelay(pdMS_TO_TICKS(50)); continue;
    }
    mqtt.loop();
    Sample s; size_t queued; uint32_t dropped;
    xSemaphoreTake(queueMutex, portMAX_DELAY);
    bool available = backlog.peek(s); queued = backlog.size(); dropped = backlog.dropped();
    xSemaphoreGive(queueMutex);
    if (available && simulatedOnline.load()) {
      char temp[24], humidity[24], acceleration[24], payload[640];
      numberOrNull(temp, sizeof(temp), s.temperature);
      numberOrNull(humidity, sizeof(humidity), s.humidity);
      numberOrNull(acceleration, sizeof(acceleration), s.acceleration);
      snprintf(payload, sizeof(payload), "{\"device_id\":\"cardioia-rm568506\",\"session_id\":\"%s\",\"synthetic\":true,\"seq\":%lu,\"uptime_ms\":%lu,\"age_ms\":%lu,\"temperature\":%s,\"humidity\":%s,\"bpm\":%u,\"acceleration\":%s,\"sensor_error\":%s,\"queued\":%u,\"dropped\":%lu}", sessionId, (unsigned long)s.seq, (unsigned long)s.uptime_ms, (unsigned long)(uint32_t(millis() - s.uptime_ms)), temp, humidity, s.bpm, acceleration, s.sensor_error ? "true":"false", unsigned(queued), (unsigned long)dropped);
      // QoS 0: true means library accepted/wrote packet, NOT broker acknowledgement.
      if (mqtt.publish(TOPIC, payload, false)) {
        Serial.print("PUBLISH_QOS0 "); Serial.println(payload);
        xSemaphoreTake(queueMutex, portMAX_DELAY);
        backlog.popIfSequence(s.seq);
        xSemaphoreGive(queueMutex);
      }
    }
    // Drain <= 10/s, yielding between messages; sample acquisition remains 1/5s.
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}
void setup() {
  Serial.begin(115200); dht.begin(); Wire.begin(21, 22); Wire.setTimeOut(50);
  mpuReady = mpu.begin();
  analogReadResolution(12);
  snprintf(sessionId, sizeof(sessionId), "%08lx", (unsigned long)esp_random());
  queueMutex = xSemaphoreCreateMutex();
  if (!queueMutex) { Serial.println("FATAL mutex allocation"); while(true) delay(1000); }
  WiFi.mode(WIFI_STA);
  Serial.printf("CardioIA SYNTHETIC session=%s capacity=%u RAM=%u bytes\n", sessionId, unsigned(CAPACITY), unsigned(sizeof(backlog)));
  Serial.println("Commands: 0=offline, 1=online, s=queue status. RAM lost on reset.");
  if (xTaskCreate(networkTask, "mqtt", 8192, nullptr, 1, nullptr) != pdPASS) Serial.println("ERROR network task failed; collecting offline only");
}
void loop() {
  while (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '0' || cmd == '1') {
      simulatedOnline.store(cmd == '1');
      Serial.printf("SIMULATED_ONLINE=%d\n", simulatedOnline.load());
    }
    if (cmd == 's') {
      xSemaphoreTake(queueMutex, portMAX_DELAY);
      Serial.printf("QUEUE size=%u dropped=%lu\n", unsigned(backlog.size()), (unsigned long)backlog.dropped());
      xSemaphoreGive(queueMutex);
    }
  }
  static uint32_t lastSample = millis() - SAMPLE_MS;
  uint32_t now = millis();
  if (uint32_t(now-lastSample) >= SAMPLE_MS) { lastSample = now; collectSample(); }
  delay(10); // Yield CPU. No network wait in the collector loop.
}
