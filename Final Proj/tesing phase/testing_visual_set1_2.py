# Testing phase

from psychopy import visual, event, core, data
import datetime
import pandas as pd
import random
import os
from sys import platform

# Load the stimuli CSV file into a dataframe]
if platform == "darwin": #Mac OS
    csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
    save_dir = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/FIN/data"
else: 
    csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
    save_dir = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\testing phase\data"
    
# Function to save response data to CSV
all_responses = []
current_phase = None

def save_to_csv():
    
    if not all_responses:
        return
        
    df = pd.DataFrame(all_responses)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response_file = os.path.join(save_dir, f"testing_V_s1_72_{timestamp}.csv")

    # Save to CSV
    df.to_csv(response_file, index = False, lineterminator = "\n")
    print(f"Saved all responses to {response_file}")
    
# Laod stimuli CSV file
stimuli_df = pd.read_csv(csv_file)

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for the space bar pressed
def show_message(text, timeout = 10):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
    msg.draw()
    win.flip()
    start_time = core.getTime()
    while True:
        keys = event.getKeys()
        
        if "space" in keys:
            break
        if core.getTime() - start_time > timeout:
            print(f"No response within {timeout} seconds. Exiting.")
            win.close()
            core.quit()
        core.wait(0.1)
        
# Visual comprehesion - Set 1
print("Starting Visual Comprehension Phase...")
current_phase = "Visual_comprehension"

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True) 

# Set the number of repetitions
n = 4

# Generate a balanced block of trials with randomized match/mismatch
def create_block():
    unique_names = list(stimuli_df['name_s1'].unique())
    random.shuffle(unique_names)
    
    # Split the names into 6 for match and 6 for mismatch
    match_names = unique_names[:6]
    mismatch_names = unique_names[6:]
    
    match_trials = []
    mismatch_trials = []

    # Load all image path
    all_images = list(stimuli_df['visual_s1'])
    
    # Create match trials: use the correct image
    for name in match_names:
        row = stimuli_df[stimuli_df['name_s1'] == name].iloc[0]
        match_trials.append({
        'name': name,
        'image': row['visual_s1'],
        'match': True
        })
        
    # Create mismatch trials: use an incorrect image
    for name in mismatch_names:
        row = stimuli_df[stimuli_df['name_s1'] == name].iloc[0]
        # Select an image that is not the correct one
        incorrect_images = [img for img in all_images if img !=row['visual_s1']]
        mismatched_image = random.choice(incorrect_images)
        mismatch_trials.append({
        'name': name,
        'image': mismatched_image,
        'match': False
        })
    
    # Combine and shuffle the block
    block_trials = match_trials + mismatch_trials
    random.shuffle(block_trials)
    
    return block_trials
    
# Generate all blocks
all_blocks = [create_block() for _ in range (n)]

# Welcome message
show_message("Press 1 if match, 2 if mismatch.\n\nPress the space bar to start.")

# Prepare text and image components
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', height = 35, pos =(0,0))
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Experiment loop
terminate_exp = False  
event.clearEvents()
block_pair_correct_responses = 0
block_pair_trial_count = 0

for block_num, block in enumerate(all_blocks):
    correct_responses = 0 # Track correct responses for this block
    block_trial_count = len(block)
    
    for trial_num, trial in enumerate(block):
        event.clearEvents()
        
        # Check for an exit key
        keys = event.getKeys(keyList = ["escape"])
        if "escape" in keys:
            terminate_exp = True
            break
        
        selected_name = trial['name']
        selected_image = trial['image']
        is_match = trial['match']
      
        #1 Each trial begins with a fixation cross (0.5s)
        fixation_display.draw()
        win.flip()
        core.wait(0.5)

        #2 Display the name (2s)
        name_display.setText(selected_name)
        name_display.draw()
        win.flip()
        core.wait(1)

        #3 Visual display of the object either matching or not matching that name (1s)
        image_display.setImage(selected_image)
        image_display.draw()
        win.flip()
        core.wait(1)

        #4 Participants needs to decide whether the object and name match (3000ms max)
        response_wait.draw()
        win.flip()
        event.clearEvents()
        
        #4-1 Start timing precisely when the response prompt appears
        responseTimer =  core.Clock()
        responseTimer.reset()
        
        response = None
        rt = None

        while responseTimer.getTime() < 3:
            # Check for early exit during the experiment
            keys = event.getKeys(keyList = ["escape", "1", "2"])
            
            if "escape" in keys:
                print("Escape key pressed during the experiment. Exiting the experiment early.")
                terminate_exp = True
                break 
            
            if "1" in keys:
                response = "match"
                rt = responseTimer.getTime()
                break
            elif "2" in keys:
                response = "mismatch"
                rt = responseTimer.getTime()
                break
            
        # If exit was triggered inside the while loop, break the main loop as well
        if terminate_exp:
            break
        
        # If no response within 3 seconds, mark is as "no response"
        if response is None:
            response = "no response"
            rt = 0
            
        # Check accuracy
        if (response == "match" and is_match) or (response == "mismatch" and not is_match):
            correct_responses += 1

        #5 1-second blank screen
        fixation_display.draw()
        win.flip()
        core.wait(1)

        # Record the response data
        all_responses.append({
            'phase': current_phase,
            'block': int(block_num) + 1,
            'trial': int(trial_num) + 1,
            'object_name': selected_name,
            'object_image': selected_image,
            'match': is_match,
            'response': response,
            'response_time': rt * 1000 if rt else 0
        })
        
        # Update cumulative accuracy tracking
        block_pair_correct_responses += correct_responses
        block_pair_trial_count += block_trial_count
        
    # Insert a break every 12 trials with a feedback message, except after the last trial
    if (block_num + 1) % 2 == 0 and block_num < len(all_blocks) - 1:
        if block_pair_trial_count > 0:
            accuracy = (block_pair_correct_responses / block_pair_trial_count) * 100
        else:
            accuracy = 0
        
        feedback_message = f"Accuracy: {accuracy: .1f}%\n\nTake a short break.\nPress the space bar to continue."
        
        feedback_display = visual.TextStim(win, text = feedback_message, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        feedback_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to contitnue
        keys = event.waitKeys(keyList = ["space", "escape"])
        
        if keys:
            if "escape" in keys:
                print ("Terminate key pressed. Exiting experiment loop early.")
                terminate_exp = True
            elif "space" in keys:
                print(f"Key pressed: {keys}")
                pass
                
        core.wait(0.1)
        
        # Reset block_pair accuracy tracking
        block_pair_correct_responses = 0
        
        event.clearEvents()

# End message
print("Completed Visual Comprehension Phase.")
show_message("Press the space bar to move to the next phase.")
core.wait(0.1)

event.clearEvents()

# Written Production - Set 1
print("Starting Written Production Phase...")
current_phase = "Written_production"
core.wait(0.1)

# Define allowed keys: alphabets, backspace, return, and escape
allowed_keys = list("abcdefghijklmnopqrstuvwxyz") + ["backspace", "space", "escape"]

# Welcome message
show_message("Type the correct name of the object and press the SPACE BAR to move next.\n\nPress the space bar to start.")

# Prepare text and image component
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0,50))
input_display = visual.TextStim(win, text = "", font = 'Arial', color = 'white', height = 30, pos = (0, -150))
input_box = visual.Rect(win, width = 150, height = 50, lineColor = "white", pos = (0, -150))

# Set the number of repetitions
n2 = 4

# Experiment loop
terminate_exp = False
event.clearEvents()

for block in range(n2):
    
    # shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys():
            terminate_exp = True
            break
    
        # 1. Select a random image and its corresponding name
        object_image = row['visual_s1']
        correct_name = row['name_s1']
        
        random.shuffle([correct_name])
        
        # 2. Display Fixation cross
        fixation_display.draw()
        win.flip()
        core.wait(0.5)
        
        # 3. Display an image
        image_display.image = object_image
        image_display.draw()
        win.flip()
        core.wait(2)
   
        # 4. Wait for participants to type name
        typed_name = ""
        responseTimer = core.Clock()
        responseTimer.reset()
        
        event.clearEvents()
        
        while True:
            image_display.draw()
            input_box.draw()
            input_display.text = typed_name
            input_display.draw() 
            win.flip()
            
            keys = event.getKeys()
            
            if "escape" in keys:
                terminate_exp = True
                break
            
            for key in keys:
                if key == "space":
                    break
                elif key == "backspace":
                    typed_name = typed_name[:-1]
                elif key in list("abcdefghijklmnopqrstuvwxyz"):
                    typed_name += key
                    
            if "space" in keys or terminate_exp:
                break
                
        rt = responseTimer.getTime()
        is_correct = typed_name.strip().lower() == correct_name.strip().lower()
        
        # If no response within 5 seconds, mark it as "no response"
        if rt > 5:
            typed_name = "no response"
            rt = 0
            is_correct = False
        
        win.flip()
    
        if terminate_exp:
            break
        
        # 5. Display fixation cross; inter-trial interval
        fixation_display.draw()
        win.flip()
        core.wait(1)
        
        # Record the response data
        all_responses.append({
            'phase': current_phase,
            'block': int(block) + 1,
            'trial': int(index) + 1,
            'object_name': correct_name,
            'object_image': object_image,
            'response': typed_name,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else 0
        })
        
        event.clearEvents()
    
    if terminate_exp:
        break
    
    # Break after every 12 tirals, except after the last trial
    if (block+1) % 2 == 0 and block +1 < n2:
        break_display = visual.TextStim(win, text = "Take a short break.\n\n Press the space bar to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        break_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to continue
        while True:
            keys = event.getKeys(keyList = ["space", "escape"])
            if "escape" in keys:
                print("Escape pressed.")
                terminate_exp = True
                break
            elif "space" in keys:
                break
        
    event.clearEvents()
        
# Final save before exit
print("Completed Written Production Phase.")
save_to_csv()

# Close the window after the experiment
# End message
show_message("Press the space bar to exit.")

win.close()
core.quit()
