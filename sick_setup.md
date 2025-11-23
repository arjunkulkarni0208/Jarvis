# Reference
1. `tm4c123gh6pge.h` header file  
2. `gpio.h` header file  
3. `pwm.h` header file  
4. `timer.h` header file  
5. `uart.h` header file  
6. [SICK DT35-B15551 Datasheet](https://www.sick.com/media/pdf/2/62/362/dataSheet_DT35-B15551_1057651_en.pdf)
7. [SICK DT35 Manual](https://cdn.sick.com/media/docs/3/43/743/operating_instructions_dx35_distance_sensors_en_im0052743.pdf)

# Prerequisites
1. Basics of **C programming language**.  
2. Understanding of all **header files**.  
3. Understanding how the **Timer** works in **TM4C**.  

# Components Used  
- **TM4C MCM**  
- **Arduino NANO**  
- **SICK Shield**  
- **1 P+B Custom Board**  
- **1 LMD Motor**  
- **2 SICK Sensors**  
- **4 O500.GR Baumers**  
- **2 IG32 Motors**  
- **2 Hitwitch Sensors**  

# Steps
1. Write a code using the following header files:  
   - `tm4c123gh6pge.h`  
   - `uart.h`  
   - `gpio.h`  
   - `pwm.h`  
   - `timer.h`  
2. Implement the following **functions**:  
   - `GPIO_Init()`  
   - `UART_Init()`  
   - `PWM_Init()`  
   - `init_peripherals()`  
   - `mode()`  
   - `receive_diameter()`  
   - `shoot_duty_measurement()`  
   - `pass_duty_measurement()`  
   - `obstruct_defense()`  
   - `receive_defense()`  
   - `control_loop()`  
3. Establish **connections** between **TM4C MCM** and other components.  

# Precautions  
1. **Avoid using `while` loops**, as they may cause the code to stop at a particular point.  
   - **Reason:** The code relies on **timers** and the **control loop function** for execution.  
2. Ensure **proper tuning** of the **SICK sensor**.  
3. Apply the correct **formula** to convert **raw data into centimeters (cm)**.

---
## Troubleshooting SICK Sensor: Factory Reset & Voltage Mode Configuration
### Factory Reset: Reset Sensor to Default Settings

If the SICK sensor readings are not accurate or behaving unexpectedly, try resetting it to the factory settings.

#### **Steps to Reset the Sensor:**

1. **Switch off** the supply voltage.
2. **Press and hold** the **Select** pushbutton.
3. **While holding** the Select button, **switch on** the supply voltage.
4. When **all Teach LEDs flash**, **release** the Select pushbutton.  
   ✓ All settings have now been **reset to factory defaults**.

### Configure Output Mode to Voltage in Expert Mode

After performing the reset, configure the sensor to **Voltage Output Mode** using the Expert Mode.

#### **Steps to Change Output to Voltage Mode:**

1. From **Operating Mode only**:  
   Press **Select** and **Set** pushbuttons **simultaneously** for **more than 10 seconds**.  
   → The **LED Q1** lights up and the **LED slow … fast** flashes cyclically according to the previous setting.
   
2. Keep **pressing the pushbuttons** until **LED Q2** lights up.

3. Keep pressing the **Set** pushbutton to cycle through output modes until desired option:

   | Flash Pattern                    | Output Mode          |
   |----------------------------------|----------------------|
   | LED slow … fast flashes **1×**   | 4 … 20 mA            |
   | LED slow … fast flashes **2×**   | 0 … 10 V *(Voltage)* |
   | LED slow … fast flashes **3×**   | Switching output     |

4. To **exit Expert Mode**:
   - Press **Select** and **Set** pushbuttons for **more than 10 seconds**, **or**
   - **Wait 5 minutes** without pressing any pushbuttons.

---



# Code 
Code used in Arduino for Sick data receive and transmit it to the mcm using the custom made Sick shield 
```cpp
#define START 0xAA        // Start byte for UART frame
#define END   0x55        // End byte for UART frame

#define dist0 A0          // Analog pin for first SICK sensor
#define dist1 A4          // Analog pin for second SICK sensor

// Calibration constants (must be defined according to your sensor setup)
float offset_0 = 100.0;  
float offset_1 = 100.0;   
float scale_0  = 800.0;   
float scale_1  = 800.0;   
float base_0   = 0.5;   
float base_1   = 0.5;     

void setup()
{
  Serial.begin(9600);  
}

void loop()
{
  // Read raw analog values from SICK sensors (in voltage mode)
  int adc_0 = analogRead(dist0);  
  int adc_1 = analogRead(dist1);  

  /*
    Convert raw ADC values to distance in meters using the following formula:
    distance = ((adc_value - offset) / scale) + base

    - adc_value: raw ADC reading from analogRead()
    - offset: ADC value corresponding to 0.0 m (sensor deadzone)
    - scale: ADC value change per 1 meter
    - base: calibrated base distance to compensate sensor error
  */
  float distance0_m = ((float)(adc_0 - offset_0) / scale_0) + base_0;
  float distance1_m = ((float)(adc_1 - offset_1) / scale_1) + base_1;

  // Convert distances from meters to centimeters
  float distance0_cm = distance0_m * 100.0;
  float distance1_cm = distance1_m * 100.0;

  // Estimate the diameter of the basketball based on distance readings
  float diameter = 25.0 - (distance0_cm + distance1_cm);

  // Send diameter as raw bytes over UART using a start and end frame
  Serial.write(START);                              
  Serial.write((byte*)&diameter, sizeof(diameter)); // Send float as 4 bytes
  Serial.write(END);                              

  delay(100);  
}

```
---
# SICK DT35 Sensor Calibration Code

This C code is used to calibrate a **SICK DT35** distance sensor operating in **voltage mode** using manually measured ADC counts and corresponding known distances.


```c
#include <stdio.h>

/**
 * Calibrate SICK DT35
 *
 * dead_adc : ADC count in the dead-zone (the one you always input)
 * adc[]    : array of measured ADC counts at known distances
 * dist[]   : array of those true distances (meters)
 * N        : number of samples in adc[]/dist[]
 *
 * Outputs via pointers:
 *   *offset = ADC offset to subtract  (will equal dead_adc)
 *   *scale  = counts per meter
 *   *base   = dead-zone distance in meters
 *
 * Returns 0 on success, –1 on error (e.g. N<2 or singular fit).
 */
int calibrate_dt35(int    dead_adc,
                   int    N,
                   float  adc[],
                   float  dist[],
                   float *offset,
                   float *scale,
                   float *base)
{
    if (N < 2) return -1;

    // 1) Offset is simply the dead-zone ADC
    *offset = (float)dead_adc;

    // 2) Fit dist = a*adc + c  via least squares on all N points
    double sum_x  = 0.0, sum_y  = 0.0;
    double sum_xy = 0.0, sum_x2 = 0.0;
    for (int i = 0; i < N; i++) {
        double x = (double)adc[i];
        double y = (double)dist[i];
        sum_x  += x;
        sum_y  += y;
        sum_xy += x * y;
        sum_x2 += x * x;
    }
    double M     = (double)N;
    double denom = M * sum_x2 - sum_x * sum_x;
    if (denom == 0.0) return -1;

    // a = slope = 1/scale,  c = intercept
    double a = (M * sum_xy - sum_x * sum_y) / denom;
    double c = (sum_y - a * sum_x)     / M;

    // 3) Recover scale and base
    *scale = 1.0f / (float)a;
    // base = c + dead_adc/scale  == c + dead_adc * a
    *base  = (float)(c + (double)dead_adc * a);

    return 0;
}

int main(void) {
    // Suppose you measured at three distances:
    //   dead_adc = 45   (unknown base)
    //   (adc,dist) = (200, 0.30), (600, 0.80), (1000, 1.40)
    int   dead_adc = 45;
    float adc_samples[]  = { 2000, 6000, 11000, 15000 };
    float dist_samples[] = { 1, 3, 5, 7 };
    int   N = sizeof(adc_samples)/sizeof(adc_samples[0]);

    float offset, scale, base;
    if (calibrate_dt35(dead_adc, N, adc_samples, dist_samples,
                       &offset, &scale, &base) == 0)
    {
        printf("Calibration results:\n");
        printf("  offset = %.4f  // ADC counts to subtract\n", offset);
        printf("  scale  = %.4f  // counts per meter\n", scale);
        printf("  base   = %.4f  // dead-zone distance (m)\n", base);
    } else {
        fprintf(stderr, "Calibration failed (insufficient data or singular fit)\n");
    }
    return 0;
}
```
---
# Images 
![SICK shiled](https://github.com/user-attachments/assets/9ef2a0ba-8b64-472f-af15-285d6346a4a7)

![SICK shiled schematic](https://github.com/user-attachments/assets/6bf2e796-7dd8-4426-a01c-d4ee6c2bba9a)
