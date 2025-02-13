# Learning phase
# Recognition Training - Visual - Set 1

from psychopy import visual, event, core, data, logging, gui
import datetime
import pandas as pd
import random
import os

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Set the number of repetitions
n = 4

# Set up the window
win = visual.Window([800,800], color = "black", units = 'pix', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Generate timestamped filename for saving data 
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_dir = "/Users/lumikang/Documents/UCSD/25/Evo_Mod"
os.makedirs(save_dir, exist_ok = True)
file_name = os.path.join(save_dir, f"recog_v_s1_{timestamp}.csv")

# Welcome message
welcome_text = visual.TextStim(win, text = "Click the mouse to start.", font = 'Arial', height = 35, color = 'white', pos = (0,0))
welcome_text.draw()
win.flip()

# Wait for mouse click with a timeout (10 seconds)
start_time = core.getTime()
while not any(mouse.getPressed()):
    core.wait(0.1) # Small delay to prevent oversue of CPU
    if core.getTime() - start_time > 10:
        print("No response within 10 seconds. Exiting.")
        win.close()
        core.quit()
        
# Define the image and text positions
image_positions = [(-200, 200), (200, 200), (-200, -200), (200, -200)]
number_positions = [(-200, 300), (200, 300), (-200, -100), (200, -100)]

# Prepare text and image component
name_display = visual.TextStim(win, text ="", font ='Arial', height = 35, color = 'white', pos =(0, 0))
image_stims = [visual.ImageStim(win, pos = pos, size = (250, 250)) for pos in image_positions]
number_stims = [visual.TextStim(win, text = str(i+1), font ='Arial',color = 'white', height = 25, pos = number_positions[i]) for i in range(4)]
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = 'white', pos = (0, 0))
break_display = visual.TextStim(win, text = "Take a short break.\nClick the mouse to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))


# Load all image paths from the column into a list
all_images = list(stimuli_df['visual_s1'])

# Initialize a list to store trial data
response_data = []

# Experiment loop
terminate_exp = False
event.clearEvents()

# Reset mouse position to center
mouse.setPos((0,0))

for block in range(n):
    
    # Shuffle the stimuli order for n blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        
        # Check for an exit key
        if "escape" in event.getKeys(keyList=["escape"]):
            terminate_exp = True
            break
        
        #1. Select a random name and its corresponding image
        selected_row = stimuli_df.sample(1).iloc[0]
        object_name = selected_row['name_s1']
        correct_image = selected_row['visual_s1']
        
        #2. Select three distractor images (excluding the correct image)
        distractor_images = random.sample([img for img in all_images if img != correct_image], 3)
        
        #3. Form the image set (1 correct + 3 distractors) and shuffle
        image_paths = distractor_images + [correct_image]
        random.shuffle(image_paths)
        
        #4. Display images with numbers
        for stim, num_text, img_path in zip(image_stims, number_stims, image_paths):
            stim.setImage(img_path)
            stim.draw()
            num_text.draw()
        
        win.flip()
        core.wait(1)
        
        #5. Display an object name with four images
        name_display.setText(object_name)
        name_display.draw()
        for stim, num_text in zip(image_stims, number_stims):
            stim.draw()
            num_text.draw()
        
        win.flip()

        #6. Wait for participants to respond by clicking
        responseTimer = core.Clock()
        responseTimer.reset()

        response = None
        selected_image = None
        rt = None
        is_correct = False
        
        while response is None:
            mouse.clickReset()
            buttons, times = mouse.getPressed(getTime = True)
            
            if "escape" in event.getKeys(keyList = ["escape"]):
                terminate_exp = True
                break
            
            if buttons[0]: # IF left click detected
                for i, stim in enumerate(image_stims):
                    if stim.contains(mouse):
                       selected_image = image_paths[i]
                       is_correct = (selected_image == correct_image)
                       rt = responseTimer.getTime()
                       response = selected_image
                       break

            # If no response within 3 seconds, mark it as "no response"
            if responseTimer.getTime() > 3:
                response = "no response"
                selected_image = "no response"
                rt = 0
                is_correct = False
                break

        if terminate_exp:
            break
        
        win.flip()
            
        #7. Provide feedback
        feedback_display.setText("Correct" if is_correct else "Incorrect")
        feedback_display.draw()
        win.flip()
        core.wait(1.5)
       
        # Blalnk screen
        win.flip()
        core.wait(1.5)
        
        # Reset mouse position to center
        mouse.setPos((0,0))
        
        # Record the response data
        response_data.append({
            'block': block + 1,
            'trial': index + 1,
            'object_name': object_name,
            'selected_image': selected_image,
            'correct_image': correct_image,
            'correct': is_correct,
            'response_time': rt * 1000 if rt else 0
        })
        
        # Save progress after every trial
        response_df = pd.DataFrame(response_data)
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
            core.wait(0.1)
        
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
