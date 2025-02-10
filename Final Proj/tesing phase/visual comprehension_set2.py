# Test phase
# Visual comprehesino - Set 2

from psychopy import visual, event, core, data
import datetime
import pandas as pd
import random
import os

# Load the stimuli CSV file into a dataframe
csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Repeat stimuli 8 times to get 96 trials
stimuli_df = pd.concat([stimuli_df] * 2, ignore_index = True)

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True) 

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Load all image paths from the column into a list
all_images = list(stimuli_df['visual_s2'])
random.shuffle(all_images)

# Initialize a list to store trial data
response_data = []

# Generate timestamped filename for saving data
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_dir = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\rec_response"
os.makedirs(save_dir, exist_ok = True)
file_name = os.path.join(save_dir, f"recog_s2_{timestamp}.csv")

# Welcome message
welcome_text = visual.TextStim(win, text = "Click 1 if match, 2 if mismatch.\nPress either 1 or 2 to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for mouse click with a timdeout
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
break_display = visual.TextStim(win, text = "Take a short break.\nPress 1 or 2 to continue.", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Experiment loop
terminate_exp = False # Flag to control early termination

for trial in range(24):
    # Check for an exit key
    keys = event.getKeys(keyList = ["escape"])
    if "escape" in keys:
        print ("Terminate key pressed. Exiting experiment loop early.")
        break
    
    row = stimuli_df.iloc[trial]
    match_image = row['visual_s2']
    object_name = row['name_s2']

    # Decide whether to present a matching or mismatching image
    if random.choice([True, False]):
        selected_image = match_image
        is_match = True
    else:
        selected_image = random.choice([img for img in all_images if img != match_image])
        is_match = False
    
    # Debugging print statement
    print(f"Trial {trial + 1}: Name = {object_name}, Image = {selected_image}, Match = {is_match}")
    
    #1 Each trial begins with a fixation cross (0.5s)
    fixation_display.draw()
    win.flip()
    core.wait(0.5)

    #2 Display the name (2s)
    name_display.setText(object_name)
    name_display.draw()
    win.flip()
    core.wait(2)

    #3 Visual display of the object either matching or not matching that name
    image_display.setImage(selected_image)
    image_display.draw()
    win.flip()
    core.wait(1)

    #4 Participants needs to decide whether the object and name match (3000ms max)
    response_wait.draw()
    win.flip()
    
    # Start timing precisely when the response prompt appears
    start_time = core.getTime()
    response = None
    rt = None

    while core.getTime () - start_time < 3:
    
        # Check for early exit during the experiment
        keys = event.getKeys(keyList = ["escape", "1", "2"])
        if "escape" in keys:
            print("Escape key pressed during the experiment. Exiting the experiment early.")
            terminate_exp = True
            break # Exit the while loop and go to saving data
        
        if "1" in keys:
            response = "match"
            rt = core.getTime() - start_time
            break
        elif "2" in keys:
            response = "mismatch"
            rt = core.getTime() - start_time
            break
        
    # If exit was triggered inside the while loop, break the main loop as well
    if terminate_exp:
        break
    
    # If no response within 3 seconds, mark is as "no response"
    if response is None:
        response = "no response"
        rt = None

    # Debugging print
    print(f"Response: {response}, Response Time: {rt:.3f} sec" if rt is not None else "No response")

    #6 1-second blank screen
    fixation_display.draw()
    win.flip()
    core.wait(1)

    # Record the response data
    response_data.append({
        'trial_number': trial + 1,
        'object_name': object_name,
        'selected_image': selected_image,
        'match': is_match,
        'response': response,
        'response_time': rt
    })
    
    # Save progress after every trial
    response_df = pd.DataFrame(response_data)
    response_df.to_csv(file_name, index = False) 
    
    # Insert a break every 12 trials, except after the last trial
    if (trial + 1) % 12 == 0 and (trial +1) < 24:
        break_display.draw()
        win.flip()
        
        # Wait for a keypress to contitnue
        event.waitKeys(keyList = ["1", "2"])
        
        # Check for early exit
        keys = event.getKeys(keyList=["escape"])
        if "escape" in keys:
            print ("Terminate key pressed. Exiting experiment loop early.")
            terminate_exp = True
            break
            
        core.wait(0.1)


# Final save before exit
response_df = pd.DataFrame(response_data)
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# Close the window after the experiment
# Welcome message
end_text = visual.TextStim(win, text = "Press either 1 or 2 to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
event.getKeys(keyList = ["1", "2"])
win.close()
core.quit()
