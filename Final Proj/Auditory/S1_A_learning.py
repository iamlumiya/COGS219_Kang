# Combined Learning Phase - Auditory - Set 1
# Initial(24) - Recognition(24) - Initial(24) - Name (24)

from psychopy import visual, core, event, sound
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

# Function to save response data to Excel
all_responses = []
current_phase = None

def save_to_csv():
    
    if not all_responses:
        return
        
    df = pd.DataFrame(all_responses)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response_file = os.path.join(excel_file_path, f"learning_A_s1_96_{timestamp}.csv")

    # Save to CSV
    df.to_csv(response_file, index = False, lineterminator = "\n")
    print(f"Saved all responses to {response_file}")

# Laod stimuli CSV file
stimuli_df = pd.read_csv(csv_file)

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for a mouse click
def show_message(text):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
    msg.draw()
    win.flip()
    
    while not any(mouse.getPressed()):
        core.wait(0.1)
        
# Initial Presentation Block
# Welcome message
print("Starting Initial Presentation Phase...")
current_phase = "Initial_Presentation_1"
show_message("Welcome to Brain & Cognition Lab.\n\n Click the mouse to start the training.")

# Prepare text and image components
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))

# Set the number of repetitions
n = 2
mouse = event.Mouse(visible = False, win = win)

for block in range(n):

    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            break
            
        # 1. Select a random pair of an image and a name
        object_image = row['visual_s1']
        correct_name = row['auditory_s1']
        
        # 2. Display an image with the name for 2 seconds
        image_display.image = object_image
        name_audio = sound.Sound(correct_name, stopTime = 1.5)
        image_display.draw()
        win.flip()
        name_audio.play()
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
mouse = event.Mouse(visible = True, win = win)
show_message("Click the mouse to move to the next phase.")
print("Completed Initial Presentation Phase.\n")
core.wait(0.1)

event.clearEvents()

# Recognition Training
# Welcome message
print("Starting Recognition Training Phase...")
current_phase = "Recognition_training"
core.wait(0.1)
show_message("Choose the correct image of the name on the screen.\n\n Click the mouse to start.")
        
# Define the image and text positions
image_positions = [(-200, 200), (200, 200), (-200, -200), (200, -200)]

# Prepare text and image component
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
            break
            
        #1. Select a random name and its corresponding image
        object_name = row['auditory_s1']
        correct_image = row['visual_s1']
        
        #2. Select three distractor images (excluding the correct image)
        distractor_images = random.sample([img for img in stimuli_df['visual_s1'] if img != correct_image], 3)
        
        #3. Form the image set (1 correct + 3 distractors) and shuffle
        image_paths = distractor_images + [correct_image]
        random.shuffle(image_paths)
        
        #4. Display images
        for stim, img_path in zip(image_stims, image_paths):
            stim.setImage(img_path)
            stim.draw()
        
        win.flip()
        core.wait(1)
        
        #5. Play the audio file with four images
        name_audio = sound.Sound(object_name, stopTime = 2)
        name_audio.play()
        for stim in image_stims:
            stim.draw()
        
        win.flip()
        
        #6. Wait for participants to respond by clicking
        responseTimer = core.Clock()
        responseTimer.reset()

        response_given = False
        response = None
        selected_image = None
        rt = None
        is_correct = False
        
        start_time = core.getTime()
        
        while core.getTime() - start_time < 5:
            if "escape" in event.getKeys():
                core.quit()
            
            mouse_clicks = mouse.getPressed()
            
            if mouse_clicks[0]:# IF left click detected
                for i, stim in enumerate(image_stims):
                    if stim.contains(mouse):
                       selected_image = image_paths[i]
                       is_correct = (selected_image == correct_image)
                       rt = responseTimer.getTime()
                       response = selected_image
                       response_given = True
                       break
                
                if response_given:
                    break
                    
            core.wait(0.1)
            
        #7. Provide feedback
        if not response_given:
            feedback_display.setText("Too Slow")
            selected_image = None
            rt = np.nan
        else:
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
            'selected': selected_image,
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
show_message("Click the mouse to move to the next phase.")
print("Completed Recognition Training Phase.\n")
core.wait(0.1)

# Initial Presentation Block - Visual - Set 1
print("Starting Initial Presentation Phase...")
current_phase = "Initial_Presentation_2"

# Prepare text and image components
image_display = visual.ImageStim(win, image = None, size = [250,250], pos = (0,0))

# Set the number of repetitions
n = 2
mouse = event.Mouse(visible = False, win = win)

for block in range(n):

    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            break
            
        # 1. Select a random pair of an image and a name
        object_image = row['visual_s1']
        correct_name = row['auditory_s1']
        
        # 2. Display an image with the name for 2 seconds
        image_display.image = object_image
        name_audio = sound.Sound(correct_name, stopTime = 1.5)
        image_display.draw()
        win.flip()
        name_audio.play()
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
mouse = event.Mouse(visible = True, win = win)
show_message("Click the mouse to move to the next phase.")
print("Completed Initial Presentation Phase.\n")
core.wait(0.1)

event.clearEvents()

# Name learning
# Welcome message
print("Starting Name Learning Phase...")
current_phase = "Name_Learning"
show_message("Choose the correct name for the image on the screen.\n\nClick the mouse to start.")

# Define the text position
number_positions = [(-200, 200), (200, 200), (200, -200), (-200, -200)]

# Prepare text and image components
number_stims = [visual.TextStim(win, text = f"({i+1})", font ='Arial',color = "white", height = 35, pos = number_positions[i]) for i in range(4)]
image_display = visual.ImageStim(win, image = None, size = (250, 250), pos = (0, 0))
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = "white", pos = (0, 0))

# Set the number of repetitions
n3 = 2

# Experiment loop
terminate_exp = False
event.clearEvents()

# Reset mouse position to center
mouse.setPos((0, 0))

for block in range(n3):

    # Shuffle the stimuli order for n blocks 
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList=["escape"]):
            break
            
        # 1. Select a random image and its corresponding name
        object_image = row['visual_s1']
        correct_name = row['auditory_s1']
        
        # 2. Select three distractor names (excluding the correct name)
        distractor_names = random.sample([name for name in stimuli_df['auditory_s1'] if name != correct_name], 3)
        
        # 3. Form the name set (1 correct + 3 distractors) and shuffle
        name_choices = distractor_names + [correct_name]
        random.shuffle(name_choices)
        
        # Load audio files for the four choices
        audio_sounds =  [sound.Sound(name) for name in name_choices]
        
        # 4. Display an image
        image_display.image = object_image
        image_display.draw()
        win.flip()
        core.wait(2)

        # 5. Display for numbers on the screen
        for stim in number_stims:
            stim.draw()

        image_display.draw()
        win.flip()

        # 6. Listening phase - automatic playback
        responseTimer = core.Clock()
        mouse.clickReset()

        # Enable mouse-clicking during playback
        response = None
        selected_image = None
        rt = None
        is_correct = False
        rt_tracking_active = False
        response_given = False

        for i, audio in enumerate(audio_sounds):
            if "escape" in event.getKeys():
                core.quit()

            # Flash the corresponding number
            for stim in number_stims:
                stim.setColor("white")

            number_stims[i].setColor("yellow")

            # Draw updated numbers and image
            for stim in number_stims:
                stim.draw()
            image_display.draw()
            win.flip()

            # Check if this is the correct name's audio, then start the response
            if name_choices[i] == correct_name:
                responseTimer.reset()
                rt_tracking_active = True
                    
            # Play audio and check for responses simultaneously
            audio.play()
                
            # Allow mouse-click responeses while audio is playing
            audio_duration = 1.5
            start_time = core.getTime()
                
            while core.getTime() - start_time < audio_duration:
                mouse_clicks = mouse.getPressed()
                    
                if mouse_clicks[0]:
                    mouse_x, mouse_y = mouse.getPos()
                        
                    for j, stim in enumerate(number_stims):
                        stim_x, stim_y = stim.pos
                        box_width = stim.height * 3
                        box_height = stim.height
                    
                        new_width = box_width * 1.25
                        new_height = box_height * 1.25
                        
                        left_bound = stim_x - new_width /2
                        right_bound = stim_x + new_width / 2
                        top_bound = stim_y + new_height / 2
                        bottom_bound = stim_y - new_height / 2
                            
                        if left_bound <= mouse_x <= right_bound and bottom_bound <= mouse_y <= top_bound:
                            selected_name = name_choices[j]
                            is_correct = (selected_name == correct_name)
                            if rt_tracking_active:
                                rt = responseTimer.getTime()
                            response = selected_name
                            response_given = True
                        
                            # Stop audio immediately and exit the loop
                            audio.stop()
                            break
                if response:
                    break
            if response:
                break
            
        # Reset the last stimulus after all audios are played
        for stim in number_stims:
            stim.setColor("white")
            stim.draw()
        image_display.draw()
        win.flip()
                    
        # 7. Response timewindow (5s) after last audio finishes
        if response is None:
            timeout = 5
            start_time = core.getTime()
            while core.getTime() - start_time < timeout:
                buttons, times = mouse.getPressed(getTime = True)
        
                if buttons[0]:
                    for i, stim in enumerate(number_stims):
                        if stim.contains(mouse):
                            selected_name = name_choices[i]
                            is_correct = (selected_name == correct_name)
                            if rt_tracking_active:
                                rt = responseTimer.getTime()
                            response = selected_name
                            response_given = True
                            break
                if response_given:
                    break
                core.wait(0.1)
                        
        # If no response within 5 seconds, mark it as "no response"
        if response is None:
            response = "no response"
            selected_name = "no response"
            rt = 0
            is_correct = False
            response_given = False
            
        if terminate_exp:
            break
        
        win.flip()
        
        # 8. Provide feedback
        if not response_given:
            feedback_display.setText("Too Slow")
            selected_image = None
            rt = 0
        else:
            feedback_display.setText("Correct" if is_correct else "Incorrect")
                
        feedback_display.draw()
        win.flip()
        core.wait(1.5)
            
        # 9. Blank screen
        win.flip()
        core.wait(1)
            
        # Reset mouse position to the center of the image
        mouse.setPos((0, 0))
        
        # Recored the response data
        all_responses.append({
            'phase': current_phase,
            'block': block + 1,
            'trial': index + 1,
            'object_name': correct_name,
            'object_image': object_image,
            'selected': selected_name,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else 0
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
