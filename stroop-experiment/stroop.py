# COGS219 - Psychopy Assignment
import time
import sys
import os
import random
from psychopy import visual,event,core,gui
from generate_trials import generate_trials

# Function for collecting runtime variables
def get_runtime_vars(vars_to_get, order, exp_version = "Stroop"):
    infoDlg = gui.DlgFromDict(dictionary = vars_to_get, title = exp_version, order = order)
    if infoDlg.OK:
        return vars_to_get
    else:
        print('User cancelled')

# Make color incongruent
def make_incongruent(color, stimuli):
    incongruent_colorsq = [stimulus for stimulus in stimuli if stimulus != color]
    random_incongruent_colors = random.choice(incongruent_colors)
    return random_incongruent_colors

# Import trials
def import_trials (trial_filename, col_names = None, separator = ","):
    trial_file = open(trial_filename, 'r')
    
    if col_names is None:
        col_names = trial_file.readline().rstrip().split(separator)
        
    trials_list = []
    for cur_trial in trial_file:
        cur_trial = cur_trial.rstrip().split(separator)
        assert len(cur_trial) == len(col_names)
        trial_dict = dict(zip(col_names, cur_trial))
        trials_list.append(trial_dict)
    return trials_list

# Open a window
win = visual.Window([800,600],color="gray", units='pix',checkTiming=False)

# Prepare components
placeholder = visual.Rect(win,width=180,height=80, fillColor="lightgray",lineColor="black", lineWidth=6,pos=[0,0])
word_stim = visual.TextStim(win,text="", height=40, color="black",pos=[0,0])
instruction = visual.TextStim(win,text="Press the first letter of the ink color", height=20, color="black",pos=[0,-200], autoDraw = True)
fixation = visual.TextStim(win, text = "+", color = "black", height = 15, pos = [0, 0])
feedback = visual.TextStim(win, text = "Incorrect", color = "black", height = 40, pos = [0, 0])
feedback2 = visual.TextStim(win, text = "Too Slow", color = "black", height = 40, pos = [0,0])

# Get the runtime variables
order = ['subj_code', 'seed', 'num_reps']
runtime_vars = get_runtime_vars({'subj_code': 'stroop_101', 'seed': 101, 'num_reps': 25}, order)

# Generate a trial list
generate_trials(runtime_vars['subj_code'], runtime_vars['seed'], runtime_vars['num_reps'])

# Read in trials 
trial_path = os.path.join(os.getcwd(), 'trials', runtime_vars['subj_code']+'_trials.csv')
trial_list = import_trials(trial_path)
print(trial_list)

# Experiment loop
RTs = []
stimuli = ['red', 'orange', 'yellow', 'green', 'blue']
trial_types = ['congruent', 'incongruent']

for cur_trial in trial_list:
    
    cur_word = cur_trial['word']
    cur_color = cur_trial['color']
    trial_type = cur_trial['trial_type']
    cur_ori = cur_trial['orientation']
    
    word_stim.setText(cur_word)
    word_stim.setColor(cur_color)
    
    if cur_ori == 'upside_down':
        word_stim.setOri(180)
    else:
        word_stim.setOri(0)

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
