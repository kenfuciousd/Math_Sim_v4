#globals.py
    #globals? - need to be initialized once, outside the simulator which is instantiated each new Simulator run.
    # in order to solve the 'math plot forgets its prior values' issue with the plot sizing
    # https://stackoverflow.com/questions/3400525/global-variable-from-a-different-file-python

def initialize():
    global y_credits_ceiling
    y_credits_ceiling = 0
    global y_rtp_ceiling
    y_rtp_ceiling = 0