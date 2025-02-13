# Test phase
# Visual comprehesion - Set 2

from psychopy import visual, event, core, data
import datetime
import pandas as pd
import random
import os

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
#csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True) 

# Set the number of repetitions
n = 2

# Generate a balanced block of trials with randomized match/mismatch
def create_block():
    unique_names = list(stimuli_df['name_s2'].unique())
    random.shuffle(unique_names)
    
    # Split the names into 6 for match and 6 for mismatch
    match_names = unique_names[:6]
    mismatch_names = unique_names[6:]
    
    match_trials = []
    mismatch_trials = []

    # Load all image path
    all_images = list(stimuli_df['visual_s2'])
    
    # Create match trials: use the correct image
    for name in match_names:
        row = stimuli_df[stimuli_df['name_s2'] == name].iloc[0]
        match_trials.append({
        'name': name,
        'image': row['visual_s2'],
        'match': True
        })
        
    # Create mismatch trials: use an incorrect image
    for name in mismatch_names:
        row = stimuli_df[stimuli_df['name_s2'] == name].iloc[0]
        # Select an image that is not the correct one
        incorrect_images = [img for img in all_images if img !=row['visual_s2']]
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
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Initialize a list to store trial data
response_data = []

# Generate timestamped filename for saving data
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_dir = "/Users/lumikang/Documents/UCSD/25/Evo_Mod"
#save_dir = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\rec_response"
os.makedirs(save_dir, exist_ok = True)
file_name = os.path.join(save_dir, f"Vcomp_s2_{timestamp}.csv")

# Welcome message
welcome_text = visual.TextStim(win, text = "Click 1 if match, 2 if mismatch.\n\nPress either 1 or 2 to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for keyboard press with a timdeout
start_time = core.getTime()
response = None

while core.getTime() - start_time < 10:
    keys = event.getKeys()
    if keys:
        if '1' in keys or '2' in keys:
            response = keys[0]
            print(f"Key pressed: {response}")
            break
            
if response is None:
    print("No response within 10 seconds. Exiting.")
    win.close()
    core.quit()

# Prepare text and image components
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', height = 35, pos =(0,0))
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Experiment loop
terminate_exp = False  
event.clearEvents()

for block_num, block in enumerate(all_blocks):
    correct_responses = 0 # Track correct responses for this block
    
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
        core.wait(2)

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
        response_data.append({
            'block_number': block_num + 1,
            'trail_number': trial_num + 1,
            'object_name': selected_name,
            'selected_image': selected_image,
            'match': is_match,
            'response': response,
            'response_time(ms)': rt * 1000
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(response_data)
        response_df.to_csv(file_name, index = False) 
        
    # Insert a break every 12 trials with a feedback message, except after the last trial
    if block_num < len(all_blocks) - 1:
        accuracy = (correct_responses / 12) * 100
        feedback_message = f"Accuracy: {accuracy: .1f}%\n\nTake a short break.\nPress 1 or 2 to continue."
        
        feedback_display = visual.TextStim(win, text = feedback_message, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        feedback_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to contitnue
        keys = event.waitKeys(keyList = ["1", "2", "escape"])
        
        if keys:
            if "escape" in keys:
                print ("Terminate key pressed. Exiting experiment loop early.")
                terminate_exp = True
            elif "1" in keys or "2" in keys:
                print(f"Key pressed: {keys}")
                pass
                
        core.wait(0.1)
        
        event.clearEvents()


# Final save before exit
response_df = pd.DataFrame(response_data)
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# Close the window after the experiment
# End message
end_text = visual.TextStim(win, text = "Press either 1 or 2 to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
event.getKeys(keyList = ["1", "2"])
win.close()
core.quit()
