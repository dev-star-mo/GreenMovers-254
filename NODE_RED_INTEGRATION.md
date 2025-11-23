# Node-RED Integration Guide

This guide explains how to connect your Node-RED instance to the Forest Protection Dashboard.

## API Endpoint

**URL**: `https://your-backend-url.onrender.com/api/alerts`  
**Method**: POST  
**Content-Type**: application/json  
**Authentication**: None required (public endpoint for Node-RED)

## Request Format

The API expects a JSON payload with the following fields:

```json
{
  "sensor_id": "string (required)",
  "sensor_name": "string (optional)",
  "alert_time": "ISO 8601 datetime string (optional, defaults to current time)"
}
```

### Example Payload

```json
{
  "sensor_id": "ESP32_001",
  "sensor_name": "North Forest Sensor",
  "alert_time": "2024-01-15T10:30:00Z"
}
```

## Node-RED Flow Setup

### Step 1: Extract Data from LoRaWAN Payload

Add a function node to extract sensor information from your ChirpStack payload:

```javascript
// Extract sensor data from LoRaWAN payload
msg.sensor_id = msg.payload.devEui || msg.payload.deviceInfo?.devEui || "unknown";
msg.sensor_name = msg.payload.deviceName || msg.payload.deviceInfo?.name || `Sensor ${msg.sensor_id}`;
msg.alert_time = new Date().toISOString();

return msg;
```

### Step 2: Create HTTP Request Node

1. Add an **HTTP Request** node to your flow
2. Configure it as follows:
   - **Method**: POST
   - **URL**: `https://your-backend-url.onrender.com/api/alerts`
   - **Headers**: 
     - Key: `Content-Type`
     - Value: `application/json`
   - **Return**: `a parsed JSON object`

### Step 3: Format the Request Body

Add a function node before the HTTP Request node to format the payload:

```javascript
// Format payload for dashboard API
msg.payload = {
    sensor_id: msg.sensor_id,
    sensor_name: msg.sensor_name,
    alert_time: msg.alert_time
};

msg.headers = {
    "Content-Type": "application/json"
};

return msg;
```

### Step 4: Handle Response

Add a debug node or function node to handle the response:

```javascript
if (msg.statusCode === 200) {
    node.log("Alert successfully sent to dashboard");
    node.log("Alert ID: " + msg.payload.id);
} else {
    node.error("Failed to send alert: " + msg.payload);
}

return msg;
```

## Complete Example Flow

```
[LoRaWAN Input] 
    ↓
[Extract Sensor Data Function]
    ↓
[Format Payload Function]
    ↓
[HTTP Request to Dashboard]
    ↓
[Handle Response Function]
    ↓
[Debug/Log Output]
```

## Function Node Code

### Extract Sensor Data

```javascript
// This function extracts sensor information from your LoRaWAN payload
// Adjust based on your actual payload structure

var payload = msg.payload;

// Extract sensor ID (adjust field names based on your payload)
msg.sensor_id = payload.devEui || 
                payload.deviceInfo?.devEui || 
                payload.sensor_id || 
                "unknown_sensor";

// Extract sensor name
msg.sensor_name = payload.deviceName || 
                  payload.deviceInfo?.name || 
                  payload.sensor_name || 
                  `Sensor ${msg.sensor_id}`;

// Set alert time
msg.alert_time = new Date().toISOString();

return msg;
```

### Format Payload

```javascript
// Format the payload for the dashboard API
msg.payload = {
    sensor_id: msg.sensor_id,
    sensor_name: msg.sensor_name,
    alert_time: msg.alert_time
};

msg.headers = {
    "Content-Type": "application/json"
};

return msg;
```

## Testing

You can test the integration using an Inject node:

1. Add an **Inject** node
2. Set the payload to:
```json
{
  "sensor_id": "TEST_001",
  "sensor_name": "Test Sensor",
  "alert_time": "2024-01-15T10:30:00Z"
}
```
3. Connect it to your HTTP Request node
4. Deploy and click the inject button
5. Check the dashboard to see if the alert appears

## Error Handling

Add error handling in your flow:

```javascript
// Error handling function
if (msg.statusCode !== 200) {
    node.error("API Error: " + JSON.stringify(msg.payload));
    // Optionally, store failed requests for retry
    msg.retry = true;
}

return msg;
```

## Monitoring

Monitor your Node-RED flow:
- Check HTTP Request node status
- Monitor dashboard for new alerts
- Set up alerts in Node-RED for failed requests

## Troubleshooting

### Connection Refused
- Verify the backend URL is correct
- Check if the Render service is running (may need to wake it up)
- Ensure CORS is properly configured

### 400 Bad Request
- Verify JSON format is correct
- Check that `sensor_id` is provided
- Ensure `Content-Type` header is set

### 500 Internal Server Error
- Check backend logs in Render dashboard
- Verify database connection
- Check if sensor creation is working

## Advanced: Adding Sensor Location

If your LoRaWAN payload includes GPS coordinates, you can update the sensor location:

**Endpoint**: `POST /api/sensors`  
**Payload**:
```json
{
  "sensor_id": "ESP32_001",
  "sensor_name": "North Forest Sensor",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

This will position the sensor icon on the dashboard map.


