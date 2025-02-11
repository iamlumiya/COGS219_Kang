# COGS219 - Psychopy Assignment
import time
import sys
import os
import random
from psychopy import visual,event,core,gui

# Create stimuli
stimuli = ['red', 'orange', 'yellow', 'green', 'blue']

# Open a window
win = visual.Window([800,600],color="gray", units='pix',checkTiming=False)

# Prepare components
placeholder = visual.Rect(win,width=180,height=80, fillColor="lightgray",lineColor="black", lineWidth=6,pos=[0,0])
word_stim = visual.TextStim(win,text="", height=40, color="black",pos=[0,0])
instruction = visual.TextStim(win,text="Press the first letter of the ink color", height=20, color="black",pos=[0,-200])
fixation = visual.TextStim(win, text = "+", color = "black", height = 15, pos = [0, 0])

# Experiment loop
while True:
    cur_stim = random.choice(stimuli)
    word_stim.setText(cur_stim)
    word_stim.setColor(cur_stim)
    
    # Display fixation cross
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Blacnk space for 0.5 second
    placeholder.draw()
    instruction.draw()    
    win.flip()
    core.wait(0.5)
    
    # Display stimuli for 1 second
    placeholder.draw()
    instruction.draw()
    word_stim.draw()
    
    win.flip()
    core.wait(1.0)
    
    # Blank space for 0.15 second
    placeholder.draw()
    instruction.draw()    
    win.flip()
    core.wait(.15)

    # Exit code
    if event.getKeys(['q']):
        win.close()
        core.quit()

