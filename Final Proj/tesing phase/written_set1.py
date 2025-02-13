# Test phase
# Written production - Set 1

from psychopy import visual, event, core, data
import datetime
import pandas as pd
import random
import os

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
#csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Set the number of repetitions
n = 4

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Load all image paths from the column into a list
all_images = list(stimuli_df['visual_s1'])

# Initialize a list to store trial data
response_data = []

# Generate timestamped filename for saving data
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_dir = "/Users/lumikang/Documents/UCSD/25/Evo_Mod"
#save_dir = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\rec_response"
os.makedirs(save_dir, exist_ok = True)
file_name = os.path.join(save_dir, f"WP_s1_{timestamp}.csv")

# Welcome message
welcome_text = visual.TextStim(win, text = "Press the space bar to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
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
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0,0))
input_display = visual.TextStim(win, text = "", font = 'Arial', color = 'white', height = 30, pos = (0, -150))

# Experiment loop
terminate_exp = False

for block in range(n):
    
    # shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for trial, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList=["escape"]):
            terminate_exp = True
            break
    
        # 1. Select a random image and its corresponding name
        selected_row = stimuli_df.sample(1).iloc[0]
        object_image = selected_row['visual_s1']
        correct_name = selected_row['name_s1']
        
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
        
        while True:
            image_display.draw()
            input_display.text = typed_name
            input_display.draw()
            win.flip()
            
            keys = event.waitKeys()
            for key in keys:
                if key == "return":
                    break
                elif key == "backspace":
                    typed_name == typed_name[:-1]
                elif key == "escape":
                    terminate_exp = True
                    break
                else:
                    typed_name += key
        
        if "return" in keys or terminate_exp:
            break
        
        rt = response_timer.getTime()
        is_correct = typed_name.strip().lower() == correct_name.strip().lower()
        
        # If no response within 5 seconds, mark it as "no response"
        if responseTime.getTime () > 5:
            response = "no response"
            selected_name = "no response"
            rt = 0
            is_correct = False
            break
        
        if terminate_exp:
            break
        
        win.flip()
        
        # 5. Display fixation cross; inter-trial interval
        fixation_display.draw()
        win.flip()
        core.wait(1)
        
        # Record the response data
        response_data.append({
            'block': block + 1,
            'trial': trial + 1,
            'object': object_image,
            'typed_name': selected_name,
            'correct_name': correct_name,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else 0
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(response_data)
        response_df.to_csv(file_name, index = False)
        
        event.clearEvents()
    
    if terminate_exp:
        break
    
    # Break after every 12 tirals, except after the last trial
    if block < n -1:
        break_display = visual.TextStim(win, text = "Take a short break.\n\n Press the space bar to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        break_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to continue
        keys = event.waitKeys(keyList = ["space", "escape"])
        
        if keys:
            if "escape" in keys:
                print("Terminate key pressed. Exiting experiment loop early")
                terminate_exp = True
            elif "space" in keys:
                print("Continue key pressed.")
                pass
        core.wait(0.1)
        
        event.clearEvents()
        
# Final save before exit
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# Close the window after the experiment
# End message
end_text = visual.TextStim(win, text = "Press the space bar to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
while not any(event.getKeys(keyList = "space")):
    core.wait(0.1)
    
win.close()
core.quit()
        
    
        