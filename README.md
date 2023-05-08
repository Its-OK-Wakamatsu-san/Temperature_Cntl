### Temperature_Cntl_class 101
This version is that  Step response model for primitive study of PID control.

### Temperature_Cntl_class201 (PID,EPS)
Temperature model ......  
  - Heat Transfer
  - Heat dissipation 

Asuumed Power Supply Model ...... 
  - Vin = 0-10V
  - Power=1000W Max
  - Load Resistance(Heater) = 5Ω
  - Vout= 0-50√2(V)...max 80(V)
<p>
Read time dependent target temperature profile in csv file and control with PID. It has several modes. It is,<p>

  1. Pause/Resume.
  2. Skip to forward phase.
  3. Move to backword Phase.
  4. Forced manual temperature control.
