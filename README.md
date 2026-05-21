# Smart Parking Sensor System Tutorial

**Anthony Huynh — ECE 196 SP26**

---

## 🧠 Brainstorm / Overview
This tutorial will go in-depth about the higher-level functions required to reduce noise and provide accurate--parked car readings for our smart-parking sensor based system. We will be coding in python and using python libraries in conjunction with arduino for communication. In this tutorial we will cover the main objective, the supplies required, hardware setups, and the firmware required to complete this. 



---

## 🎯 Objectives

- Understand how to interface sensors with an ESP32  
- Learn how to collect and process sensor data  
- Build a simple occupancy detection system  
- Transmit data to a user interface or dashboard  

---

## 🧰 Supplies

- ESP32 Development Board  
- Distance Sensor (VL53L0X or VL53L1X)  
- Jumper Wires  
- Breadboard  
- USB Cable  
- Optional: Load Cell + Amplifier  

> **Note:** You can substitute sensors depending on availability.

---

## 🔌 Hardware Setup

1. Connect the sensor to the ESP32:
   - VCC → 3.3V  
   - GND → GND  
   - SDA → GPIO 21  
   - SCL → GPIO 22  

2. Ensure all connections are secure.

3. Power the ESP32 via USB.

---

## 💻 Firmware

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
