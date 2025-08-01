## Temperature_Cntl_class 101
This version is that step response model to set PID constants.

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
<p>
<img width="350" height="611" alt="image" src="https://github.com/user-attachments/assets/0bb33643-719d-42ef-8be2-8cb774318cb2" /> <p>
Fig.1　Input Window(Temperature_Cntl_class201)
<p>
  <img width="484" height="354" alt="image" src="https://github.com/user-attachments/assets/1592ab46-93da-43bb-9a96-8ee677729291" /><p>
Fig.2　Taget Temperature Profile(Temperature_Cntl_class201)
<p>
<img width="972" height="538" alt="image" src="https://github.com/user-attachments/assets/291e470e-3ccf-486d-bda3-391f3a16b04a" /> <p>
Fig.3　Typical Example(Temperature_Cntl_class201)
