# Testing phase
# Auditory Comprehension

from psychopy import visual, core, event, data, sound
import pandas as pd
import random
import datetime
import os
from sys import platform

# Set file path
if platform == "darwin": # macOS
    excel_file_path = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/test phase/data"
    csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
else: #window
    excel_file_path = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\testing phase\data"
    csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
    
# Generate timestamped file name
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(excel_file_path, exist_ok = True)
file_name = os.path.join(excel_file_path, f"comp_aud_set1_{timestamp}.csv")

# Load the stimuli CSV file into a dataframe
stimuli_df = pd.read_csv(csv_file)

# Function to save response data to CSV
all_responses = []

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True)

# Set the number of repetitions
n = 4

# Generate a balanced block of trials with randomized match/mismatch
def create_block():
    unique_names = list(stimuli_df['auditory_s1'].unique())
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
        row = stimuli_df[stimuli_df['auditory_s1'] == name].iloc[0]
        match_trials.append({
        'name': name,
        'image': row['visual_s1'],
        'match': True
        })
        
    # Create mismatch trials: use an incorrect image
    for name in mismatch_names:
        row = stimuli_df[stimuli_df['auditory_s1'] == name].iloc[0]
        # Select an image that is not the correct one
        incorrect_images = [img for img in all_images if img != row['visual_s1']]
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

# Set up the window
win = visual.Window([800, 800], color = "black", units = 'pix', checkTiming = False)

# Welcome message
welcome_text = visual.TextStim(win, text = "Press LEFT arrow key if match, RIGHT arrow key if mismatch.\n\nPress the space bar to start.", font = 'Arial', color = "white", height = 35, pos = (0, 0))
welcome_text.draw()
win.flip()

# Wait for keyboard press with a timdeout
start_time = core.getTime()
response = None

while core.getTime() - start_time < 15:
    keys = event.getKeys()
    if keys:
        if "space" in keys:
            response = keys[0]
            print(f"Key pressed: {response}")
            break
            
if response is None:
    print("No response within 15 seconds. Exiting.")
    win.close()
    core.quit()
    
# Prepare text and image components
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0, 0))

# Experiment loop
terminate_exp = False
event.clearEvents()
block_pair_correct_responses = 0
block_pair_trial_count = 0

for block_num, block in enumerate(all_blocks):
    correct_responses = 0
    block_trial_count = 0
    event.clearEvents()
    
    for trial_num, trial in enumerate(block):
        selected_name = trial['name']
        selected_image = trial['image']
        is_match = trial['match']
    
        # Check for an exit key
        keys = event.getKeys(keyList = ["escape"])
        if "escape" in keys:
            terminate_exp = True
            break
            
        # 1. Each trial begins with a fixation cross (0.5s)
        fixation_display.draw()
        win.flip()
        core.wait(0.5)
        
        # 2. Audio play with a fixation cross (2s)
        name_audio = sound.Sound(selected_name, stopTime = 2)
        name_audio.play()
        fixation_display.draw()
        win.flip()
        core.wait(2)
        
        # 3. Visual display of the object either matching or not matching that name (1s)
        image_display.setImage(selected_image)
        image_display.draw()
        win.flip()
        core.wait(1)
        
        # 4. Participants needs to decide whether the object and name match (3000ms max)
        response_wait.draw()
        win.flip()
        event.clearEvents()
        
        # 4-1. Start timing precisely when the response prompt appear
        responseTimer = core.Clock()
        responseTimer.reset()
        
        response = None
        rt = None
        
        while responseTimer.getTime() < 3:
            # Check for early exit during the experiment
            keys = event.getKeys(keyList = ["escape", "left", "right"])
            
            if "escape" in keys:
                print("Escape key pressed during the experiment. Exiting the experiment early.")
                terminate_exp = True
                break 
                
            if "left" in keys:
                response = "match"
                rt = responseTimer.getTime()
                break
            elif "right" in keys:
                response = "mismatch"
                rt = responseTimer.getTime()
                break   
                
        # If exit was triggered inside the while loop, break the main loop as well
        if terminate_exp:
            break
        
        # If no response within 3 seconds, mark it as "no response"
        if response is None:
            response = "no response"
            rt = 0
            
        # Check accuracy
        if (response == "match" and is_match) or (response == "mismatch" and not is_match):
            correct_responses += 1
            
        # 5. 1-second blank screen
        fixation_display.draw()
        win.flip()
        core.wait(1)
    
        # Record the response data
        all_responses.append({
            'block': block_num + 1,
            'trial': trial_num + 1,
            'object_name': selected_name,
            'selected_image': selected_image,
            'match': is_match,
            'response': response,
            'response_time': rt * 1000 if rt else 0
        })
    
        # Save progress after every trial
        response_df = pd.DataFrame(all_responses)
        response_df.to_csv(file_name, index = False)
        
        # Accumulate trial count
        block_trial_count += 1
        
    # Update cumulativ accuracy tracking
    block_pair_correct_responses += correct_responses
    block_pair_trial_count += block_trial_count
    
    # Insert a break every 2 blocks with a feedback message, except after the last one
    if (block_num + 1) % 2 == 0 and block_num < len(all_blocks) -1:
        accuracy = (block_pair_correct_responses / block_pair_trial_count) * 100
        feedback_message = f"Accuracy: {accuracy: .1f}%\n\nTake a short break.\nPress the space bar to continue."

        feedback_display = visual.TextStim(win, text = feedback_message, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        feedback_display.draw()
        win.flip()

        # Wait for a keypress to continue
        keys = event.waitKeys(keyList = ["space", "escape"])
        if "escape" in keys:
            print ("Terminate key pressed. Exiting experiment loop early.")
            terminate_exp = True
            
        elif "space" in keys:
            print(f"Key pressed: {keys}")
            pass
                    
        core.wait(0.1)
        event.clearEvents()
    
# Final save before exit
response_df = pd.DataFrame(all_responses)
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# Close the window after the experiment
# End message
end_text = visual.TextStim(win, text = "Press the space bar to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
event.getKeys(keyList = ["space"])
win.close()
core.quit()