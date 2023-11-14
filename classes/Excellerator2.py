#Excellerator2.py

import sys
import os
import os.path
import math
import random as rd
import numpy as np        # rounding
import pandas as pd

class Excellerator2():
    def __init__(self, filepath, bet, initial_credits, debug_level, infinite_checked):
        # initialization values 
        self.input_filepath = filepath
        self.game_credits = initial_credits   # the 'wallet' value 
        self.initial_credits = initial_credits  #specifically to save the value for the infinite check
        self.bet_per_line = bet
        self.infinite_checked = infinite_checked
        self.debug_level = debug_level
        #self.eset_df = excel_file.parse(self.settings_sheetname, index_col = 0)
        #if(self.debug_level >= 3):
        #    for idx, item in eset_df.iterrows():
        #       print(f"index: '{idx}' and \n row '{item['value']}' .. \n")

        # this section is to define where we get our theoretical/pre-calculated values from.. 
        self.rtp_sheetname = 'Math'   # it doesn't like 'Ways/Pays' in excel
        self.vi_sheetname = 'Math'
        self.rtp_column = 'RTP'
        self.vi_column = 'Volatility Index'
        self.paylines_column = 'Number of Lines'
        self.bet_per_line_column = 'Bet Per Line'
        #self.columns = ['Win Lines', 'Weight', 'Lower Range', 'Upper Range']
        self.columns="A:D"  # the above column names, it's either one or the other to select.
        #self.paylines_total = 9 # 3x3 defaul0t value to be set later... in the paylines
        # the math section.
        self.paylines = 1   # just setting a default, because it used to be calculated in the old script. 
        # ---- this will need to be calculated.
        self.winlines = 0
        self.hit_total = 0
        self.maximum_liability = 0
        #for volatility
        self.volitility = float(0)
        self.mean_pay = 0
        self.summation = 0
        self.this_win = 0    # value to be returned for tracking
        self.round_win = 0
        self.total_won = 0
        self.total_bet = 0
        self.win_toggle = 0 
        #if(self.debug_level >= 2):
        #    print(f"        = Total bet is being set and is {self.total_bet}")
        self.rtp = 0
        self.vi = 0
        self.bonus_hit_count = 0
        # debug announcement; the place for initial conditions to get checked or set.
        if(self.debug_level >= 1):
            print(f"DEBUG LEVEL 1 - basic math and reel matching info")
        if(self.debug_level >= 2):
            print(f"DEBUG LEVEL 2 - most debugging information, descriptive")
            #print(f"        >>> the local variable {self.input_filepath} .. was saved from input {filepath}")
        if(self.debug_level >= 3):
            print(f"DEBUG LEVEL 3 - every other status message used for debugging - verbose, keep below ")
        # LOAD - Access the excel file
        self.load_excel()        
        # for each set, table 1 would be #spins, table 2 is paylines, table 3 is win values
        # for example, after the excel file is loaded, we should be able to directly call the first three tables, always
        #self.paylines = len(self.lines_sheet1) - 1 # -1 becuase we aren't counting the 0 line /  header
        # this needs to be addressed, due to new calculations
        if(self.paylines == 0):
            self.paylines = 1
        #for betting
        self.this_bet = self.bet_per_line * self.paylines

    def load_excel(self):
        """ takes in the excel file, and performs the setup logic""" 
        excel_file = pd.ExcelFile(self.input_filepath)
        if(self.debug_level >= 2):
            print(f"Loading Excel sheet, found: {excel_file.sheet_names}")
        sheet_count = 0
        self.spin_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)
        self.spin_sheet1.columns = self.spin_sheet1.columns.str.strip()
        sheet_count += 1
        games_total = len(self.spin_sheet1)  # this is how many bonus games we have, from the # of choices
        #print(f"found {games_total} total games!")
        self.lines_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)
        self.lines_sheet1.columns = self.lines_sheet1.columns.str.strip()
        sheet_count += 1
        self.pays_sheet1 = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)
        self.pays_sheet1.columns = self.pays_sheet1.columns.str.strip()
        sheet_count += 1
        # set the math -- ERROR CHECKING NEEDED HERE
        # set the RTP
        if(self.rtp_sheetname in excel_file.sheet_names):
            self.rtp_data = pd.read_excel(self.input_filepath, sheet_name=self.rtp_sheetname, header=0)
            self.rtp_data.columns = self.rtp_data.columns.str.strip()
            self.rtp = self.rtp_data[self.rtp_column][0] * 100 ## times 100 so that we have the percentage that matches the data
        if(self.vi_sheetname in excel_file.sheet_names):
            self.vi_data = pd.read_excel(self.input_filepath, sheet_name=self.vi_sheetname, header=0)
            self.vi_data.columns = self.vi_data.columns.str.strip()
            self.vi = self.vi_data[self.vi_column][0]
        self.paylines_data = pd.read_excel(self.input_filepath, sheet_name=self.rtp_sheetname, header=0)
        self.paylines_data.columns = self.paylines_data.columns.str.strip()
        self.paylines = self.paylines_data[self.paylines_column][0]
        self.bet_per_line_data = pd.read_excel(self.input_filepath, sheet_name=self.rtp_sheetname, header=0)
        self.bet_per_line_data.columns = self.bet_per_line_data.columns.str.strip()
        self.bet_per_line = self.bet_per_line_data[self.bet_per_line_column][0] / 100  # converting correctly.
    
        # now dynamically build the bonus games
        for i in range(2, games_total+1):
            if(self.debug_level >= 2):
                print(f"    Loading Bonus Game sheet {i} at sheet_count {sheet_count}")
            exec("self.spin_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)" % i)
            exec("self.spin_sheet%d.columns = self.spin_sheet%d.columns.str.strip()" % (i, i))
            #print(f'SPIN SHEET {i}:')
            #exec("print(f'{spin_sheet%d}')" % i)
            sheet_count += 1
            exec("self.lines_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)" % i)
            exec("self.lines_sheet%d.columns = self.lines_sheet%d.columns.str.strip()" % (i, i))
            #print(f"LINES SHEET {i}:")
            #exec("print(f'{lines_sheet%d}')" % i)
            sheet_count += 1
            exec("self.pays_sheet%d = excel_file.parse(sheet_name=sheet_count, usecols=self.columns, header=0)" % i)
            exec("self.pays_sheet%d.columns = self.pays_sheet%d.columns.str.strip()" % (i, i))
            #print(f"PAYS SHEET {i}:")
            #exec("print(f'{pays_sheet%d}')" % i)
            sheet_count += 1

        # now calculate mean_pay
#        self.mean_pay = 0
        ## old calculation way
        #total_mean_pays = 0
        #total_mean_lines = 0
        #########
        # weighted wins will require a weighted mean calculation
        # https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/weighted-mean/
        #########
#        sum_weighted_win = 0
#        sum_weight = 0
#        pays_sheet = []
#        for i in range(1, games_total+1):
#            exec("pays_sheet.append(self.pays_sheet%d) " % i)
            #exec("print(f'i = {i}, ps = {self.pays_sheet%d}')" % i)
#            for j, line in pays_sheet[0].iterrows():
                #print(f"line {line[len(line)-1]}")
                ##total_mean_pays += line[0]
                ##total_mean_lines += 1
#                sum_weighted_win += line[0] * line[1]
#                sum_weight += line[1]                                                                                                                                                                                                                                                                                                                                          
#                if(self.debug_level >= 2):
#                    print(f"    #### sum of weighted wins: {sum_weighted_win} and the sum of weights: {sum_weight}")
        # This needs to be a Weighted Mean Formula
#        self.mean_pay = sum_weighted_win / sum_weight
        #self.mean_pay = total_mean_pays / total_mean_lines
#        if(self.debug_level >= 2):
#            print(f"    #### mean pay {self.mean_pay} = sum of products {sum_weighted_win} / weights {sum_weight}")
        #if(self.debug_level >= 2):
        #    print(f"        $!MATH$! Paytable Mean Pay is {self.mean_pay}")    
        #self.mean_pay = self.mean_pay / len(self.pays_sheet1)
        #### EXAMINE THIS - DO THE BONUS TABLES ADD INTO THE MEAN AS WELL? MATTERS FOR LATER MATH


    def adjust_credits(self,value):
        # bets should be negative values, wins or deposits positive
        # for totals tracked
        if(value >= 0):
            self.total_won += value
            if(self.debug_level >= 2):
                print(f"                     STATUS: total_won is: {self.total_won}")
        elif(value < 0):
            # the negative value of the bet itself. 
            self.total_bet -= value
            if(self.debug_level >= 2):
                print(f"                     STATUS: total_bet is: {self.total_bet}")
        #adjust credits, set to 2 decimal pplaces, this should rounds appropriately in all situations. 
        self.game_credits = np.round(float(self.game_credits) + value, 2)
        if(self.debug_level >= 1):
            print(f"    $$$$ Adjusted credits by {str(value)}, now game wallet at: {str(self.game_credits)}")

    def return_credits(self):
        return self.game_credits 

    def bonus_game(self, spin_sheet, lines_sheet, pays_sheet):
        # will use spin_sheet{sheet_num}. lines_sheet{sheet_num}, and pays_sheet{sheet_num}
        # this will heavily use the exec() function using the sheet_number
        #print(f"{spin_sheet}")
        #print(f"{lines_sheet}")
        #print(f"{pays_sheet}")
        self.bonus_hit_count += 1
        try: 
            random = rd.randrange(0, int(spin_sheet[-1:]['Upper Range']))
        except:
            random = 0
        if(self.debug_level >= 1):
            print(f"   Bonus Spins, random: {random}")      
        for s, srow in spin_sheet.iterrows():
            #print(f" -- spin check in bonus: checking row {s} with info {srow}")
            if((random >= srow["Lower Range"] and random <= srow["Upper Range"]) or len(spin_sheet) == 1):
                spins = int(srow[0])
                if(self.debug_level >= 1):
                    print(f"      Found {spins} Bonus spins")
                if(spins==0):
                    spins = 1   # to accomodate weirdness with the 'upper range' column = 0'
                for j in range(0, spins):
                    random = rd.randrange(0, int(lines_sheet[-1:]['Upper Range']))
                    if(self.debug_level >= 1):
                        print(f"      Bonus Lines: at spin {j} random: {random}")
                    for l, lrow in lines_sheet.iterrows():
                      #print(f" -- lines check in bonus: checking {l} with info {lrow}")
                        if((random >= lrow["Lower Range"] and random <= lrow["Upper Range"]) or len(lines_sheet) == 1):
                            if(self.debug_level >= 1):
                                print(f"         Bonus Chose {lrow[0]} Line Wins")
                            if(lrow[0] == 0):
                                lspins = 1
                            else:
                                lspins = lrow[0]
                            for lines in range(0, lspins):  
                                random = rd.randrange(0, int(pays_sheet[-1:]['Upper Range']))
                                if(self.debug_level >= 1):
                                    print(f"            Bonus Wins random result: {random}")
                                for bw, bwrow in pays_sheet.iterrows():
                                    if(random >= bwrow["Lower Range"] and random <= bwrow["Upper Range"]):
                                        if(bwrow[0] != 0):
                                            if(self.debug_level >= 1):
                                                print(f"               Bonus Winner! would add {bwrow[0]} to the total, found between {bwrow['Lower Range']} and {bwrow['Upper Range']}")
                                            self.this_win = bwrow[0] * self.bet_per_line #* .01 # (in pennies)
                                            self.round_win += self.this_win
                                            self.win_toggle = 1 
                                            break                                        
                    # reminder to check mean_pay - do we sum the bonus tables too? 
        self.summation += (self.round_win - self.mean_pay) ** 2
        if(self.win_toggle == 1):
            self.adjust_credits(self.round_win)
            self.hit_total += 1
            if(self.debug_level >= 1):
                print(f" [H]found a hit! hit total now: {self.hit_total}")
            self.win_toggle = 0    
            if(self.round_win > self.maximum_liability):
                self.maximum_liability = self.round_win
            if(self.debug_level >= 2):
                print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {self.round_win}) squared. ")

    def play_game(self):
       # The "Game Spins".. if this were a slot, it would be the "play game" button. Will use spin_sheet1, lines_sheet1, and pays_sheet1
        self.this_win = 0  # the 'running total'
        self.round_win = 0 # the tallies win
        if(self.debug_level >= 1):
            print(f"    -- betting {self.this_bet}")
        self.adjust_credits(self.this_bet * -1)
        if(self.debug_level >= 3):
            print(f"            checking credits: {self.game_credits}  <  {str(this_bet)}")
        # random number vs spin table.   ## set upper range as a variable, so we don't have to keep calling the data structure? 
        ssur = int(self.spin_sheet1.iloc[-1:]['Upper Range'])
        if(ssur == 0):
            ssur = 1
        random = rd.randrange(0, ssur)
        if(self.debug_level >= 1):
            print(f"    Main Game Initial Bonus Trigger, randomly number for the spin: {random}")
        for i, row in self.spin_sheet1.iterrows():
            if(random >= row["Lower Range"] and random <= row["Upper Range"]):
                if(self.debug_level >= 1):
                    print(f"   Found {random} is between {row['Lower Range']} and {row['Upper Range']}")
                if(i == 0):
                    if(self.debug_level >= 1):
                        print(f"    Playing Main Game")
                    lsur = int(self.lines_sheet1[-1:]['Upper Range'])
                    if(lsur == 0):
                        lsur = 1
                    random = rd.randrange(0, lsur)
                    if(self.debug_level >= 1):
                        print(f"   Main Game Lines: randomly chosen, for the lines: {random}")
                    #loop through the pay lines sheet
                    for l, lrow in self.lines_sheet1.iterrows():
                        if(random >= lrow["Lower Range"] and random <= lrow["Upper Range"]):
                            if(self.debug_level >= 1):
                                print(f"      Chose {lrow[0]} Line Wins")
                            if(lrow[0] > 0):
                                # if it's more than 0 lines
                                for lines in range(0, int(lrow[0])):  
                                    psur = int(self.pays_sheet1[-1:]['Upper Range']) # should never have 0 as an UR. if so, out of design
                                    if(psur == 0):
                                        psur = 1
                                    random = rd.randrange(0, psur)
                                    if(self.debug_level >= 1):
                                        print(f"      Main Game Win: randomly chosen, for the wins: {random}")
                                    for w, wrow in self.pays_sheet1.iterrows():
                                        if(wrow[0] > 0):
                                            # figure out what the payout is by looping through the win table
                                            if(random >= wrow["Lower Range"] and random <= wrow["Upper Range"]):
                                                if(self.debug_level >= 1):
                                                    print(f"         Winning Line! would add {wrow[0]} to the total, found between {wrow['Lower Range']} and {wrow['Upper Range']}")
                                                # win logic goes here
                                                self.this_win = wrow[0] * .01 # (in pennies) #* self.bet_per_line #
                                                self.round_win += self.this_win
                                                self.win_toggle = 1 
                                                break
                else:
                    sn = i+1
                    if(self.debug_level >= 1):
                        print(f"   Bonus Game '{row[0]}' at row {sn} !!!!!!!!!!!!")
                    # using i+1 because it counts up from zero programatically, and the sheets are referenced starting at 1.
                    toPass = []
                    # this is a concession to the fact that I spent way too long trying to get this dynamic info through
                    exec("toPass.append(self.spin_sheet%d)" % sn)
                    exec("toPass.append(self.lines_sheet%d)" % sn)
                    exec("toPass.append(self.pays_sheet%d)" % sn)
                    self.bonus_game(toPass[0], toPass[1], toPass[2])
        if(self.debug_level >= 2):
            print(f"        $$$$ ++++ TOTAL win this round: {self.round_win}, with a total simulator win of {self.total_won}")
        # Then, if it was a win, do the math
        if(self.win_toggle == 1):
            self.adjust_credits(self.round_win)
            self.hit_total += 1
            if(self.debug_level >= 1):
                print(f" [H]found a hit! hit total now: {self.hit_total}")            
            self.win_toggle = 0    
            if(self.round_win > self.maximum_liability):
                self.maximum_liability = self.round_win
            # reminder to check mean_pay - do we sum the bonus tables too? 
            # the running summation, calculated each round, skipping non-wins because it's += 0 and extra unneeded calcs
            self.summation += (self.round_win * 100) ** 2 / self.paylines   # multiplying 100 to put it into 'credits' instead of 'money' 
            #self.summation += (self.round_win - self.mean_pay) ** 2
            if(self.debug_level >= 2):
                print(f"    +=+=+=+= summation is now {self.summation}, which is adding {self.round_win*100} squared, divided by {self.paylines}. ")
    # end of play_game
#end class Excellerator2