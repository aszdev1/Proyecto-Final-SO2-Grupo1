# Proyecto-Final-SO2-Grupo1

## Ambiente de desarrollo

### Version backend python 
Python 3.13.7

Copiar .env.example -> Renombrar a .env

```powershell
cd C:\Proyecto-Final-SO2-Grupo1\backend
```

```powershell
pip install -r requirements.txt

uvicorn main:app --reload
```


## Documentacion
http://localhost:3000/docs

## Insertar evento
```powershell
curl -X POST http://localhost:3000/event \
-H "Content-Type: application/json" \
-d '{"evento":"sensor","estado":"activo"}'
```

## Index
http://localhost


## Compilar

```powershell
build.bat
```

# Manual de API Backend — Sistema de Monitoreo de Eventos

# Información General

Backend desarrollado con:

- FastAPI
- MongoDB
- Docker

Base URL:

```plaintext
http://IP_PUBLICA:3000
```

Prefijo API:

```plaintext
/api
```

---

# Arquitectura

```plaintext
ESP32 / Robot
      |
      v
FastAPI Backend
      |
      v
MongoDB
      |
      v
Dashboard Frontend
   ------
Monitor de servicios

```

---

# Formato General

## Content-Type requerido

```http
Content-Type: application/json
```

---

# Estados HTTP utilizados

| Código | Significado |
|---|---|
| 200 | OK |
| 201 | Creado |
| 400 | Error petición |
| 404 | No encontrado |
| 500 | Error servidor |

---

# Estructura General de Respuesta

## Respuesta exitosa

```json
{
  "ok": true,
  "message": "Operación realizada"
}
```

---

## Respuesta error

```json
{
  "ok": false,
  "message": "Descripción error"
}
```

---

# ENDPOINTS

---

# 1. Verificar Estado Backend

## Endpoint

```http
GET /api/health
```

---

## Descripción

Verifica si el backend está funcionando correctamente.

---

## Request

No requiere body.

---

## Response 200

```json
{
  "ok": true,
  "service": "backend",
  "status": "online"
}
```

---

# 2. Verificar Estado MongoDB

## Endpoint

```http
GET /api/mongo-status
```

---

## Descripción

Verifica conexión con MongoDB.

---

## Request

No requiere body.

---

## Response 200

```json
{
  "ok": true,
  "database": "mongodb",
  "status": "connected"
}
```

---

## Response 500

```json
{
  "ok": false,
  "database": "mongodb",
  "status": "disconnected"
}
```

---

# 3. Registrar Evento

## Endpoint

```http
POST /api/event
```

---

# Descripción

Permite registrar eventos enviados por el ESP32 o robot.

---

# JSON Request

## Formato general

```json
{
  "robot_id": "robot_01",
  "tipo": "movimiento",
  "evento": "adelante",
  "nivel": "info",
  "datos": {},
  "timestamp": "2026-05-18T10:00:00"
}
```

---

# Campos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| robot_id | string | Sí | Identificador robot |
| tipo | string | Sí | Categoría evento |
| evento | string | Sí | Nombre evento |
| nivel | string | No | info, warning, critical |
| datos | object | No | Información adicional |
| timestamp | string | No | Fecha evento |

---

# Tipos de Evento Recomendados

| Tipo |
|---|
| movimiento |
| sensor |
| temperatura |
| energia |
| error |
| sistema |
| otro |

---

# Ejemplo Movimiento

```json
{
  "robot_id": "robot_01",
  "tipo": "movimiento",
  "evento": "adelante",
  "nivel": "info",
  "datos": {
    "velocidad": 80
  }
}
```

---

# Ejemplo Obstáculo

```json
{
  "robot_id": "robot_01",
  "tipo": "sensor",
  "evento": "obstaculo_detectado",
  "nivel": "warning",
  "datos": {
    "distancia_cm": 15
  }
}
```

---

# Ejemplo Error

```json
{
  "robot_id": "robot_01",
  "tipo": "error",
  "evento": "motor_fail",
  "nivel": "critical"
}
```

---

# Response 201

```json
{
  "ok": true,
  "message": "Evento registrado",
  "event_id": "6829f94db6e4a0d90e2c1201"
}
```

---

# Response 500

```json
{
  "ok": false,
  "message": "MongoDB no disponible"
}
```

---

# 4. Obtener Todos los Eventos

## Endpoint

```http
GET /api/events
```

---

# Descripción

Retorna todos los eventos registrados.

---

# Request

No requiere body.

---

# Response 200

```json
[
  {
    "_id": "6829f94db6e4a0d90e2c1201",
    "robot_id": "robot_01",
    "tipo": "movimiento",
    "evento": "adelante",
    "nivel": "info",
    "datos": {
      "velocidad": 80
    },
    "fecha": "2026-05-18T10:00:00"
  }
]
```

---

# 5. Obtener Eventos Recientes

## Endpoint

```http
GET /api/events/latest
```

---

# Descripción

Retorna los últimos eventos registrados.

---

# Parámetros Query

| Parámetro | Tipo | Ejemplo |
|---|---|---|
| limit | int | 10 |

---

# Ejemplo

```http
GET /api/events/latest?limit=5
```

---

# Response 200

```json
[
  {
    "_id": "6829f94db6e4a0d90e2c1201",
    "tipo": "sensor",
    "evento": "obstaculo_detectado"
  }
]
```

---

# 6. Filtrar Eventos por Tipo

## Endpoint

```http
GET /api/events/type/{tipo}
```

---

# Ejemplo

```http
GET /api/events/type/error
```

---

# Tipos válidos

| Tipo |
|---|
| movimiento |
| sensor |
| temperatura |
| energia |
| error |
| sistema |

---

# Response 200

```json
[
  {
    "_id": "6829f94db6e4a0d90e2c1201",
    "tipo": "error",
    "evento": "motor_fail",
    "nivel": "critical"
  }
]
```

---

# 7. Obtener Estadísticas

## Endpoint

```http
GET /api/stats
```

---

# Descripción

Retorna estadísticas generales del sistema.

---

# Response 200

```json
{
  "total_eventos": 150,
  "movimientos": 80,
  "errores": 5,
  "sensores": 30,
  "temperatura": 20,
  "energia": 15
}
```

---

# 8. Obtener Estado Robot

## Endpoint

```http
GET /api/robot/status
```

---

# Descripción

Retorna el último estado conocido del robot.

---

# Response 200

```json
{
  "robot_id": "robot_01",
  "estado": "activo",
  "ultimo_evento": "movimiento",
  "ultima_conexion": "2026-05-18T10:00:00",
  "bateria": 76
}
```

---

# 9. Eliminar Eventos

## Endpoint

```http
DELETE /api/events
```

---

# Descripción

Elimina todos los eventos registrados.

---

# Response 200

```json
{
  "ok": true,
  "message": "Eventos eliminados"
}
```

---

# Estructura MongoDB

## Base de datos

```plaintext
eventosdb
```

---

# Colección

```plaintext
eventos
```

---

# Documento MongoDB

```json
{
  "_id": "ObjectId",
  "robot_id": "robot_01",
  "tipo": "movimiento",
  "evento": "adelante",
  "nivel": "info",
  "datos": {},
  "timestamp": "2026-05-18T10:00:00",
  "fecha_servidor": "2026-05-18T10:00:01"
}
```

---

# Flujo Completo

```plaintext
ESP32
   |
POST /api/event
   |
   v
FastAPI
   |
   v
MongoDB
   |
   v
Frontend consulta:
GET /api/events
GET /api/stats
```

---

# Swagger FastAPI

Documentación automática:

```plaintext
http://IP_PUBLICA:3000/docs
```

---

# Seguridad Recomendada

## No exponer MongoDB públicamente

NO usar:

```yaml
27017:27017
```

---

# Docker recomendado

```yaml
restart: always
```

en todos los servicios.

---

# Recomendaciones Finales

## Frontend

Consumir:

| Endpoint |
|---|
| /api/events |
| /api/stats |
| /api/health |

---

# ESP32

Usar únicamente:

```http
POST /api/event
```

---

# Resultado Esperado

Sistema de monitoreo distribuido con:

- ESP32 simulando robot
- Backend FastAPI
- MongoDB
- Dashboard web
- Docker
- GitHub Actions
- VPS DigitalOcean

---

# Monitor de Servicios

Servicio que verifica periódicamente el estado de los 3 contenedores (backend, frontend, MongoDB).

## Funcionamiento

- Cada **15 segundos** hace un ping HTTP a backend y frontend, y un socket check a MongoDB.
- Guarda el historial de los últimos **10 minutos** en `monitor-servicios/data/monitor.json`.
- No depende de MongoDB para su almacenamiento (funciona incluso si MongoDB está caído).

## Dashboard

```
http://localhost:4000
```

Muestra:

| Indicador | Descripción |
|---|---|
| Estado | Online / Offline con indicador verde/rojo |
| Respuesta | Tiempo de respuesta en ms |
| Uptime | Porcentaje de disponibilidad (últimos 10 min) |
| Último chequeo | Hora del último check |
| Historial | Línea de tiempo con puntos verdes/rojos |

## Endpoints

```http
GET /                         → Dashboard HTML
GET /api/monitor/status       → Estado actual de cada servicio
GET /api/monitor/history      → Historial de checks
GET /api/monitor/stats        → Estadísticas de uptime
```

---

# Manual de Pruebas — Detener servicios uno a uno

Para probar que el monitor detecta correctamente las caídas, se pueden detener los servicios de forma individual. El monitor tarda hasta **15 segundos** en reflejar el cambio.

## Windows (PowerShell)

```powershell
# Detener solo MongoDB
docker stop mongodb

# Verificar que el monitor detecta la caída
# Abrir http://localhost:4000

# Volver a iniciar MongoDB
docker start mongodb
```

```powershell
# Detener solo el backend
docker stop backend
docker start backend
```

```powershell
# Detener solo el frontend
docker stop frontend
docker start frontend
```

```powershell
# Detener todos (simular caída total)
docker stop mongodb backend frontend

# Ver dashboard del monitor (debería mostrar todo offline)

# Reanudar todo
docker start mongodb backend frontend
```

## Linux

```bash
# Detener solo MongoDB
docker stop mongodb

# Verificar que el monitor detecta la caída
# Abrir http://localhost:4000

# Volver a iniciar MongoDB
docker start mongodb
```

```bash
# Detener solo el backend
docker stop backend
docker start backend
```

```bash
# Detener solo el frontend
docker stop frontend
docker start frontend
```

```bash
# Detener todos (simular caída total)
docker stop mongodb backend frontend

# Ver dashboard del monitor (debería mostrar todo offline)

# Reanudar todo
docker start mongodb backend frontend
```

> **Nota:** El monitor se ejecuta en su propio contenedor (`monitor`) y no debe detenerse durante las pruebas, ya que es quien observa y registra el estado de los demás servicios.