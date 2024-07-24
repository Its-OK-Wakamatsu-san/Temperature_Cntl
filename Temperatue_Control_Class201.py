#Temperature Controller Demo
import os
import os.path
import sys
import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.ttk import Combobox
from tkinter import scrolledtext
from tkinter import messagebox, filedialog
import numpy as np
from numpy.linalg import solve
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import time

class Application(tk.Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        
        self.master.geometry("450x700")
        str_prog_name = os.path.basename(__file__) # get present program name
        self.master.title( str_prog_name )

        self.ini_dir = os.path.dirname(__file__) # get present program directory # change # 2022/12/21 
        file_name1 = "Temp_coditon.csv" # "
        self.typelist3 = [("Temp_coditon", "*.csv")] 
        self.file_path_Temp = os.path.join (self.ini_dir, file_name1)
        #Output file
        file_name1 = "Output1_data.csv"
        self.typelist1 = [("Output1_data", ".csv"),("Output1 text file", ".txt")] 
        self.ini_dir = os.path.dirname(__file__).replace(os.sep,'/')        # get present program directory
        self.file_path1 = os.path.join(self.ini_dir, file_name1).replace(os.sep,'/')

        # アニメーションの動作/停止状態を示すフラグを立てておく。
        self.isRunning      = True
        self.i_phase        = 0          #Phase
        self.sub_phase_flag = False      #flag in sub_Phase 
        self.manual_input_flag = False      #flag in manual input temperature  
        self.start_flag     = True       #Start flag to prevent another procces generate

        # Initialized
        self.elapsed_t_h = 0.
        self.temp_slope_max  = 600. / 0.1    # 600°C/1hr 0.1
        self.dt =1.0                        # interval time (sec)
        
        # Aqua(透明度20%)⇒(R,G,B, alpha)=(0,1,1,0.2)
        self.aqua = (0,1,1, 0.2)
        # Preset Color
        self.color_green = str('#ccffaa') #緑系統
        self.color_red   = str('#ffaacc') #赤系統
        self.color_gray  = str('#f2f2f2') #背景色

        #Initial Temperature Model
        self.temp_target  =  40.0           #  °C
        self.temp_present =  30.0           #  °C
        self.temp_ext     =  30.0           # external temperatue °C
        self.v_high_lmt   =  10.0           # V commoand upper limit
        self.v_low_lmt    =   0.0           # V commoand lower limit
        self.alfa_temp    = -0.226 * 2       # °C/s.....temperatue 
        self.alfa_pwr     = 0.442/1000*2    # kJ°C/s...power
        self.epg_pwr_max  = 1000.0          # 1000W Electric Power Generator maximum power
        self.temp_lmt     = 800.0           # 800°C  Temperatue Top value
        self.resist_ht    = 5.0             # heater resistance(ohm)

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
        frame4 = tk.Frame(root, bd=2, relief=tk.RAISED, pady=5, padx=5)
        frame4.pack(anchor=tk.NW)

        label_Temp_filename = tk.Label(frame4, text='Set Tempature Conditon file')
        label_Temp_filename.grid(row=0, column=0, padx=5, pady=5)
        self.Temp_filename = tk.Text(frame4,  height=4,width=30, background=self.color_gray)
        self.Temp_filename.grid(row=1, column=0, padx=5, pady=5)
        self.Temp_filename.insert(tk.END, str(self.file_path_Temp))
        btn_assign_file = tk.Button(frame4, text='Assign file', command=self.Assign_file_path,  height=1)
        btn_assign_file.grid(row=2, column=0, padx=5, pady=5)
        btn_Write_text1 = tk.Button(frame4, text='Read Temp file', command=self.Read_Temp_condition, height=2, bg = self.color_green)
        btn_Write_text1.grid(row=3, column=0, padx=5, pady=5)

        btn_Plot = tk.Button(frame4, text='Start', command=self.Plot_Framework, width=12, height=2, bg = self.color_green)
        btn_Plot.grid(row=4, column=0, padx=5, pady=5)

        label_t_interval = tk.Label(frame4, text='dt_time interval (s)')
        label_t_interval.grid(row=8, column=0, padx=5, pady=5)
        self.srt_t_interval = tk.Entry(frame4, width=10, justify='center')
        self.srt_t_interval.grid(row=8, column=1, padx=5, pady=5)
        self.srt_t_interval.insert(tk.END, str(1))

        btn_K_PID = tk.Button(frame4, text='Set Kp,Ki,Kd', command=self.Set_PID_const, height=1)
        btn_K_PID.grid(row=9, column=0, padx=5, pady=5)
        label_Kp = tk.Label(frame4, text='Kp')
        label_Kp.grid(row=10, column=0, padx=5, pady=5)
        self.en_Kp = tk.Entry(frame4, width=10, justify='center')
        self.en_Kp.grid(row=10, column=1, padx=5, pady=5)
        self.en_Kp.insert(tk.END, str(5))
        label_Ki = tk.Label(frame4, text='Ki')
        label_Ki.grid(row=11, column=0, padx=5, pady=5)
        self.en_Ki = tk.Entry(frame4, width=10, justify='center')
        self.en_Ki.grid(row=11, column=1, padx=5, pady=5)
        self.en_Ki.insert(tk.END, str(0.01))
        label_Kd = tk.Label(frame4, text='Kd')
        label_Kd.grid(row=12, column=0, padx=5, pady=5)
        self.en_Kd = tk.Entry(frame4, width=10, justify='center')
        self.en_Kd.grid(row=12, column=1, padx=5, pady=5)
        self.en_Kd.insert(tk.END, str(0.0))

        label_Manual = tk.Label(frame4, text='Manual In Temp(°C)')
        label_Manual.grid(row=15, column=0, padx=5, pady=5)
        self.en_Manual_Temp = tk.Entry(frame4, width=10, justify='center')
        self.en_Manual_Temp.grid(row=15, column=1, padx=5, pady=5)
        self.en_Manual_Temp.insert(tk.END, str(100))

        # Set Output File Path Button
        self.set_output_filepath_btn = tk.Button(frame4, text='Set File Path', command=self.Set_File_path)
        self.set_output_filepath_btn.grid(row=16, column=0, padx=5, pady=5)
        # File output Button
        self.file_output_btn = tk.Button(frame4, text='Output File Button', command=self.__File_Out, height=2, bg = self.color_green)
        self.file_output_btn.grid(row=16, column=1, padx=5, pady=5)

        #ScrolledTextウィジェットを作成
        self.strings = scrolledtext.ScrolledText( frame4, width=40,  height=15 , background=self.color_gray)
        self.strings.grid(row=17, column=0, padx=5, pady=5)

    # Real_Time_Plot but asynchronus
    def Plot_Framework(self):
        if self.start_flag :
            ret = messagebox.askyesno('Reconformation', 'Are you ready for "Temp Cntl"？')
            if ret :
                self.start_flag = not self.start_flag
                pass
            else:
                return
        else:
            return
        
        # print Log
        str_comment =   ' Starts temperature CNTL praogram.' + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール    
        
        #   各種定数設定
        self.unixtime_start=time.time()
        # Read & Set  time inteval  Kp,Ki,Kd
        self.dt = float(self.srt_t_interval.get())
        t_interval = int(self.dt *1000)
        self.Set_PID_const()   

        # Set Initial Conditions 
        self.x = [0]
        self.y0 = [0]
        self.Get_Temp_target()       #Table interpolation
        self.temp_present = self.temp_ext
        self.y1 = [self.temp_target]
        self.y2 = [self.temp_present]
        self.y3 = [self.v_cmd]

        # set Graph Frame
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        
        # set Graph Legend
        self.ax.set_xlabel('Reference Time [$hours$]')
        self.ax.set_ylabel('Temperature [$°C$]')
        Label_0 = 'Set Value'
        Label_1 = 'Present Target Value'
        Label_2 = 'Present Value'
        Label_3 = 'V_command'

        self.ln0, = plt.plot(self.time_tb, self.temp_tb, color='C6', linestyle=':', label=Label_0)
        self.ln1, = plt.plot(self.y0, self.y1, color='C0', linestyle='-', label=Label_1)
        self.ln2, = plt.plot(self.y0, self.y2, color='C1', linestyle='-', label=Label_2)
        self.ln3, = plt.plot(self.y0, self.y3, color='C2', linestyle=':', label=Label_3)
        self.ax.legend()

        # Show buttons and values in the View Graph 
        self.PlayButton  = self.__CreateButton(0.5 , 0.95, 0.15, 0.03, "Hold//Resume", self.__Pause_Resume) # (bottom_left_x, bottom_left_y,Width, Height, Label, binded Function)
        self.FwdButton   = self.__CreateButton(0.7, 0.95, 0.15, 0.03, "Move FWD" , self.Forward_Phase) 
        self.ManualButton = self.__CreateButton(0.3, 0.90, 0.15 , 0.03, "Manual Temp. Input" , self.Manual_Phase ) 
        self.BackButton  = self.__CreateButton(0.5 , 0.90, 0.15 , 0.03, "Move BWD", self.Backward_Phase ) 
        self.BeginButton = self.__CreateButton(0.7, 0.90, 0.18 , 0.03, "Move Beginning Phase" , self.Beginning_Phase ) 
        self.ax.text(-0.1, 1.12, "Temp_target(°C)", ha='left', transform=self.ax.transAxes)
        self.ax.text(-0.1, 1.07, "Temp_present(°C)", ha='left', transform=self.ax.transAxes)
        self.ax.text(-0.1, 1.02, "V_command(V)", ha='left', transform=self.ax.transAxes)
        self.ax.text(0.15, 1.12, "Reference Time(h:m:s))", ha='left', transform=self.ax.transAxes)
        self.str_temp_t = [str('{:.1f}'.format(self.temp_target))]
        self.my_text1 = self.ax.text(0.1, 1.12, self.str_temp_t, ha='right', color='C0', transform=self.ax.transAxes)
        self.str_temp_p = [str('{:.1f}'.format(self.temp_present))]
        self.my_text2 = self.ax.text(0.1, 1.07, self.str_temp_p, ha='right', color='C1', transform=self.ax.transAxes)
        self.str_v_cmd = [str('{:.2f}'.format(self.v_cmd))]
        self.my_text3 = self.ax.text(0.1, 1.02, self.str_v_cmd, ha='right', color='C2', transform=self.ax.transAxes)
        str_elp_time = self.elapsed_time_str( 0 )  # hh:mm:ss形式の文字列で返す
        self.my_text4 = self.ax.text(0.4, 1.12, str_elp_time, ha='right', transform=self.ax.transAxes)

        # Update status
        self.anim = FuncAnimation(self.fig, self.__update, interval=t_interval)
        plt.show()
        return
    
    def __update(self,frame):
        # update time 
        unixtime = time.time()
        elapsed_t   = (unixtime - self.unixtime_start)    #elapsed time(s)
        self.elapsed_t_h = elapsed_t / 3600               #elapsed time(hours)

        #Phase (Check elapsed_time and Terminate when time is over)
        self.Check_Phase()
        #Cntl Command   (Command Voltage) 
        self.Cntl_Command()
        #Temperature Model Present Temperature
        self.Temp_Model()

        # update status
        self.x.append(self.x[-1] + 1)
        self.y0.append(self.elapsed_t_h)
        self.Get_Temp_target()       #Table interpolation Target Temperature
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
    
        self.ln1.set_data(self.y0, self.y1)
        self.ln2.set_data(self.y0, self.y2) 
        self.ln3.set_data(self.y0, self.y3) 

        # update status text
        self.my_text1.set_text(str('{:.1f}'.format(self.temp_target)))
        self.my_text2.set_text(str('{:.1f}'.format(self.temp_present)))
        self.my_text3.set_text(str('{:.2f}'.format(self.v_cmd)))
        str_elp_time = self.elapsed_time_str(elapsed_t)  # hh:mm:ss形式の文字列で返す
        self.my_text4.set_text(str_elp_time)
        return

    # "Puase//Resume"  If Button clicked, Animation is paused and resumed, and Running Flag is toggled.
    def __Pause_Resume(self,event):
        if self.manual_input_flag  :
            ret = messagebox.askyesno('Reconformation', 'Reset Manual Input!')
            return
        if self.isRunning:
            #self.anim.event_source.stop()
            self.isRunning = not self.isRunning
            self.pause_start_t = time.time()
            self.PlayButton.ax.set_facecolor(self.color_red)
            self.PlayButton.color = self.color_red
            str_comment =   " Pause button was pushed. " + '\n'
            self.strings.insert (tk.END, str_comment)
            self.strings.see('end')     #自動で最新までスクロール
        else:
            #self.anim.event_source.start()
            self.isRunning = not self.isRunning
            pause_stop_t = time.time()
            self.PlayButton.ax.set_facecolor(self.color_gray)
            self.PlayButton.color = self.color_gray
            wait_t = pause_stop_t - self.pause_start_t          #waiting time
            self.unixtime_start = self.unixtime_start + wait_t  #corrected time by the waiting time
            str_comment =   " Resume button was pushed. " + '\n'
            self.strings.insert (tk.END, str_comment)
            self.strings.see('end')     #自動で最新までスクロール
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
           
    #Assign Magnetic Flux Density condition file    # 2022/12/21  add　 function
    def Assign_file_path(self):
        filename = tk.filedialog.askopenfilename(initialdir=self.ini_dir, filetypes=self.typelist3, title="Load", defaultextension = "")
        if filename == "":
            return
        self.file_path_Temp = filename
        self.Temp_filename.delete('1.0','end')                    # Delete "Temp_filename" all
        self.Temp_filename.insert(tk.END, self.file_path_Temp)    # insert new "Temp_filename" 
        #print('Set Temperature condition file_path =' , self.file_path_Temp)
        str_comment =  " Assigned Temperature profile file path = " + os.path.abspath(self.file_path_Temp) + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール
        return
    
    def __File_Out(self):
        # Header
        str_prog_name = os.path.basename(__file__) # get present program name
        str_time      = str(datetime.datetime.now())
        str_row0   = "  ,  "+ str_prog_name + "  ,  " + str_time
        str_row1   = "blanc"
        str_row2   = " number ,  reference time(hr), temp_target(°C) , temp_present(°C) , V_command(V)"
        str_header = str_row0 + " \n "+ str_row1 + " \n " + str_row2  # \n 改行
        # Data
        array_x  = np.array( self.x )       # number
        array_y0 = np.array( self.y0 )      # elapsed time(hr)
        array_y1 = np.array( self.y1 )      # temp_target
        array_y2 = np.array( self.y2 )      # temp_present
        array_y3 = np.array( self.y3 )      # v_command
        # Data  stack
        array_2 = np.column_stack(( array_x , array_y0, array_y1 ,array_y2 ,array_y3 ))
        #print(array_2)

        # CSV file Out put
        np.savetxt( self.file_path1 , array_2 , delimiter=',', header=str_header, comments='#', fmt='%.6e')
        # print Log   
        str_def_Func = sys._getframe().f_code.co_name           #Function name get
        #print(  " def ", str_def_Func , " was finished " )    
        str_comment =   " def " + str_def_Func + " was finished "  +'\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール
        return
    
    def Set_File_path(self):
        #20221108 add defaultextension = ""  ....「ファイルの種類」で指定された拡張子で、自動で拡張子が付加されます
        filename=filedialog.asksaveasfilename(initialdir=self.ini_dir, filetypes=self.typelist1, title="Set Output File path", defaultextension = "")
        if filename == "":
            return
        else:
            self.file_path1 = filename
            self.f_root, self.ext = os.path.splitext(self.file_path1)
            self.ini_dir = self.f_root
            #print('Set Output File path =' , os.path.abspath(self.file_path1))
            str_comment =   ' Set Output File path =' + os.path.abspath(self.file_path1)  + '\n'
            self.strings.insert (tk.END, str_comment)
            self.strings.see('end')     #自動で最新までスクロール
            return

    def Read_Temp_condition(self):
        col0 = np.loadtxt(self.file_path_Temp, delimiter=',',usecols=0)
        col1 = np.loadtxt(self.file_path_Temp, delimiter=',',usecols=1)
        self.time_tb = col0
        self.temp_tb = col1
        print(self.time_tb)
        print(self.temp_tb)
        self.i_phase_max = len(col0)-1
        
        # print Log      
        str_comment =  " Read Temperature profile = " + os.path.abspath(self.file_path_Temp) + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール

        # set graph frame
        fig, ax = plt.subplots(figsize=(6, 3))
        plt.title('Input Table Preview')
        # set graph Legend
        ax.set_xlabel('Reference Time [$hours$]')
        ax.set_ylabel('Temperature [$°C$]')
        Label_1 = 'Set Value'
        ln1, = plt.plot(self.time_tb, self.temp_tb, color='C6', linestyle=':', label=Label_1)
        ax.legend()
        plt.show()
        return
    
    def elapsed_time_str(self,seconds):
        """時間をhh:mm:ss形式の文字列で返す
        """
        seconds = int(seconds + 0.5)    # 秒数を四捨五入
        h = seconds // 3600             # 時の取得
        m = (seconds - h * 3600) // 60  # 分の取得
        s = seconds - h * 3600 - m * 60 # 秒の取得
        return f"{h:02}:{m:02}:{s:02}"  # hh:mm:ss形式の文字列で返す
    
    def Check_Phase(self):
        self.elapsed_t_h
        for i in range(self.i_phase_max) :
            if self.elapsed_t_h > self.time_tb[i]:
               self.i_phase = i 
        if self.elapsed_t_h > self.time_tb[self.i_phase_max]:
            self.v_cmd =0.0
            sys.exit(0)
        return
    
    def Forward_Phase(self,event):
        ret = messagebox.askyesno('Reconformation', 'Move to "Forward Phase"？')
        if ret :
            pass
        else:
            return
        self.i_phase += 1
        if self.i_phase >= self.i_phase_max:
            ret = messagebox.askyesno('Reconformation', 'you want to terminate？')   
            if ret :
                self.v_cmd =0.0
                sys.exit(0)
            else:
                return
        # Search Intersection and Reset time.
        self.Search_Intersection() 
        # print Log
        str_comment =   ' Pushed Forward Phase button.' + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール
        return
    
    def Backward_Phase(self,event):
        ret = messagebox.askyesno('Reconformation', 'Move to "Backward Phase"？')
        if ret :
            pass
        else:
            return
        self.i_phase -= 1
        if self.i_phase < 0:
            self.i_phase = 0                                                # Start over Phase0
        # Search Intersection and Reset time.
        self.Search_Intersection() 
        # print Log
        str_comment =   ' Pushed Backward Phase button.' + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール
        return
    
    def Beginning_Phase(self,event):
        ret = messagebox.askyesno('Reconformation', 'Move to "beginning of this Phase"？')
        if ret :
            pass
        else:
            return
        # Search Intersection and Reset time.
        self.Search_Intersection() 
        # print Log
        str_comment =   ' Pushed Beginning of this Phase button.' + '\n'
        self.strings.insert (tk.END, str_comment)
        self.strings.see('end')     #自動で最新までスクロール
        return
    
    def Manual_Phase(self,event):
        ret = messagebox.askyesno('Reconformation', 'Move to Manual Temperasture Input"？')
        if ret :
            pass
        else:
            return
        
        if self.isRunning == False :
            ret = messagebox.askyesno('Reconformation', 'Reset Hold!')
            return
        
        if self.manual_input_flag == False:
            self.manual_input_flag = True
            #self.pause_start_t = time.time()
            self.ManualButton.ax.set_facecolor(self.color_red)
            self.ManualButton.color = self.color_red          
            # print Log
            str_comment =   ' Now Manual input temperature Phase. Input Temp. is ' + self.en_Manual_Temp.get() + '(°C).' + ' \n'
            self.strings.insert (tk.END, str_comment)
            self.strings.see('end')     #自動で最新までスクロール  
        else:
            self.manual_input_flag = False
            self.Search_Intersection() 
            #pause_stop_t = time.time()
            self.ManualButton.ax.set_facecolor(self.color_gray)
            self.ManualButton.color = self.color_gray 
            #wait_t = pause_stop_t - self.pause_start_t          #waiting time
            #self.unixtime_start = self.unixtime_start + wait_t  #corrected time by the waiting time# Search Intersection and Reset time.
            # print Log
            str_comment =   ' Exit Manual input temperature Phase.' + '\n'
            self.strings.insert (tk.END, str_comment)
            self.strings.see('end')     #自動で最新までスクロール     
        return
              
    def Search_Intersection(self):                                 
        temp_present = self.temp_present
        diff_temp_0 = temp_present - self.temp_tb[self.i_phase]
        diff_temp_1 = temp_present - self.temp_tb[self.i_phase+1]
        multi_0_1   = diff_temp_0 * diff_temp_1

        # y - y0 = dy/dx(x - x0)
        dy_dx  = (self.temp_tb[self.i_phase+1]-self.temp_tb[self.i_phase]) / (self.time_tb[self.i_phase+1]-self.time_tb[self.i_phase])
        y0     = self.temp_tb[self.i_phase]
        x0     = self.time_tb[self.i_phase]
        c      = dy_dx * x0 - y0

        if multi_0_1 < 0 :                  #have a cross point
            self.sub_phase_flag = False
            interpol= 1
            # y = temp_present
            left   = [[dy_dx, -1], [0, 1]]
            right  = [c, temp_present]
            [x_crs,y_crs] = solve(left, right)
            time_restart         = x_crs

        else:                               #without cross point
            self.sub_phase_flag = True
            # y - y0 = dy/dx(x - x0)
            dy_dx_A  = -self.temp_slope_max #decrease 
            y0_A     = temp_present
            x0_A     = self.time_tb[self.i_phase]
            c_A      = dy_dx_A * x0_A - y0_A
            
            if   diff_temp_0 > 0 :          #decrease
                #decrease
                interpol= 2
                pass

            elif diff_temp_0 < 0 :          #increase
                #increase 
                interpol= 3
                # y - y0 = dy/dx(x - x0)
                dy_dx_A  = self.temp_slope_max
                c_A      = dy_dx_A * x0_A - y0_A
    
            left_A   = [[dy_dx, -1], [dy_dx_A, -1]]
            right_A  = [c, c_A]
            [x_crsA,y_crsA] = solve(left_A, right_A)
            self.temp_sub_phase  = [y0_A, y_crsA]
            self.time_sub_phase  = [x0_A, x_crsA]
            time_restart         = self.time_tb[self.i_phase]

        diff_time = (self.elapsed_t_h - time_restart)*3600                  # difference time 
        self.unixtime_start = self.unixtime_start + diff_time               # corrected "unixtime_start" by diff_time
        self.elapsed_t_h  = ( time.time() - self.unixtime_start ) /3600.
        return
    
    # Creat Button on Graph
    def __CreateButton(self, bottomLeftX, bottomLeftY, width, height, label, func):
        box    = self.fig.add_axes([bottomLeftX, bottomLeftY, width, height])   # draw Button frame
        button = Button(box, label)                                             # from matplotlib.widgets import Button
        button.on_clicked(func)                                                 # When button clicked, function is binded.
        return button
    
    def Get_Temp_target(self):
        if self.manual_input_flag == True :
            self.temp_target =  float(self.en_Manual_Temp.get())    # sub_phase interpolation
            return
        if self.isRunning == False :
            return
        if self.sub_phase_flag == True :
            if self.elapsed_t_h < self.time_sub_phase[1]:
                self.temp_target = np.interp(self.elapsed_t_h, self.time_sub_phase, self.temp_sub_phase)    # sub_phase interpolation
                return
            else:
                self.sub_phase_flag = False
        self.temp_target = np.interp(self.elapsed_t_h, self.time_tb, self.temp_tb)      #Table interpolation
        return
    
    def Temp_Model(self):
        temp_old = self.temp_present
        v_out    = self.v_cmd/self.v_high_lmt * ( ( self.epg_pwr_max * self.resist_ht )**(1/2) )    #EPG voltage(V)
        pwr_cmd  = (v_out**(2) )/ self.resist_ht                                                    #EPG Power(W)
        temp_slope_0 = self.alfa_temp * ( (self.temp_present- self.temp_ext) / self.temp_lmt)   #Heat dissipation
        temp_slope_1 = self.alfa_pwr  * pwr_cmd                                                 #Heat transfer
        dtemp_dt     = temp_slope_0 + temp_slope_1
        self.temp_present  = temp_old + dtemp_dt * self.dt
        return
        
    def Cntl_Command(self):
        self.e_pre    = self.e

        #  // PID制御の式より、制御入力uを計算
        '''
        e  : error
        Kp : （P) Constant
        Ki : （I) Constant
        Kd : （D) Constant 
        '''
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
    
    def Set_PID_const(self):
        self.Kp = float(self.en_Kp.get())
        self.Ki = float(self.en_Ki.get())
        self.Kd = float(self.en_Kd.get())
        return

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
