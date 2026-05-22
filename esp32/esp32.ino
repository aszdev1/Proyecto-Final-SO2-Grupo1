#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "CLARO_2.4GHz_CFB0DE";
const char* password = "p%RdwGCEhZX9e9P";
const char* server = "http://163.192.133.68:3000";

unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));

  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
}

String getTimestamp() {
  time_t now = time(nullptr);
  struct tm* t = localtime(&now);
  char buf[30];
  strftime(buf, sizeof(buf), "%d/%m/%Y %I:%M:%S %p", t);
  return String(buf);
}

bool healthCheck() {
  HTTPClient http;
  http.begin(String(server) + "/api/v1/eventos");
  http.setTimeout(5000);
  int code = http.GET();
  http.end();
  return code == 200;
}

void sendEvent(const String& body) {
  HTTPClient http;
  http.begin(String(server) + "/api/v1/eventos");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  int code = http.POST(body);
  Serial.printf("HTTP %d -> %s\n", code, body.c_str());
  http.end();
}

String j(const char* tipo, const char* evento,
         const char* nivel, const String& datos) {
  return String("{\"robot_id\":\"robot_01\",\"tipo\":\"") + tipo
       + "\",\"evento\":\"" + evento
       + "\",\"nivel\":\"" + nivel
       + "\",\"datos\":" + datos + "}";
}

void loop() {
  unsigned long now = millis();
  if (now - lastSend < random(10000, 15000)) return;
  lastSend = now;

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado");
    return;
  }

  if (!healthCheck()) {
    Serial.println("Backend no disponible, reintentando en 10s");
    delay(10000);
    return;
  }

  int r = random(100);
  String body;

  if (r < 15) {
    body = j("movimiento","adelante","info","{\"velocidad\":" + String(random(30,101)) + "}");
  } else if (r < 25) {
    body = j("movimiento","detenido","info","{\"velocidad\":0}");
  } else if (r < 35) {
    body = j("movimiento","giro","info",
      "{\"velocidad\":" + String(random(30,101)) + ",\"angulo\":" + String(random(-90,91)) + "}");
  } else if (r < 45) {
    int d = random(5, 201);
    body = j("sensor","obstaculo_detectado", d < 20 ? "warning" : "info",
      "{\"distancia_cm\":" + String(d) + "}");
  } else if (r < 52) {
    body = j("sensor","ultrasonido","info",
      "{\"distancia_cm\":" + String(random(2,31)) + ",\"angulo\":" + String(random(0,361)) + "}");
  } else if (r < 60) {
    int t = random(18, 46);
    const char* n = "info";
    if (t > 40) n = "critical";
    else if (t > 35) n = "warning";
    body = j("temperatura","lectura",n,"{\"temperatura_c\":" + String(t) + "}");
  } else if (r < 68) {
    body = j("temperatura","sobrecalentamiento","critical",
      "{\"temperatura_c\":" + String(random(45,61)) + "}");
  } else if (r < 75) {
    int b = random(5, 101);
    const char* n = "info";
    if (b < 15) n = "critical";
    else if (b < 30) n = "warning";
    body = j("energia","bateria",n,"{\"bateria_pct\":" + String(b) + "}");
  } else if (r < 80) {
    body = j("energia","consumo","info","{\"consumo_ma\":" + String(random(50,501)) + "}");
  } else if (r < 87) {
    body = j("error","motor_fail","critical","{\"codigo\":" + String(random(100,106)) + "}");
  } else if (r < 92) {
    body = j("error","sensor_fail","warning",
      "{\"codigo\":" + String(random(200,204)) + ",\"sensor\":\"ultrasonido\"}");
  } else if (r < 97) {
    body = j("sistema","reinicio","warning","{\"accion\":\"reinicio_completo\"}");
  } else {
    body = j("otro","test","info","{\"mensaje\":\"prueba_conexion\"}");
  }

  sendEvent(body);
}

