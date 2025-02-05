# Learning phase
# Recognition Training - Visual - Set 1

from psychopy import visual, event, core, data, logging, gui, sound
from datetime import datetime
import pandas as pd
import random
import os

# Load the stimuli CSV file into a dataframe
csv_file = "/Users/lumikang/Documents/UCSD/25/Evo_Mod/evo_data.csv"
stimuli_df = pd.read_csv(csv_file)

# Set up the window
win = visual.Window([800,800], color = "black", units = 'norm', checkTiming = False)

# Create a mouse
mouse = event.Mouse(visible = True, win = win)

# Welcome message
welcome_text = visual.TextStim(win, text = "Click the mouse to start.", font = 'Arial', color = 'white', pos = (0,0))
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
image_positions = [(-0.5, 0.5), (0.5, 0.5), (-0.5, -0.5), (0.5, -0.5)]
number_positions = [(-0.5, 0.8), (0.5, 0.8), (-0.5, -0.2), (0.5, -0.2)]

# Prepare text and image component
name_display = visual.TextStim(win, text ="", font ='Arial', color = 'white', pos =(0,0))
image_stims = [visual.ImageStim(win, pos = pos, size = (0.4, 0.4)) for pos in image_positions]
number_stims = [visual.TextStim(win, text = str(i+1), font ='Arial',color = 'white', pos = number_positions[i]) for i in range(4)]

# Load soound files
correct_sound = sound.Sound("/Users/lumikang/Documents/UCSD/25/Evo_Mod/soundeffect/correct_sound.wav")
incorrect_sound = sound.Sound("/Users/lumikang/Documents/UCSD/25/Evo_Mod/soundeffect/incorrect_sound.wav")

# Load all image paths from the column into a list
all_images = list(stimuli_df['visual_s1'])
random.shuffle(all_images)

# Initialize a list to store trial data
response_data = []

# Experiment loop
for index, row in stimuli_df.iterrows():
    correct_image = row['visual_s1']
    object_name = row['name_s1']
    
    # Ensure the correct image is included in the set of four
    image_paths = random.sample(all_images, 3)
    if correct_image not in image_paths:
        image_paths.append(correct_image)
    
    # Double-check that 'image_paths' always has exactly 4 images
    if len(image_paths) != 4:
        print(f"Error: Image path list length is {len(image_paths)} instead of 4.")
        image_paths = list(set(image_paths))
        while len(image_paths) < 4:
            random_image = random.choice(all_images)
            if random_image not in image_paths:
                image_paths.append(random_image)
    
    # Shuffle to randomize positions
    random.shuffle(image_paths)
    
    # 1 Select 4 distinct images
    for stim, num_text, img_path in zip(image_stims, number_stims, image_paths):
        stim.setImage(img_path)
        stim.draw()
        num_text.draw()
        
    win.flip()
    core.wait(1)
    
    # 2 Display an object name with four images
    name_display.setText(object_name)
    name_display.draw()
    for stim, num_text in zip(image_stims, number_stims):
        stim.draw()
        num_text.draw()
    
    win.flip()

    # 3 Wait for participants to click an image
    response = None
    selected_image = None
    rt = None
    is_correct = False
    
    start_time = core.getTime()
    
    while response is None:
        mouse.clickReset()
        buttons, times = mouse.getPressed(getTime = True)
        
        if buttons[0]: # IF left click detected
            mouse_pos = mouse.getPos()
            for i in range(len(image_stims)):
                if image_stims[i].contains(mouse):
                    if i < len(image_paths):
                        response = image_paths[i]
                        selected_image = response
                        is_correct = (selected_image == correct_image)
                        rt = core.getTime() - start_time
                        break
                else:
                    print(f"Warning: Index {i} is out of range for image_paths!")
                    
        # If no response within 3 seconds, makr it as "no response"
        if core.getTime() - start_time > 3:
            response = "no response"
            rt = None
            is_correct = False
            break
        
        # Debugging print
        print(f"Response: {response}, Response Time: {rt:.3f} sec" if rt is not None else "No response")

    
    win.flip()
    
    # Update path
    correct_audio = sound.Sound(correct_sound, stopTime = 2)
    incorrect_audio = sound.Sound(incorrect_sound, stopTime = 2)
    
    # 4 Provide feedback after a mouse clicking
    if is_correct:
        correct_audio.play()
    else:
        incorrect_audio.play()
    
    
    # Blalnk screen
    win.flip()
    core.wait(1.5)
    
    # Record the response data
    response_data.append({
        'object_name': object_name,
        'selected_image': selected_image,
        'correct_image': correct_image,
        'correct': is_correct,
        'response_time': rt
    })

# Generate a timestamp for a unique file name
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
file_name = f'/Users/lumikang/Documents/UCSD/25/Evo_Mod/recognition/response/sv1_recognition_{timestamp}.csv'

# Save the response to a CSV file
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