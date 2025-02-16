# COGS219 - Psychopy Assignment
import time
import sys
import os
import random
from psychopy import visual,event,core,gui

# Create stimuli
stimuli = ['red', 'orange', 'yellow', 'green', 'blue']
trials = ['congruent', 'incongruent']

# Make color incongruent
def make_incongruent(color):
    incongruent_colors = [stimulus for stimulus in stimuli if stimulus != color]
    random_incongruent_colors = random.choice(incongruent_colors)
    return random_incongruent_colors

# Open a window
win = visual.Window([800,600],color="gray", units='pix',checkTiming=False)

# Prepare components
placeholder = visual.Rect(win,width=180,height=80, fillColor="lightgray",lineColor="black", lineWidth=6,pos=[0,0])
word_stim = visual.TextStim(win,text="", height=40, color="black",pos=[0,0])
instruction = visual.TextStim(win,text="Press the first letter of the ink color", height=20, color="black",pos=[0,-200], autoDraw = True)
fixation = visual.TextStim(win, text = "+", color = "black", height = 15, pos = [0, 0])
feedback = visual.TextStim(win, text = "Incorrect", color = "black", height = 40, pos = [0, 0])
feedback2 = visual.TextStim(win, text = "Too Slow", color = "black", height = 40, pos = [0,0])

# Experiment loop
RTs = []

while True:
    cur_stim = random.choice(stimuli)
    trial_type = random.choice(trials)
    
    word_stim.setText(cur_stim)
    if trial_type == 'incongruent':
        cur_color = make_incongruent(cur_stim)
    else:
        cur_color = cur_stim
    word_stim.setColor(cur_color)
    
    # Display fixation cross
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Blacnk space for 0.5 second
    placeholder.draw()   
    win.flip()
    core.wait(0.5)
    
    # Display stimuli for 1 second
    responseTimer = core.Clock()
    responseTimer.reset()
    placeholder.draw()
    instruction.draw()
    word_stim.draw()
    
    win.flip()
    core.wait(1.0)
    
    # Wait for response and record RT    
    valid_keys = ["r", "o", "y", "g", "b", "q"]
    key_pressed = event.waitKeys(keyList = valid_keys, maxWait = 2)

    if not key_pressed:
        feedback2.draw()
        win.flip()
        core.wait(1)
        RT = 0
    else: 
        if key_pressed[0] == "q":
            break
            
        RT = round(responseTimer.getTime() * 1000)
        RTs.append(RT)
        print("Response:", key_pressed[0], "Reaction Time:", RT)
    
        # Display feedback message only for incorrect response
        if key_pressed[0] == cur_color[0]:
            pass
        elif key_pressed[0] == "q":
            break
        else:
            feedback.draw()
            win.flip()
            core.wait(1)
    
    # Blank space for 0.15 second
    placeholder.draw()
    win.flip()
    core.wait(.15)
    
    event.clearEvents()

# Exit 
win.close()
core.quit()
