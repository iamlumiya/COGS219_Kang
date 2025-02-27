# Testing phase
# Spoken production - Set 1

from psychopy import visual, event, core, data
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
    save_dir = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/test phase/data"
else: 
    csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
    save_dir = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\testing phase\data"

stimuli_df = pd.read_csv(csv_file)

# Set the number of repetitions
n = 1

# Set up
win = visual.Window([800, 800], color = "black", units = "pix", checkTiming = False)

# Generate timestamped filename for saving data
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(save_dir, exist_ok = True)
file_name = os.path.join(save_dir, f"SP_s1_{timestamp}.csv")

# Initialize a list to store trial data
all_responses = []

# Welcome message
welcome_text = visual.TextStim(win, text = "Speak the correct name aloud. \n\n Press the space bar to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))

welcome_text.draw()
win.flip()

# Wait for space key to start 
start_time = core.getTime()
response = None

while core.getTime() - start_time < 10:
    keys = event.getKeys()
    if "space" in keys:
        response = True
        break
        
if response is None:
    print("No response within 10 seconds. Exiting.")
    win.close()
    core.quit()
    
# Prepare text and image component
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Experiment loop
terminate_exp = False

for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys():
            terminate_exp = True
            break
            
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
        audio_filename = os.path.join(save_dir, f"response_sp_{block+1}_{index+1}.wav")
        
        # 4. Wait for the response (3000ms) + Record the voice
        response_wait.draw()
        win.flip()
        
        # Start recording
        response_start = core.getTime()
        recording = sd.rec(int(duration * fs), samplerate = fs, channels = 1, dtype = "int16")
        sd.wait()
        response_end = core.getTime()
        
        sf.write(audio_filename, recording, fs)
        
        # Compute response time
        rt = response_end - response_start
        
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
            'object': object_name,
            'image': correct_image,
            'response': audio_filename,
            'response_time': rt * 1000 if rt else 0
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(all_responses)
        response_df.to_csv(file_name, index = False)
        
    event.clearEvents()
    
    if terminate_exp:
        break
        
    # Break after every 2 blocks, except after the last trial
    if (block + 1) % 2 == 0 and block + 1 < n:
        break_display = visual.TextStim(win, text = "Take a short break.\n\n Press the space bar to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        break_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to continue
        while True:
            keys =  event.getKeys(keyList = ["space", "escape"])
            if "escape" in keys:
                print("Escape pressed.")
                terminate_exp = True
                break
            elif "space" in keys:
                break
                
    event.clearEvents()
    
# Final save before exit
if all_responses:
    response_df = pd.DataFrame(all_responses)
    response_df.to_csv(file_name, index=False)
    print(f"✅ Response data successfully saved to: {file_name}")
else:
    print("❌ No response recorded. File not saved properly.")

# Close the window after the experiment
# End message
end_text = visual.TextStim(win, text = "Press the space bar to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for response
while not any(event.getKeys(keyList = "space")):
    core.wait(0.1)
    
win.close()
core.quit()
