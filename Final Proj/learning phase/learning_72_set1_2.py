# Combined Learning phase (Initial[24] - Recog[24] - Name[24])

from psychopy import visual, core, event
import pandas as pd
import random
import datetime
import os
import numpy as np
from sys import platform

# Set file path
if platform == "darwin": # macOS
    excel_file_path = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/FIN/data"
    csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
else: # window
    excel_file_path = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\FIN\response"
    csv_file = r"C:\Users\l5kang\Documents\Lumi\Evo_mod\evo_data.csv"

# Function to save response data to CSV
all_responses = []
current_phase = None

def save_to_csv():
    
    if not all_responses:
        return
        
    df = pd.DataFrame(all_responses)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response_file = os.path.join(excel_file_path, f"learning_V_s1_72_{timestamp}.csv")

    # Save to CSV
    df.to_csv(response_file, index = False, lineterminator = "\n")
    print(f"Saved all responses to {response_file}")
    
# Laod stimuli CSV file
stimuli_df = pd.read_csv(csv_file)

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for a mouse click
def show_message(text, timeout = 10):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
    msg.draw()
    win.flip()
    start_time = core.getTime()
    while not any(mouse.getPressed()):
        if core.getTime() - start_time > timeout:
            print (f"No response within {timeout} seconds. Exiting.")
            win.close()
            core.quit()
        core.wait(0.1)


# Initial Presentation - Visual - Set 1
# Welcome message
print("Starting Initial Presentation Phase...")
show_message("Thank you for participating this experiment.\nClick the mouse to start.")

# Prepare text and image components
current_phase = "Initial_Presentation"
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', height = 35, pos =(0,150))
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))


# Set the number of repetitions
n = 2

for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            break
            
        # 1. Select a random pair of an image and a name
        object_image = row['visual_s1']
        correct_name = row['name_s1']
                
        # 2. Display an image with the name for 2 seconds
        image_display.image = object_image
        name_display.text = correct_name
        image_display.draw()
        name_display.draw()
        win.flip()
        core.wait(2)
        
        # Record the response data       
        all_responses.append({
            'phase': current_phase,
            'block': block + 1,
            'trial': index + 1,
            'object_name': correct_name,
            'object_image': object_image
        })
        
        # Blank space
        win.flip()
        core.wait(1.5)

# End message
show_message("Click the mouse to move to the next phase.")
print("Completed Initial Presentation Phase.\n")
core.wait(0.1)

event.clearEvents()

# Recognition Training - Visual - Set 1
# Welcome message
current_phase = "Recognition_training"
print("Starting Recognition Training Phase...")
core.wait(0.1)
show_message("Choose the correct image of the name on the screen.\n\n Click the mouse to start.")

# Define the image and text positions
image_positions = [(-200, 200), (200, 200), (-200, -200), (200, -200)]

# Prepare text and image component
name_display = visual.TextStim(win, text ="", font ='Arial', height = 35, color = 'white', pos =(0, 0))
image_stims = [visual.ImageStim(win, pos = pos, size = (250, 250)) for pos in image_positions]
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = 'white', pos = (0, 0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))

# Set the number of repetitions
n2 = 2

# Experiment loop
terminate_exp = False
event.clearEvents()

# Reset mouse position to center
mouse.setPos((0,-30))

for block in range(n2):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList=["escape"]):
            core.quit()
        
        #1. Select a random name and its corresponding image
        object_name = row['name_s1']
        correct_image = row['visual_s1']
        
        #2. Select three distractor images (excluding the correct image)
        distractor_images = random.sample([img for img in stimuli_df['visual_s1'] if img != correct_image], 3)
        
        #3. Form the image set (1 correct + 3 distractors) and shuffle
        image_paths = distractor_images + [correct_image]
        random.shuffle(image_paths)
        
        #4. Display images with numbers
        for stim, img_path in zip(image_stims, image_paths):
            stim.setImage(img_path)
            stim.draw()
        
        win.flip()
        core.wait(1)
        
        #5. Display an object name with four images
        name_display.setText(object_name)
        name_display.draw()
        for stim in image_stims:
            stim.draw()
        
        win.flip()

        #6. Wait for participants to respond by clicking
        responseTimer = core.Clock()
        responseTimer.reset()

        response = None
        selected_image = None
        rt = None
        is_correct = False
        
        start_time = core.getTime()
        while core.getTime() - start_time < 3:
            if "escape" in event.getKeys():
                core.quit()
            
            if mouse.getPressed()[0]: # IF left click detected
                for i, stim in enumerate(image_stims):
                    if stim.contains(mouse):
                       selected_image = image_paths[i]
                       is_correct = (selected_image == correct_image)
                       rt = responseTimer.getTime()
                       response = selected_image
                       break
                       
                break
        core.wait(0.1)
            
        #7. Provide feedback
        feedback_display.setText("Correct" if is_correct else "Incorrect")
        feedback_display.draw()
        win.flip()
        core.wait(1.5)
       
        # Blalnk screen
        win.flip()
        core.wait(1.5)
        
        # Reset mouse position to center
        mouse.setPos((0,-30))
        
        # Record the response data       
        all_responses.append({
            'phase': current_phase,
            'block': block + 1,
            'trial': index + 1,
            'object_name': object_name,
            'object_image': correct_image,
            'selected_image': selected_image,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else np.nan
        })
        
    event.clearEvents()
    
    
    # Break after every two blocks, except the last one
    if (block+1) % 2 == 0 and block + 1 < n2:
        break_display.draw()
        win.flip()
        
        # Wait for a response
        while not any(mouse.getPressed()):
            core.wait(0.1)
        
    core.wait(0.1)
    event.clearEvents()

# End message
event.clearEvents()
print("Completed Recognition Training Phase.\n")
show_message("Click the mouse to move to the next phase.")
core.wait(0.1)
 
# Name learning - Visual - Set 1
# Welcome message
print("Starting Name Learning Phase...")
current_phase = "Name_Learning"
show_message("Choose the correct name for the image on the screen.\n\nClick the mouse to start.")

# Define the text position
name_positions = [(0, -50), (0, -100), (0, -150), (0, -200)]  

# Prepare text and image components
name_stims = [visual.TextStim(win, text = "", font = "Arial", height = 35, color = "white", pos = name_positions[i]) for i in range(4)]
image_display = visual.ImageStim(win, image = None, size = (250, 250), pos = (0, 100))
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = "white", pos = (0, 0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))


# Set the number of repetitions
n3 = 2

# Experiment loop
terminate_exp = False
event.clearEvents()

# Reset mouse position to center
mouse.setPos((0, 100))

for block in range(n3):
    
    # Shuffle the stimuli order for n blocks 
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList=["escape"]):
            break
            
        # 1. Select a random image and its corresponding name
        object_image = row['visual_s1']
        correct_name = row['name_s1']
        
        # 2. Select three distractor names (excluding the correct name)
        distractor_names = random.sample([name for name in stimuli_df['name_s1'] if name != correct_name], 3)
        
        # 3. Form the name set (1 correct + 3 distractors) and shuffle
        name_choices = distractor_names + [correct_name]
        random.shuffle(name_choices)
        
        # 4. Display an image
        image_display.image = object_image
        image_display.draw()
        win.flip()
        core.wait(2)
        
        # 5. Display names with numbers
        for stim, name_text in zip(name_stims, name_choices):
            stim.setText(name_text)
            stim.draw()
        
        image_display.draw()
        win.flip()
        
        # 6. Wait for participants to respond by clicking
        responseTimer = core.Clock()
        responseTimer.reset()
        
        response = None
        selected_name = None
        rt = None
        is_correct = False
        
        start_time = core.getTime()
        
        while core.getTime() - start_time < 3:
            if "escape" in event.getKeys():
                core.quit()
                
            if mouse.getPressed()[0]:
                for i, stim in enumerate(name_stims):
                    if stim.contains(mouse):
                        selected_name = name_choices[i]
                        is_correct = (selected_name == correct_name)
                        rt = responseTimer.getTime()
                        response = selected_name
                        break
                break
            core.wait(0.1)
                
        # 7. Provide feedback
        feedback_display.setText("Correct" if is_correct else "Incorrect")
        feedback_display.draw()
        win.flip()
        core.wait(1.5)
        
        # Blank screen
        win.flip()
        core.wait(1)
        
        # Reset mouse position to the center
        mouse.setPos((0, 100))
        
        # Record the response data
        all_responses.append({
            'phase': current_phase,
            'block': block + 1,
            'trial': index + 1,
            'object_name': correct_name,
            'object_image': object_image,
            'selected_name': selected_name,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else np.nan
        })
        
    event.clearEvents()
    
    # Break after every two blocks, except the last one
    if (block+1) % 2 == 0 and block + 1 < n3:
        break_display.draw()
        win.flip()
        
        # Wait for a response
        while not any(mouse.getPressed()):
            core.wait(0.5)
        
    core.wait(0.1)
    event.clearEvents()


# Final save before exit
print("Completed Name Learning Phase.\n")
save_to_csv()
 
# Close the window after the experiment
# End message
show_message("You've completed all the training phases.\n\nClick the mouse to exit.")

    
win.close()
core.quit()
