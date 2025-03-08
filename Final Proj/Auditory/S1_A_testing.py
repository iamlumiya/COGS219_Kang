# Testing phase - Auditory - Set 1

from psychopy import visual, event, core, data, sound
import datetime
import pandas as pd
import random
import os
from sys import platform
import sounddevice as sd
import soundfile as sf
import numpy as np

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
    response_file = os.path.join(save_dir, f"testing_V_s1_{timestamp}.csv")

    # Save to CSV
    df.to_csv(response_file, index = False, lineterminator = "\n")
    print(f"Saved all responses to {response_file}")
    
# Laod stimuli CSV file
stimuli_df = pd.read_csv(csv_file)

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for the space bar pressed
def show_message(text):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
    msg.draw()
    win.flip()

    while True:
        keys = event.getKeys()
        if "space" in keys:
            break
        core.wait(0.1)

# Auditory comprehension
print("Starting Auditory Comprehension Phase...")
current_phase = "Auditory_comprehension"

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

# Welcome message
show_message("Press LEFT arrow key if match, RIGHT arrow key if mismatch when \"?\" appears on the screen. \n\nPress the space bar to start.")

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
    block_trial_count = len(block)
    
    for trial_num, trial in enumerate(block):
        event.clearEvents()
        
        selected_name = trial['name']
        selected_image = trial['image']
        is_match = trial['match']
    
        # Check for an exit key
        keys = event.getKeys(keyList = ["escape"])
        if "escape" in keys:
            terminate_exp = True
            break
            
        # 1. Each trial begins with a fixation cross (500ms)
        fixation_display.draw()
        win.flip()
        core.wait(0.5)
        
        # 2. Audio play with a fixation cross (200ms)
        name_audio = sound.Sound(selected_name, stopTime = 0.9)
        name_audio.play()
        fixation_display.draw()
        win.flip()
        core.wait(0.9)
        
        # 3. Visual display of the object either matching or not matching that name (200ms)
        image_display.setImage(selected_image)
        image_display.draw()
        win.flip()
        core.wait(0.2)
        
        # 4. Blank space (800ms)
        win.flip()
        core.wait(0.8)
        
        # 5. Participants needs to decide whether the object and name match (3000ms max)
        response_wait.draw()
        win.flip()
        event.clearEvents()
        
        # 5-1. Start timing precisely when the response prompt appear
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
            
        # 6. 1-second blank screen
        fixation_display.draw()
        win.flip()
        core.wait(1)
    
        # Record the response data
        all_responses.append({
            'phase': current_phase,
            'block': block_num + 1,
            'trial': trial_num + 1,
            'object_name': selected_name,
            'selected_image': selected_image,
            'match': is_match,
            'response': response,
            'response_time': rt * 1000 if rt else 0
        })

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
        
        # Reset block_pair accuracy tracking
        block_pair_correct_responses = 0
        event.clearEvents()
        
# End message
print("Completed Auditory Comprehension Phase.")
show_message("Press the space bar to move to the next phase.")
core.wait(0.1)

event.clearEvents()

# Spoken Production
print("Starting Spoken Production Phase...")
current_phase = "Spoken_production"
core.wait(0.1)

# Welcome message
show_message("Speak the correct name alound.\n\n Press the space bar to start.")

# Prepare text and image component
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Extract the filename without the extension
csv_filename = os.path.splitext(os.path.basename(csv_file))[0]

# Define the folder path inside the save directory
folder_path = os.path.join(save_dir, csv_filename)

# Create the directory if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

# Set the number of repetitions
n2 = 4

# Experiment loop
terminate_exp = False
event.clearEvents()

for block in range(n2):
    # Shuffle the stimuli order for n2 blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        # Check for an exit key
        if "escape" in event.getKeys():
            terminate_exp = True
            core.quit()
            
        # 1. Select a random image and its corresponding name
        object_name = row['auditory_s1']
        correct_image = row['visual_s1']
        
        random.shuffle([correct_image])
        
        # 2. Display fixation cross
        fixation_display.draw()
        win.flip()
        core.wait(0.5)
        
        # 3. Display the image (2000ms)
        image_display.image = correct_image
        image_display.draw()
        win.flip()
        core.wait(2)
        
        # Recording settings
        fs = 44100
        duration = 3
        audio_filename = os.path.join(folder_path, f"response_sp_{block+1}_{index+1}.wav")
        
        # 4. Wait for the response (3000ms) + record the voice
        # Set default color to white
        response_wait.color = 'white'
        response_wait.draw()
        win.flip()
        
        # Change color to green when recording starts
        response_wait.color = [-0.61, 0.61, -0.61]
        response_wait.draw()
        win.flip()
        
        # Start recording
        response_start = core.getTime()
        recording = sd.rec(int(duration* fs), samplerate = fs, channels = 1, dtype = "int16")
        sd.wait()
        response_end = core.getTime()
        
        sf.write(audio_filename, recording, fs)
        
        # Compute response time
        rt = response_end - response_start
        
        # Change color to red for 0.2 seconds after recording finishes
        response_wait.color = 'red'
        response_wait.draw()
        win.flip()
        core.wait(0.2)
        
        # Stop recording
        core.wait(3)
        
        # 5. Blank space (1000ms)
        fixation_display.draw()
        win.flip()
        core.wait(1)
        
        # Record the response data 
        all_responses.append({
            'block': block + 1,
            'trial': index + 1,
            'object_name': object_name,
            'selected_image': correct_image,
            'response': audio_filename,
            'response_time': rt * 1000 if rt else 0
        })
        
        event.clearEvents()
        
    if terminate_exp:
        core.quit()
        
    # Break after every 12 trials, except after the last trial
    if (block + 1) % 2 == 0 and block + 1 <n2:
        break_display = visual.TextStim(win, text = "Take a short break.\n\n Press the space bar to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        break_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to continue
        while True:
            keys = event.getKeys(keyList = ["space", "escape"])
            if "escape" in keys:
                terminate_exp = True
                break
            elif "space" in keys:
                break
        event.clearEvents()

# Final save before exit
print("Completed Spoken Production Phase.")
save_to_csv()

# Close the window after the experiment
# End message
show_message("You've completed all the testing phases.\n\n Press the space bar to exit.")

win.close()
core.quit()

