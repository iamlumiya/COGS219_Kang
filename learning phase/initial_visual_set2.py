# Learning phase
# Initial Presentation Block - Visual - Set 2

from psychopy import visual, core, event, data
import pandas as pd
import random

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# # Repeat stimuli 3 times to get 36 trials
stimuli_df = pd.concat([stimuli_df] * 3, ignore_index = True)

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True) 

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Combine both image and object into one list of trials
trials = list(zip(stimuli_df['visual_s2'], stimuli_df['name_s2']))
random.shuffle(trials)

# Welcome message
welcome_text = visual.TextStim(win, text = "Click the mouse to start.", font = 'Arial', color = 'white', pos = (0,0))
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
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', pos =(0,-250))
image_display = visual.ImageStim(win, image = None, size = [400,400], pos = (0,0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', pos = (0,0))

# Experiment loop
terminate_exp = False

for trials, (image_path, name_text) in enumerate(trials):
    # Check for an exit key
    keys = event.getKeys(keyList = ["escape"])
    if "escape" in keys:
        print ("Terminate key pressed. Exiting experiment loop early.")
        break
    
    # Update stimuli
    image_display.image = image_path
    name_display.text = name_text
    
    # Display an image with the name for 2 seconds
    image_display.draw()
    name_display.draw()
    win.flip()
    core.wait(2)
    
    # Blank space
    win.flip()
    core.wait(0.5)
    
    # Close the window after 36 trials
    if trials  == 35:
        end_text = visual.TextStim(win, text = "The end.\nClick the mouse to exit.", font = 'Arial', color = 'white', pos = (0,0))
        end_text.draw()
        win.flip()

while not any(mouse.getPressed()):
    pass

win.close()
core.quit()

