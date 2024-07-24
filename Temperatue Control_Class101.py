# Temperatue Control_Class101  on Python
import os.path
import tkinter as tk
from tkinter import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

class Application(tk.Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)

        self.master.geometry("350x400")
        str_prog_name = os.path.basename(__file__) # get present program name
        self.master.title( str_prog_name )  

        # Animation Running Flag 
        self.isRunning = True
        self.dt =1.0                    # interval time (sec)

        #Initial Temperature Model
        self.temp_target  =  40.0       #  °C
        self.temp_present =  30.0       #  °C
        self.temp_ext     =  30.0       # external temperatue °C
        self.v_high_lmt   =  10.0       # V commoand upper limit
        self.v_low_lmt    =   0.0       # V commoand lower limit
        self.alfa_temp    = -0.226      # °C/s.....temperatue 
        self.alfa_pwr     = 0.25/1000   # kJ°C/s...power
        self.epg_pwr_max  = 1000.0      # 1000W Electric Power Generator maximum power
        self.temp_lmt     = 800.0       # 800°C  Temperatue Top value
        self.resist_ht    = 5.0         # heater resistance(ohm)

        #Initial Cntl Command
        self.v_cmd = 0.00
        self.e  = 0.00
        self.e_pre = 0.00
        self.ie = 0.00
        self.Kp = 5.0
        self.Ki = 0.01
        self.Kd = 0.0
        self.diff_init_flag = True          # Flag to avoid discrete differential

        # Frame4
        frame4 = tk.Frame(root, bd=2, relief=RAISED, pady=5, padx=5)
        frame4.pack(side=tk.RIGHT,expand=True,anchor=tk.NW)

        label_temp = tk.Label(frame4, text='Temp_target(°C)')
        label_temp.grid(row=0, column=0, padx=5, pady=5)
        self.en_temp = tk.Entry(frame4, width=10, justify='center')
        self.en_temp.grid(row=0, column=1, padx=5, pady=5)
        self.en_temp.insert(tk.END, str(40))
        label_temp = tk.Label(frame4, text='d-time(s))')
        label_temp.grid(row=1, column=0, padx=5, pady=5)
        self.en_dt = tk.Entry(frame4, width=10, justify='center')
        self.en_dt.grid(row=1, column=1, padx=5, pady=5)
        self.en_dt.insert(tk.END, str(1))   

        label_kp = tk.Label(frame4, text='Kp')
        label_kp.grid(row=2, column=0, padx=5, pady=5)
        self.en_kp = tk.Entry(frame4, width=10, justify='center')
        self.en_kp.grid(row=2, column=1, padx=5, pady=5)
        self.en_kp.insert(tk.END, str(5))  
        label_ki = tk.Label(frame4, text='Ki')
        label_ki.grid(row=3, column=0, padx=5, pady=5)
        self.en_ki = tk.Entry(frame4, width=10, justify='center')
        self.en_ki.grid(row=3, column=1, padx=5, pady=5)
        self.en_ki.insert(tk.END, str(0.01))
        label_kd = tk.Label(frame4, text='Kd')
        label_kd.grid(row=4, column=0, padx=5, pady=5)
        self.en_kd = tk.Entry(frame4, width=10, justify='center')
        self.en_kd.grid(row=4, column=1, padx=5, pady=5)
        self.en_kd.insert(tk.END, str(0.0))

        button_hys = tk.Button(frame4, text='Simulation Start', command=self.Plot_Framework, width=15, height=2)
        button_hys.grid(row=10, column=0, padx=5, pady=5)

    # Plot main Framework
    def Plot_Framework(self):

        # set value
        self.temp_target = float(self.en_temp.get())
        self.dt = float(self.en_dt.get())
        self.Kp = float(self.en_kp.get())
        self.Ki = float(self.en_ki.get())
        self.Kd = float(self.en_kd.get())

        # step2 Graph Frame
        self.fig = plt.figure(figsize=(12,6))
        self.ax  = plt.axes()

        #  Graph Legend
        self.ax.set_xlabel('Time [$sec$]')
        self.ax.set_ylabel('Temperature [$°C$]')
        Label_1 = 'Temp_target'
        Label_2 = 'Temp_present'
        Label_3 = 'V_command'

        t_interval = int(self.dt *1000)      # dt(s) -> t_inteval(ms)
        # Set Initial Conditions 
        self.x = [0]
        self.y0 = [0.0]
        self.y1 = [self.temp_target]
        self.y2 = [self.temp_ext]
        self.y3 = [self.v_cmd]
        self.ln1, = plt.plot(self.y0, self.y1, color='C0', linestyle='--', label=Label_1)
        self.ln2, = plt.plot(self.y0, self.y2, color='C1', linestyle='-', label=Label_2)
        self.ln3, = plt.plot(self.y0, self.y3, color='C2', linestyle=':', label=Label_3)
        self.ax.legend()

        # Show button and value  in the View Graph 
        PuaseButton  = self.__CreateButton(0.7, 0.93, 0.10, 0.05, "pause//resume", self.__Pause_Resume)
        #                                 (left_bottom_x, _y, Width, Height, Label, binded Function)
        ResetButton  = self.__CreateButton(0.85, 0.93, 0.10, 0.05, "reset"     , self.__Reset    )
        self.ax.text(0.0, 1.12, "Temp_target(°C)", ha='left', transform=self.ax.transAxes)
        self.ax.text(0.0, 1.07, "Temp_present(°C)", ha='left', transform=self.ax.transAxes)
        self.ax.text(0.0, 1.02, "V_command(V)", ha='left', transform=self.ax.transAxes)
        str_temp_t = [str('{:.1f}'.format(self.temp_target))]
        self.my_text1 = self.ax.text(0.2, 1.12, str_temp_t, ha='right', color='C0', transform=self.ax.transAxes)
        str_temp_p = [str('{:.1f}'.format(self.temp_present))]
        self.my_text2 = self.ax.text(0.2, 1.07, str_temp_p, ha='right', color='C1', transform=self.ax.transAxes)
        str_v_cmd = [str('{:.2f}'.format(self.v_cmd))]
        self.my_text3 = self.ax.text(0.2, 1.02, str_v_cmd, ha='right',color='C2', transform=self.ax.transAxes)

        # Update status
        self.anim = FuncAnimation(self.fig, self.__update, interval=t_interval)
        plt.show()
        return

    def __update(self,__):

        #Temperature Model
        self.Temp_Model()
        #Cntl Command
        self.Cntl_Command()

        #Data update
        self.x.append(self.x[-1] + 1)
        self.y0.append(self.y0[-1]+ self.dt) 
        self.y1.append(self.temp_target)
        self.y2.append(self.temp_present)
        self.y3.append(self.v_cmd)

        # Axis ReScaling
        x_max = np.max(self.y0) *1.1
        x_min = 0
        self.ax.set_xlim(x_min, x_max)
        y_max =np.max([self.y1,self.y2,self.y3]) *1.1
        y_min =np.min([self.y1,self.y2,self.y3]) 
        self.ax.set_ylim(y_min, y_max)

        # line update
        self.ln1.set_data(self.y0, self.y1) 
        self.ln2.set_data(self.y0, self.y2)
        self.ln3.set_data(self.y0, self.y3)
        # text update
        self.my_text1.set_text(str('{:.1f}'.format(self.temp_target)))
        self.my_text2.set_text(str('{:.1f}'.format(self.temp_present)))
        self.my_text3.set_text(str('{:.2f}'.format(self.v_cmd)))
        return
            
    # "Puase/Resume"  If Button clicked, Animation is paused/resumed, and Running Flag is toggled.
    def __Pause_Resume(self, event):
        if self.isRunning:
            self.anim.event_source.stop()
            self.isRunning = not self.isRunning
        else:
            self.anim.event_source.start()
            self.isRunning = not self.isRunning
        return

    # Clicking the "Reset" button will reload the input data.
    def __Reset(self, event):

        self.diff_init_flag = True      # Flag to avoid discrete differential
        Ki_pre = self.Ki
        # set (GUI)panel value
        self.temp_target = float(self.en_temp.get())
        self.dt = float(self.en_dt.get())
        self.Kp = float(self.en_kp.get())
        self.Ki = float(self.en_ki.get())
        self.Kd = float(self.en_kd.get())

        # Initialized state value
        self.Temp_Model() 
        self.v_cmd = 0.00
        self.e  = 0.00
        self.e_pre = 0.00
        #  self.ie(Intrgral Error) calculated from Ki & Ki_pre
        if self.Ki != 0 and Ki_pre != 0:
            self.ie = self.ie/self.Ki * Ki_pre
        return

    # Creat Button on Graph
    def __CreateButton(self, bottomLeftX, bottomLeftY, width, height, label, func):
        box    = self.fig.add_axes([bottomLeftX, bottomLeftY, width, height])   # draw Button frame
        button = Button(box, label)                                             # from matplotlib.widgets import Button
        button.on_clicked(func)                                                 # When button clicked, function is binded.
        return button

    def Temp_Model(self):
        temp_old = self.temp_present
        v_out    = self.v_cmd/self.v_high_lmt * ( ( self.epg_pwr_max * self.resist_ht )**(1/2) )    #Electric Power Supply voltage(V)
        pwr_cmd  = (v_out**(2) )/ self.resist_ht                                                    #Electric Power Supply Power(W)
        temp_slope_0 = self.alfa_temp * ( (self.temp_present- self.temp_ext) / self.temp_lmt)   #Heat dissipation
        temp_slope_1 = self.alfa_pwr  * pwr_cmd                                                 #Heat transfer
        dtemp_dt     = temp_slope_0 + temp_slope_1
        self.temp_present  = temp_old + dtemp_dt * self.dt
        return
        
    def Cntl_Command(self):
        self.e_pre    = self.e

        #  // PID制御の式より、制御入力uを計算
        #   e  = r - y                      #; // 誤差を計算 r:target y:present
        self.e   = self.temp_target - self.temp_present
        #   de = (e - e_pre)/T              #; // 誤差の微分を近似計算
        if self.diff_init_flag == True:     # flag to avoid discrete differential
            self.de = 0
            self.diff_init_flag = not self.diff_init_flag
        else:
            self.de = (self.e - self.e_pre)/self.dt
        #   ie = ie + (e + e_pre)*T/2       #; // 誤差の積分を近似計算
        self.ie = self.ie + (self.e + self.e_pre)*self.dt/2
        # u  = KP*e + KI*ie + KD*de       #; // PID制御の式にそれぞれを代入
        self.v_cmd  =  self.Kp * self.e + self.Ki * self.ie + self.Kd * self.de
        # V commamd limit
        if self.v_cmd > self.v_high_lmt:
            self.v_cmd = self.v_high_lmt
        if self.v_cmd < self.v_low_lmt:
            self.v_cmd = self.v_low_lmt
        return

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()