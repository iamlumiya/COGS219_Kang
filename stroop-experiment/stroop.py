# COGS219 - Psychopy Assignment
import time
import sys
import os
import random
from psychopy import visual,event,core,gui

# Function for collecting runtime variables
def get_runtime_vars(vars_to_get, order, exp_version = "Stroop"):
    infoDlg = gui.DlgFromDict(dictionary = vars_to_get, title = exp_version, order = order)
    if infoDlg.OK:
        return vars_to_get
    else:
        print('User cancelled')

# Make color incongruent
def make_incongruent(color, stimuli):
    incongruent_colors = [stimulus for stimulus in stimuli if stimulus != color]
    random_incongruent_colors = random.choice(incongruent_colors)
    return random_incongruent_colors

# Create a generate trials file
def generate_trials(subj_code, seed, num_repetitions = 25):
    
    # Define key parameters
    colors = ['red', 'orange', 'yellow', 'green', 'blue']
    trial_types = ["congruent", "incongruent"]
    orientations = ["upright", "upside_down"]
    num_repetitions = int(num_repetitions)
    
    # Random seed
    random.seed(int(seed))
    
    # Ensure 'trials' directory exists
    os.makedirs('trials', exist_ok = True)
    
    # Open a trial file
    trial_file = open(os.path.join(os.getcwd(), 'trials', f"{subj_code}_trials.csv"), 'w')
    separator = ","
    header = separator.join(["subj_code", "seed", "word", "color", "trial_type", "orientation"])
    trial_file.write(header+'\n')
    
    # Write code to loop through creating trials here
    trial_data = []
    for i in range(num_repetitions):
        for cur_trial_type in trial_types:
            for cur_orientation in orientations:
                cur_word = random.choice(colors)
                if cur_trial_type == "incongruent":
                    cur_color = make_incongruent(cur_word, colors)
                else:
                    cur_color = cur_word
                trial_data.append([subj_code, seed, cur_word, cur_color, cur_trial_type, cur_orientation])
    
    # Shuffle the list
    random.shuffle(trial_data)
    
    # Write the tirals to the trials file
    for cur_trial in trial_data:
        trial_file.write(separator.join(map(str, cur_trial)) + '\n')
        
    # Close the file
    trial_file.close()
        
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

# Experiment loop
RTs = []
stimuli = ['red', 'orange', 'yellow', 'green', 'blue']
trial_types = ['congruent', 'incongruent']

while True:
    cur_stim = random.choice(stimuli)
    trial_type = random.choice(trial_types)
    
    word_stim.setText(cur_stim)
    cur_color = make_incongruent(cur_stim, stimuli) if trial_type == 'incongruent' else cur_stim
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
