# Learning phase
# Initial Presentation Block - Auditory - Set 1

from psychopy import visual, core, event, data, sound
import pandas as pd
import random
import datetime
import os
from sys import platform

# Set file path
if platform == "darwin": # macOS
    excel_file_path = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/learning phase/data"
    csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
else: #window
    excel_file_path = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\learning phase\data"
    csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
    
# Generate timestamped file name
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(excel_file_path, exist_ok = True)
file_name = os.path.join(excel_file_path, f"initial_aud_{timestamp}.csv")

# Load the stimuli CSV file into a dataframe
stimuli_df = pd.read_csv(csv_file)

# Function to save response data to CSV
all_responses = []

# Set the number of repetitions
n = 3

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Welcome message
welcome_text = visual.TextStim(win, text = "Click the mouse to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for mouse click with a timeout (10 seconds)
start_time = core.getTime()
while not any(mouse.getPressed()):
    if core.getTime() - start_time > 10:
        print("No response within 10 seconds. Exiting.")
        win.close()
        core.quit()

# Prepare text and image components
# fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))

# Experiment loop
terminate_exp = False

for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():    
    
    # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            terminate_exp = True
            break
            
        # 1. Select a random pair of an image and a name
        object_image = row['visual_s1']
        correct_name = row['auditory_s1']
    
        # Update stimuli
        image_display.image = object_image
        name_audio = sound.Sound(correct_name, stopTime = 2)
    
        # 2. Display an image with the name for 2 seconds
        image_display.draw()
        win.flip()
        name_audio.play()
        core.wait(2)
        
        # Record the reesponse data 
        all_responses.append({
        'block': block + 1,
        'trial': index + 1,
        'object_name': correct_name,
        'object_image': object_image
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(all_responses)
        response_df.to_csv(file_name, index = False)
        
        # 3. Blank space
        win.flip()
        core.wait(1.5)
    
    if terminate_exp:
        break
        
# Final save before exit
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# End message after compeleting 36 trials
end_text = visual.TextStim(win, text = "The end.\nClick the mouse to exit.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
end_text.draw()
win.flip()

while not any(mouse.getPressed()):
    pass

win.close()
core.quit()