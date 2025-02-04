# Test phase
# Visual comprehesino - Set 1

from psychopy import visual, event, core, data, logging, gui
from datetime import datetime
import pandas as pd
import random

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Repeat stimuli 4 times to get 48 trials
stimuli_df = pd.concat([stimuli_df] * 4, ignore_index = True)

# Shuffle the rows to randomize trial order
stimuli_df = stimuli_df.sample(frac = 1).reset_index(drop = True) 

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Load all image paths from the column into a list
all_images = list(stimuli_df['visual_s1'])
random.shuffle(all_images)

# Initialize a list to store trial data
response_data = []

# Welcome message
welcome_text = visual.TextStim(win, text = "Click LEFT if match, RIGHT if mismatch.\nClick the mouse to start.", font = 'Arial', color = 'white', pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for mouse click with a timeout
start_time = core.getTime()
while not any(mouse.getPressed()):
    if core.getTime() - start_time > 10:
        print("No response within 10 seconds. Exiting.")
        win.close()
        core.quit()

# Prepare text and image components
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', pos = (0,0))
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', pos =(0,0))
image_display = visual.ImageStim(win, image = None, size = [400,400], pos = (0,0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', pos = (0,0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', pos = (0,0))

# Experiment loop
terminate_exp = False # Flag to control early termination

for trial in range(48):
    # Check for an exit key
    keys = event.getKeys(keyList = ["esc"])
    if "esc" in keys:
        print ("Terminate key pressed. Exiting experiment loop early.")
        break
    
    row = stimuli_df.iloc[trial]
    match_image = row['visual_s1']
    object_name = row['name_s1']

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
    image_path = selected_image
    image_display.setImage(image_path)
    
    name_display.setText(object_name)
    name_display.draw()
    win.flip()
    core.wait(2)


    #3 Visual display of the object either matching or not matching that name
    image_display.setImage(selected_image)
    image_display.draw()
    win.flip()
    core.wait(2)

    #4 Participants needs to decide whether the object and name match (3000ms max)
    response_wait.draw()
    win.flip()
    
    # Start timing precisely when the response prompt appears
    start_time = core.getTime()

    #5 Mouse-clicking
    response = None
    rt = None

    while core.getTime () - start_time < 3:
    
        # Check for early exit during the experiment
        keys = event.getKeys(keyList = ["esc"])
        if "esc" in keys:
            print("Escape key pressed during the experiment. Exiting the experiment early.")
            terminate_exp = True
            break # Exit the while loop and go to saving data
            
        buttons, times = mouse.getPressed(getTime = True)
        if buttons[0]:
            response = "match"
            rt = core.getTime() - start_time
            break
        elif buttons[1]:
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
    
    # Insert a break every 12 trials, except after the last trial
    if (trial + 1) % 12 == 0 and (trial +1) < 48:
        break_display.draw()
        win.flip()
        
        # Reset the mouse click status before waiting for a new click
        mouse.clickReset()
        
        # Wait for a mouse click to resume
        while True:
            buttons, times = mouse.getPressed(getTime = True)
            if buttons[0] or buttons[1]: # Left or right click
                break
            keys = event.getKeys(keyList=["esc"])
            if "esc" in keys:
                print ("Terminate key pressed. Exiting experiment loop early.")
                terminate_exp = True
                break
        core.wait(0.1)


# Save the response to a CSV file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f'/Users/lumikang/Documents/UCSD/25/Evo_Mod/test phase/Comprehension/response/s1_response_{timestamp}.csv'
response_df = pd.DataFrame(response_data)
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")

# Close the window after the experiment
# Welcome message
end_text = visual.TextStim(win, text = "Click the mouse to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
while not any(mouse.getPressed()):
    win.close()
    core.quit()
