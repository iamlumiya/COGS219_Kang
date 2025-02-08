# Learning phase
# Initial Presentation Block - Auditory - Set 2

from psychopy import visual, core, event, data, sound
import pandas as pd
import random
import datetime
import os

# Generate subj_code based on timestamp
subj_code = "initial_a_s2_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"Generated Subject Code: {subj_code}")

# Load the stimuli CSV file into a dataframe
csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# # Repeat stimuli 3 times to get 36 trials
stimuli_df = pd.concat([stimuli_df] * 3, ignore_index = True)

# Convert to list of tuples (object, name) and shuffle them
trials = list(zip(stimuli_df['visual_s2'], stimuli_df['auditory_s2']))

# Create data file
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok = True)

data_file_path = os.path.join(data_dir, subj_code +'_data.csv')
data_file = open(data_file_path, 'w')

separator = ','
data_file.write(separator.join(["subj_code", "image_path", "audio_path"]) + '\n')

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
for i in range (0, len(trials), 12):
    # Shuffle the next block of 12 trials
    block = trials[i: i+12]
    random.shuffle(block)
    
    for image_path, audio_path in block:
        # Check for an exit key
        keys = event.getKeys(keyList = ["escape"])
        if "escape" in keys:
            print ("Terminate key pressed. Exiting experiment loop early.")
            terminate_exp = True
            break
        
        trials.append([subj_code, image_path, audio_path]) 
        
        # Debugging: Check if audio file exists
        if not os.path.exists(audio_path):
            print(f"Warning: Audio file not found - {audio_path}")
            continue
    
        # Update stimuli
        image_display.image = image_path
        name_audio = sound.Sound(audio_path, stopTime = 2)
        
        # Display an image with the name for 2 seconds
        image_display.draw()
        win.flip()
        name_audio.play()
        core.wait(2)
        
        # Blank space
        win.flip()
        core.wait(1.5)
        
        # Write trial data
        data_file.write(separator.join([subj_code, image_path, audio_path]) + '\n')

    if terminate_exp:
        break
    
# End message after completing 36 trials
end_text = visual.TextStim(win, text = "The end.\nClick the mouse to exit.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
end_text.draw()
win.flip()

while not any(mouse.getPressed()):
    pass
    
data_file.close()
win.close()
core.quit()

