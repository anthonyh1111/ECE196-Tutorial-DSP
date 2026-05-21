# Processing Sensor Data Tutorial

**Anthony Huynh — ECE 196 SP26**

---

## Brainstorm ideas / Overview
This tutorial will go in-depth about the higher-level functions required to reduce noise and provide accurate--parked car readings for our smart-parking sensor based system. We will be coding in python and using python libraries in conjunction with arduino for communication. In this tutorial we will cover the main objective, the supplies required, hardware setups, and the firmware required to complete this. 



---

## Objectives

- Understand how to interface sensors with an ESP32  
- Learn how to collect and process sensor data   
- Build a simple occupancy detection system  
- Detailed look into filtering sensor data with python. 

---

## Supplies

- ESP32 Development Board  
- Distance Sensor (VL53L0X or VL53L1X)  
- USB Cable  
- Model Car 

> **Note:** You can size the model down based on product availability. 

---

## Hardware Setup

1. Connect the sensor to the ESP32:
   - VCC → 3.3V  
   - GND → GND  
   - SDA → GPIO 26 (Choose a GPIO Data Pin) 
   - SCL → GPIO 21 (Choose a GPIO Data Pin)
  
   (Photo of ESP32 Devboard) 

2. Ensure all connections are secure.

3. Power the ESP32 via USB.

---

## Firmware (Hardware Code) 

Example Arduino-style code:

```cpp
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();
}

void loop() {
  Serial.println("Reading sensor...");
  delay(1000);
}
```

## Software 

