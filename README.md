## Temperature_Cntl_class 101
This version is that step response model to make PID constants.

## Temperature_Cntl_class201 
#### Temperature model 
Temperature model ......  (Input:) This method is model, but you will need replace your system sensor.
  - Heat Transfer
  - Heat dissipation 

#### Power Supply Model 
Asuumed Power Supply Model ...... (Output:)T his Controll method is model, but You will need replace PID constant according to your system.
  - Vin = 0-10V
  - Power=1000W Max
  - Load Resistance(Heater) = 5Ω
  - Vout= 0-50√2(V)...max 80(V)

#### Temperature Control and Phase Control
Read temperature-time profile in csv file, and control with PID. It has several modes. 
  1. Pause/Resume.
  2. Skip to forward phase.
  3. Move to backword Phase.
  4. Forced manual temperature control.
