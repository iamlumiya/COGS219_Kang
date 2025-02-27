# Learning phase
# Name learning - Auditory - Set 1

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
file_name = os.path.join(excel_file_path, f"name_aud__set1_{timestamp}.csv")

# Load the stimuli CSV file into a dataframe
stimuli_df = pd.read_csv(csv_file)

# Function to save response data to CSV
all_responses = []

# Set the number of repetitions
n = 2

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Welcome message
welcome_text = visual.TextStim(win, text = "Choose the correct name that corresponds to the image.\n Press a number key (1, 2, 3, or 4) to listen to the names and click a number to finalize your answer. \n\n Click the mouse to start.", font = 'Arial', color = 'white', height = 35, pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for mouse click with a timeout (15 seconds)
start_time = core.getTime()
while not any(mouse.getPressed()):
    if core.getTime() - start_time > 15:
        print("No response within 15 seconds. Exiting.")
        win.close()
        core.quit()
        
# Define the text position
number_positions = [(0, -50), (0, -100), (0, -150), (0, -200)]  

# Prepare text and image components
number_stims = [visual.TextStim(win, text = f"({i+1})", font ='Arial',color = "white", height = 35, pos = number_positions[i]) for i in range(4)]
image_display = visual.ImageStim(win, image = None, size = (250, 250), pos = (0, 100))
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = "white", pos = (0, 0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))

# Load all image pahts from the column into a list
all_images = list(stimuli_df['visual_s1'])

# Experiment loop
terminate_exp = False
event.clearEvents()

# Reset mouse position to center of the image
mouse.setPos((0, 100))

for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for indext, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList = ["escape"]):
            terminate_exp = True
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
        audio_sounds = [sound.Sound(name) for name in name_choices]
                
        # 4. Display an image
        image_display.image = object_image
        image_display.draw()
        win.flip()
        core.wait(2)
        
        # 5. Display four numbers on the screen
        for stim in number_stims:
            stim.draw()
        
        image_display.draw()
        win.flip()
        
        # Initialize response variables
        responseTimer = core.Clock()
        responseTimer.reset()
        
        response = None
        selected_name = None
        rt = None
        is_correct = None
        
        # 6. Listening phase
        while response is None:
            keys = event.getKeys(keyList = ["1", "2", "3", "4", "escape"])
            
            if "escape" in keys:
                terminate_exp = True
                break
                
            for key in keys:
                if key in ["1", "2", "3", "4"]:
                    index = int(key) - 1
                    audio_sounds[index].play()
                    core.wait(1.5)
                    
        # 7. Wait for mouse click to finalize response
            mouse.clickReset()
            buttons, times = mouse.getPressed(getTime = True)
            
            if buttons[0]:
                for i, stim in enumerate(number_stims):
                    if stim.contains(mouse):
                        selected_name = name_choices[i]
                        is_correct = (selected_name == correct_name)
                        rt = responseTimer.getTime()
                        response = selected_name
                        break
                        
            # If no response within 10 seconds, mark it as "no response"
            if responseTimer.getTime() > 10:
                response = "no response"
                selected_name = "no response"
                rt = 0
                is_correct = False
                break
                
        if terminate_exp:
            break
            
        win.flip()
        
        # 7. Provide feedback
        feedback_display.setText("Correct" if is_correct else "Incorrect")
        feedback_display.draw()
        win.flip()
        core.wait(1.5)
        
        # Blank screen
        win.flip()
        core.wait(1)
        
        # Reset mouse position to the center of the image
        mouse.setPos((0, 100))
        
        # Record the response data
        all_responses.append({
            'block': block + 1,
            'trial': index + 1,
            'object': object_image,
            'selected_name': selected_name,
            'correct_name': correct_name,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else 0
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(all_responses)
        response_df.to_csv(file_name, index = False)
        
        event.clearEvents()
        
    if terminate_exp:
        break
        
        # Break after every two blocks, except the last one
        if (block+1) % 2 == 0 and block + 1 < n:
            break_display.draw()
            win.flip()
        
        # Wait for a response
        while not any(mouse.getPressed()):
            core.wait(0.5)
        
    core.wait(0.1)
    event.clearEvents()


# Final save before exit
response_df.to_csv(file_name, index = False)
print(f"Response data saved to {file_name}")
 
# Close the window after the experiment
# End message
end_text = visual.TextStim(win, text = "Click the mouse to exit.", font = 'Arial', color = 'white', pos = (0,0))
end_text.draw()
win.flip()

# Wait for mouse click
while not any(mouse.getPressed()):
    core.wait(0.1)
    
win.close()
core.quit()
        
