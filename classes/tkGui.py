import os
import math
import matplotlib.pyplot as plt  # for displaying math 
import tkinter as tk    # for the gui
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter import *
from tkinter import filedialog as fd
import pandas as pd
import numpy as np
from classes.Excellerator2 import Excellerator2
from classes.Simulator import Simulator
import time


class tkGui(tk.Tk):

    def __init__(self):
        super().__init__()  #the super is a bit unnecessary, as there is nothing to inherit... but leaving it here for reference. 
        self.debug_level_default = 0
        #initial gui settings and layout
        self.geometry("650x740")
        self.title("Slot Simulator")
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)

        # default text/value entries
        #self.bet = StringVar(self, value = "0.50")  ## set this as a string in order to get a decimal.
        self.bet = StringVar(self, value = "0.01")  ## set this as a string in order to get a decimal.
        self.slot_ready = False
        self.infinite_checked = BooleanVar(self, value=False)
        #self.mechreel_checked = BooleanVar(self, value=True)
        # .. simulator settings: 
        self.initial_credits = IntVar(self, value = 100)
        self.machine_credits = IntVar(self, value = 0)
        self.simruns = IntVar(self, value = 500)
        self.input_filepath = StringVar(self, value = "./assets/GameFitStrategy.xlsx") 
        self.sim_output_filepath = StringVar(self, value = "./assets/simdata.csv")
        self.math_output_filepath = StringVar(self, value = "./assets/mathdata.csv")
        self.payline_number = IntVar(self, value = 0)
        self.payline_totalbet = DoubleVar(self, value = 0 )
        self.status_box = StringVar(self, value = "[Select Input File at 1., or/then Click 2.]")
        self.start_time = 0
        self.end_time = 0
        # simulator spins/credits data
        self.df = pd.DataFrame()
        # debug level, a gui element to decide if we want extra output. 
        self.debug_level = IntVar(self, value = self.debug_level_default)
        # dictionary with math, next? 
        self.hit_total = IntVar(self, value = 0)
        self.hit_freq = IntVar(self, value = 0)
        self.max_liability = IntVar(self, value = 0)        
        self.volatility = DoubleVar(self, value = 0)
        self.return_to_player = DoubleVar(self, value = 0)
        self.found_volatility = DoubleVar(self, value = 0)
        self.found_return_to_player = DoubleVar(self, value = 0)
        self.bonus_hit_percentage = DoubleVar(self, value = 0)
        self.bonus_hit_count = DoubleVar(self, value = 0)
        self.confidence_interval = 1.65 # 90% confidence
        #self.confidence_interval = 1.96 # 95% confidence 
        #self.confidence_interval = 2.58 # 99% confidence       
        self.plot_toggle = 0
        # finally for init, create the gui itself, calling the function
        self.create_gui()

    #output buttons - decided to make them separate in case we want to do different things with them
    ##### currently broken.. when using .get() .. meaning it's breaking out of the text box string format...
    def input_filepath_dialog_button(self): 
        #clear out the old entries, then reset. 
        if(self.debug_level.get() >= 1):
            print(f"    input was {self.input_filepath.get()}")  
        # examples of how to clear the box. created unnecessary issues with reading the file. 
        #self.input_filepath.set("")
        #self.input_file_entry.select_clear()     
        the_input = fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("excel files","*.xlsx"), ("all files","*.*")) )
        while(the_input == ''):
            print(f"WARNING: An .xslx input file, properly formatted, is required.")
            the_input = fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("excel files","*.xlsx"), ("all files","*.*")) )
        self.input_filepath.set(the_input)
        if(self.debug_level.get() >= 2):
            print(f"        input is {self.input_filepath.get()}")
        self.input_file_entry.textvariable=self.input_filepath.get()
        if(self.debug_level.get() >= 3):
            print(f"            and the entry is {self.input_file_entry.get()}")

    def sim_output_filepath_dialog_button(self): 
        self.sim_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        if(self.debug_level.get() >= 1):
            print(f"    ouput filepath is {self.sim_output_filepath}")       
        self.sim_output_file_entry.textvariable=self.sim_output_filepath.get()

    def math_output_filepath_dialog_button(self): 
        self.math_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        if(self.debug_level/get() >= 1):
            print(f"    math output file is {self.math_output_filepath}")
        self.math_output_file_entry.textvariable=self.math_output_filepath.get()

    def sim_output_save_file(self):
        #header = ['spin','credits']
        #print(data)
        # if file does not exist, create first.. then append
        #print(self.sim_output_filepath.get())
        if(os.path.exists(str(self.sim_output_filepath)) == False):
            with open(str(self.sim_output_filepath.get()), 'w') as fp:
                fp.close()
        self.df.to_csv(str(self.sim_output_filepath.get()), index=False, header=False)
        if(self.debug_level.get() >= 0):
            print(f"    Sim Output Saving... {str(self.sim_output_filepath.get())}")

    #currently unused
    def math_output_save_file(self):
        #data = self.df #### this will be a different data set.....
        #print(data)
        # if file does not exist, create first.. then append
        #print(str(self.math_output_filepath.get()))
        if(os.path.exists(str(self.math_output_filepath)) == False):
            with open(str(self.math_output_filepath.get()), 'w') as fp:
                fp.close()
        self.df.to_csv(str(self.math_output_filepath.get()))
        if(self.debug_level.get() >= 1):
            print(f"    Math Output File Saving... {str(self.math_output_filepath.get())}")

    # a quick and dirty reset button; currently unused because its logic was wonky
    def refill_button_clicked(self):
        self.status_box.set(f"[3a. Slot Credits Refilled, ready to rerun Simulation]")
        #reset defaults, from Slot Machine initialization
        self.sm.game_credits = 0
        self.sm.incremental_rtp = []
        self.sm.incremental_credits = []
        self.sm.adjust_credits(int(self.sm.initial_credits))
        self.machine_credits.set(self.sm.return_credits())

    #### This is where the magic happens in the GUI, part 1 ####
    def build_slot_button(self):
        # use the current values
        input_filepath = self.input_filepath.get() #this didnt like .get()
        #print(f" after build slot, input filepath clicked is: {input_filepath}")
        bet = float(self.bet_entry.get())
        initial_credits = self.credit_entry.get()
        if(self.debug_level.get() >= 3):
            print(f"            Slot Machine geting passed: {input_filepath}, {bet}, {initial_credits}, {self.debug_level.get()} and inf checked? {self.infinite_checked.get()}")
        #self.sm = SlotMachine(input_filepath, bet, initial_credits, self.debug_level.get(), self.infinite_checked.get())
        # the slot machine constructor - even though it uses new algorithms, may as well keep the instance name, as it's littered through the code. 
        self.sm = Excellerator2(input_filepath, bet, initial_credits, self.debug_level.get(), self.infinite_checked.get())
        self.slot_ready = True
        self.status_box.set("[2. Slot Built - Credits Loaded]")
        self.payline_number.set(self.sm.paylines)
        self.bet.set(self.sm.bet_per_line)
        self.payline_totalbet.set("{:.2f}".format(int(self.payline_number.get()) * float(self.bet_entry.get())))
        self.machine_credits.set(self.sm.return_credits())
        # a gui checkbox to show it was done? in the build column in slot 0?

    #### This is where the magic happens in the GUI, part 2 ####
    def sim_button_clicked(self):
        #start simulation here...
        #print("buttonpress")
        self.status_box.set("[Run Simulator Button Pressed, Running.]")        
        if(self.slot_ready == True):
            self.start_time = time.time()
            self.sim = Simulator(self.sm, self.simruns.get(), self.debug_level.get())   # simulator call 
            self.df = pd.DataFrame(self.sim.win_list)   #, columns=['Credits'])  # pull the saved simulator dat
            # set the machine credits after each run
            self.machine_credits.set(self.sm.return_credits())
            # most of the math scattered through this function has been moved
            self.do_the_math()
            self.status_box.set("[3. Done - Click 2 to Rebuild Slot, or Reload Credits]") # setting status 
        else:
            self.status_box.set("[->2. Click 2 to Build or reload]")
            #print("->1. Slot needs to be loaded first.")
        # this is how to keep the #'s from running out of control between spins'
        self.sm.hit_total = 0

    def plot_cred_button_clicked(self):
        self.sim.plot_credits_result()

    def plot_rtp_button_clicked(self):
        self.sim.plot_rtp_result()

    def do_the_math(self):
        """ Moving the math here - this fills out the bottom portion of the gui after play"""
        ######math goes here for output
        if(self.debug_level.get() >= 2):
            print(f"        hit info for math, total hits {self.sm.hit_total} and simulator runs: {self.simruns.get()}")
        hfe = ( self.sm.hit_total / self.simruns.get() ) * 100 
        self.hit_freq.set(str(round(hfe, 2))+"%")
        ml = self.sm.maximum_liability
        self.max_liability.set("$"+str(round(ml, 2)))
        
        #### volatility goes here. ### 
        #if(self.debug_level.get() >= 1):
            #print(f"    ^^^^ the volatility math: {self.sm.summation} / {self.simruns.get() * (len(self.sm.paytable) + 1)} = {self.sm.summation/(self.simruns.get() * (len(self.sm.paytable) + 1))}.. sqrt is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) ))}, and so with * 1.96 the volatility index is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) )) * 1.96} ")
            #print(f"    ^^^^ the volatility math: {self.sm.summation} / {self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1)} = {self.sm.summation/(self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1))}.. sqrt is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1) ))}, and so with * 1.96 the volatility index is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1) )) * 1.96} ")
            #print(f"    ^^^^ the volatility math: {self.sm.summation} / {self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1)} = {self.sm.summation/(self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1))}.. sqrt is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1) ))}, and so with * 1.96 the volatility index is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1)-1 + 1) )) * 1.96} ")
        #volatilitymath = math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) ) ) * 1.96   #()
        #volatilitymath = math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1) ) ) ) * self.confidence_interval   #(removed the +1 required by the function, as the length inclides the zero line, an additional 1
        ##### this section is where we are refining the math. 
        ## self.sim.spins instead of simruns, lines_sheet1 is no longer necessarily the paylines total because changes
        #volatilitymath = math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.lines_sheet1) ) ) ) * self.confidence_interval   #(removed the +1 required by the function, as the length inclides the zero line, an additional 1
        # above is the old way
        # below is the new way
        if(self.debug_level.get() >= 2):
            print(f"    ^^^^ the volatility math: summation {self.sm.summation} / {float(self.sim.spins[-1]) * self.payline_totalbet.get()} = {self.sm.summation / (float(self.sim.spins[-1]) * self.payline_totalbet.get())}")
            print(f"    .. sqrt times confidence interval is {math.sqrt( self.sm.summation / (float(self.sim.spins[-1]) * self.payline_totalbet.get()) ) * self.confidence_interval} ")
        # volatility is Standard Deviation * the Confidence Interval. Std Dev is the square root of the variance. variance is summation / coin-in
        # weighted mean is in the excellerator, used to compute Sum of Squares "summation"
        # summation defined elsewhere - in the slot machine excellerator, with the line: self.summation += (self.round_win - self.mean_pay) ** 2 
        coinin = self.sm.total_bet * 100    # times 100 because the machine keeps track in dollars and cents. the calculation is in cents
        coinout = self.sm.total_won * 100 
        #print(f"-- coins in: {coinin} out: {coinout}")
        #https://www.investopedia.com/terms/v/variance.asp
        #variance = math.sqrt( self.sm.summation / float(self.sim.spins[-1]) )      # from the math pages, cited. 
        variance = abs( ( self.sm.summation - (coinout **2 / coinin) ) / coinin ) # Scott's adjusted formula
        # absolute number is required, because sqrt of negs throws errors. 
        stddev = math.sqrt(variance)
        # https://www.investopedia.com/terms/v/volatility.asp
        volatility = stddev * self.confidence_interval
        if(self.debug_level.get() >= 1):
            print(f"    #InDev# Volatility calculation variables\n    -- coins in: {coinin} out: {coinout} summation: {self.sm.summation} variance: {variance} stddev: {stddev} volatility: {volatility}")
        #volatilitymath = math.sqrt( self.sm.summation / (float(self.sim.spins[-1]) * self.payline_totalbet.get()) ) * self.confidence_interval   #(removed the +1 required by the function, as the length inclides the zero line, an additional 1
        #volatilitymath = math.sqrt( self.sm.summation - (self.sm.total_won ** 2 / self.sm.total_bet) / self.sm.total_bet ) * self.confidence_interval        
        #volatilitymath = math.sqrt( self.sm.summation - (self.sm.total_won ** 2 / self.sm.total_bet) / self.sm.total_bet ) * self.confidence_interval                
#        self.volatility.set(round(volatilitymath, 2))
        self.volatility.set(round(volatility, 2))
        #found volatility from the spreadsheet
        try:
            self.found_volatility.set(round(self.sm.vi, 2))
        except NameError:
            self.found_volatility.set("N/A")

        # RTP
        if(self.debug_level.get() >= 1):
            print(f"    $$$$ RTP is {self.sm.total_won} / {self.sm.total_bet} = {(self.sm.total_won / self.sm.total_bet)} ")
        self.return_to_player.set("{:.2f}".format(self.sm.total_won / self.sm.total_bet * 100)+"%")
        # found rtp from the spreadsheet
        try:
            self.found_return_to_player.set( str(round(self.sm.rtp, 2) ) + "%" ) 
        except NameError:
            self.found_return_to_player.set("N/A")

        # finally, record / print our final values as a status
        if(self.debug_level.get() >= 1):
            print(f"Final values, at spin {self.sim.spins[len(self.sim.spins)-1]}, the final credit value was {self.sim.incremental_credits[len(self.sim.incremental_credits)-1]}" )
        self.end_time = time.time()
        run_time = np.round(self.end_time - self.start_time, 2) 
        mrt = np.round(run_time / 60 , 2) 
        bhp = np.round(self.sm.bonus_hit_count / self.sim.spins[len(self.sim.spins)-1], 4) 
        self.hit_total.set(self.sm.hit_total)
        self.bonus_hit_count.set( str(self.sm.bonus_hit_count) )
        self.bonus_hit_percentage.set( str(bhp) + "%")
        # end of the simulation procedure
        print(f"Simulation Complete, total run time in seconds: {run_time}, or approximately {mrt} minutes, played {self.sim.spins[-1]} spins.")

    def create_gui(self):
        # UI element values
        gui_row_iteration = 0
        #self.input_filepath = StringVar(self, value = '/Users/jdyer/Documents/GitHub/JD-Programming-examples/Python/math_slot_simulator/PARishSheets.xlsx')
        self.label_plot = tk.Label(self, text="1. Select Input File ")
        self.label_plot.grid(row = gui_row_iteration, column = 0, columnspan = 3, sticky=W, padx=15, pady=5)
        gui_row_iteration += 1
        self.input_label_filepath = tk.Label(self, text="Input Filepath ")
        self.input_label_filepath.grid(row = gui_row_iteration, column = 0, sticky=E)
        #self.label_filepath.pack( side = LEFT)
        self.input_file_entry = ttk.Entry(self, textvariable = self.input_filepath, text=self.input_filepath)
        #self.input_file_entry.insert(0,self.input_filepath)
        self.input_file_entry.grid(row = gui_row_iteration, column = 1, columnspan = 2)
        self.file_button = tk.Button(self, text="1. ...", command = self.input_filepath_dialog_button)
        self.file_button['command'] = self.input_filepath_dialog_button
        self.file_button.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        
        #simulator settings entries
        self.label_debug = tk.Label(self, text="Debug Level: 0 (Silent) through 3 (Verbose) ")
        self.label_debug.grid(row = gui_row_iteration, column = 0, columnspan=3, sticky=E)
        self.debug_entry = ttk.Entry(self, width = 8, textvariable = self.debug_level)
        self.debug_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        #gui_row_iteration += 1
        self.label_cred = tk.Label(self, width = 14, text="Starting Dollars ")
        self.label_cred.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.credit_entry = ttk.Entry(self, width = 8, textvariable = self.initial_credits)
        self.credit_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        #self.label_mechreel = tk.Label(self, text="Mechanical Style Slots: ")
        #self.label_mechreel.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        #self.mechreel_checkbox = ttk.Checkbutton(self, variable = self.mechreel_checked, onvalue = True, offvalue = False)
        #self.mechreel_checkbox.grid(row = gui_row_iteration, column = 2)        
        #gui_row_iteration += 1
        self.label_machine_credits = tk.Label(self, text="Machine Credits: ")
        self.label_machine_credits.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.machine_credit_entry = ttk.Entry(self, width = 8, state='readonly', textvariable = self.machine_credits)
        self.machine_credit_entry.grid(row = gui_row_iteration, column = 1)
        self.label_infinite = tk.Label(self, text="Infinite Credits: ")
        self.label_infinite.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.infinite_checkbox = ttk.Checkbutton(self, variable = self.infinite_checked, onvalue = True, offvalue = False)
        self.infinite_checkbox.grid(row = gui_row_iteration, column = 3)        
        gui_row_iteration += 1

        # build slot button
        self.label_build_slot = tk.Label(self, text="2. Build Virtual Slot ")
        self.label_build_slot.grid(row = gui_row_iteration, column = 0, columnspan = 4, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_slots_button = tk.Button(self, text="2. Build Virtual Slot", command = self.build_slot_button)
        self.run_slots_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1

        # the status box. intentionally making it a bit obnoxious to catch the eye and because I may want to change how this works later. 
        self.status_box_box = tk.Label(self, textvariable=self.status_box, bg = "dodgerblue1", fg = "ghostwhite")
        self.status_box_box.grid(row = gui_row_iteration, columnspan=4, pady=15 )
        gui_row_iteration += 1

        # payline explanation
        self.label_bet = tk.Label(self, text="Bet per Line ")
        self.label_bet.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.bet_entry = ttk.Entry(self, width = 8, textvariable = self.bet)
        self.bet_entry.grid(row = gui_row_iteration, column = 1)
        self.label_payinfo = tk.Label(self, text="Paylines: ")
        self.label_payinfo.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.paylines_entry = ttk.Entry(self, width = 8, state='readonly', textvariable = self.payline_number)
        self.paylines_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        self.label_payinfo = tk.Label(self, text="Total Bet: ")
        self.label_payinfo.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.paylines_entry = ttk.Entry(self, width = 8, state='readonly', textvariable = self.payline_totalbet)
        self.paylines_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1

        # simulator info
        self.label_simruns = tk.Label(self, text="Simulator Total Spins " )
        self.label_simruns .grid(row = gui_row_iteration, column = 0, columnspan=3, sticky=E)
        self.simrun_entry = ttk.Entry(self, width = 8, textvariable = self.simruns)
        self.simrun_entry.grid(row = gui_row_iteration, column = 3, pady=5)
        gui_row_iteration += 1

        # Run Button
        self.label_sim = tk.Label(self, text="3. Run Simulation ")
        self.label_sim.grid(row = gui_row_iteration, column = 0, columnspan = 3, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_sim_button = tk.Button(self, text="3. Run Simulation", command = self.sim_button_clicked)       
        self.run_sim_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        #self.run_refill_button = tk.Button(self, text="Reload Slot with Initial Credits", command = self.refill_button_clicked)       
        #self.run_refill_button.grid(row = gui_row_iteration, column = 1, columnspan = 3, sticky=W, padx=15)
        gui_row_iteration += 1

        #sim label
        self.label_output = tk.Label(self, text="4a. Save Outputs")
        self.label_output.grid(row = gui_row_iteration, column = 0, columnspan = 3, pady=5, padx=15, sticky=W)
        gui_row_iteration += 1
        #Sim output file
        self.sim_output_label_filepath = tk.Label(self, text="Sim Output Filepath ")
        self.sim_output_label_filepath.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.sim_output_file_entry = ttk.Entry(self, textvariable = self.sim_output_filepath, text=self.sim_output_filepath)
        self.sim_output_file_entry.grid(row = gui_row_iteration, column = 1, columnspan = 2)
        self.sim_output_file_button = tk.Button(self, text="...", command = self.sim_output_filepath_dialog_button)
        self.sim_output_file_button['command'] = self.sim_output_filepath_dialog_button
        self.sim_output_file_button.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        self.sim_do_output_button = tk.Button(self, text="Save File", command = self.sim_output_save_file)   
        self.sim_do_output_button.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration+= 1

        # math output file
        #self.math_output_label_filepath = tk.Label(self, text="Math Output Filepath ")
        #self.math_output_label_filepath.grid(row = gui_row_iteration, column = 0)
        #self.math_output_file_entry = ttk.Entry(self, textvariable = self.math_output_filepath, text=self.math_output_filepath)
        #self.math_output_file_entry.grid(row = gui_row_iteration, column = 1)
        #self.math_output_file_button = tk.Button(self, text="...", command = self.math_output_filepath_dialog_button)
        #self.math_output_file_button['command'] = self.math_output_filepath_dialog_button
        #self.math_output_file_button.grid(row = gui_row_iteration, column = 2)
        #gui_row_iteration += 1
        #self.math_do_output_button = tk.Button(self, text="Save File", command = self.math_output_save_file)   
        #self.math_do_output_button.grid(row = gui_row_iteration, column = 2)
        #gui_row_iteration += 1

        # Plot Credits Button to show math
        self.label_cred_plot = tk.Label(self, text="4b. Plot Credits Over Spins")
        self.label_cred_plot.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_cred_plot_button = tk.Button(self, text="4b. Plot Credits", command = self.plot_cred_button_clicked)       
        self.run_cred_plot_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1
        # Plot RTP Button to show math
        self.label_rtp_plot = tk.Label(self, text="4c. Plot Return To Player Over Spins")
        self.label_rtp_plot.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_rtp_plot_button = tk.Button(self, text="4c. Plot RTP", command = self.plot_rtp_button_clicked)       
        self.run_rtp_plot_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1

        ### reset credits button (separate from the 'build virtual slot'?)
        ### math output area
        # Hit frequency (hits / spins)
        self.label_hit_freq = tk.Label(self, text="Hit Frequency ")
        self.label_hit_freq.grid(row = gui_row_iteration, column = 0,  sticky=E, pady=15)
        self.hit_freq_freq = ttk.Entry(self, width = 8, textvariable = self.hit_freq, state='readonly')
        self.hit_freq_freq.grid(row = gui_row_iteration, column = 1)
        self.label_hit_total = tk.Label(self, text="Hit Total ")
        self.label_hit_total.grid(row = gui_row_iteration, column = 2,  sticky=E)
        self.hit_total_entry = ttk.Entry(self, width = 8, textvariable = self.hit_total, state='readonly')
        self.hit_total_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        # Max Liability (biggest win)
        self.label_max_liability = tk.Label(self, text="Max Liability ")
        self.label_max_liability.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.max_liability_entry = ttk.Entry(self, width = 8, textvariable = self.max_liability, state='readonly')
        self.max_liability_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        # Volatility  (see documentation, it's complex...  volatility  = square root of: (  ( ( sum(win values - mean pay) ) ^^ 2 ) / total spins  )
        self.label_volatility = tk.Label(self, text="Volatility Index ")
        self.label_volatility.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.volatility_entry = ttk.Entry(self, width = 8, textvariable = self.volatility, state='readonly')
        self.volatility_entry.grid(row = gui_row_iteration, column = 1)
        self.label_calc_volatility = tk.Label(self, text="Expected VI ")
        self.label_calc_volatility.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.calc_volatility_entry = ttk.Entry(self, width = 8, textvariable = self.found_volatility, state='readonly')
        self.calc_volatility_entry.grid(row = gui_row_iteration, column = 3)
        gui_row_iteration += 1
        # Return to Player
        self.label_rtp = tk.Label(self, text="Return to Player % (RTP) ")
        self.label_rtp.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.rtp_entry = ttk.Entry(self, width = 8, textvariable = self.return_to_player, state='readonly')
        self.rtp_entry.grid(row = gui_row_iteration, column = 1)
        self.label_calc_rtp = tk.Label(self, text="Expected RTP ")
        self.label_calc_rtp.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.calc_rtp_entry = ttk.Entry(self, width = 8, textvariable = self.found_return_to_player, state='readonly')
        self.calc_rtp_entry.grid(row = gui_row_iteration, column = 3)        
        gui_row_iteration += 1
        self.bhp_label = tk.Label(self, width = 14, text="Bonus Hit Count")
        self.bhp_label.grid(row = gui_row_iteration, column = 0, sticky=E)
        self.bhp_entry = ttk.Entry(self, width = 8, textvariable = self.bonus_hit_count, state='readonly')
        self.bhp_entry.grid(row = gui_row_iteration, column = 1) 
        self.bhp_label = tk.Label(self, width = 14, text="Bonus Hit Percentage")
        self.bhp_label.grid(row = gui_row_iteration, column = 2, sticky=E)
        self.bhp_entry = ttk.Entry(self, width = 8, textvariable = self.bonus_hit_percentage, state='readonly')
        self.bhp_entry.grid(row = gui_row_iteration, column = 3) 
        ### set jackpot
        ### set win
