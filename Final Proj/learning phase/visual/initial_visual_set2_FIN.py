# Learning phase
# Initial Presentation Block - Visual - Set 2

from psychopy import visual, core, event, data, gui
import pandas as pd
import random
import datetime
import os

# Generate subj_code based on timestamp
subj_code = "initial_v_s2_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"Generated Subject Code: {subj_code}")

# Load the stimuli CSV file into a dataframe
#csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Set the number of repetitions
n = 2

# Create data file
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok = True)

data_file_path = os.path.join(data_dir, subj_code +'_data.csv')
data_file = open(data_file_path, 'w')

separator = ','
data_file.write(separator.join(["subj_code", "block", "trial", "object_image", "correct_name"]) + '\n')

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
# fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'blue', pos = (0,0))
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', height = 35, pos =(0,150))
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))

# Experiment loop
terminate_exp = False
for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for trial_idx, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            terminate_exp = True
            break
            
        # 1. Select a random pair of an image and a name
        object_image = row['visual_s2']
        correct_name = row['name_s2']
                
        # 2. Display an image with the name for 2 seconds
        image_display.image = object_image
        name_display.text = correct_name
        image_display.draw()
        name_display.draw()
        win.flip()
        core.wait(2)
        
        # Blank space
        win.flip()
        core.wait(1.5)
    
        # Write trial data
        data_file.write(separator.join([subj_code, str(block +1), str(trial_idx +1), object_image, correct_name]) + '\n')
        
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