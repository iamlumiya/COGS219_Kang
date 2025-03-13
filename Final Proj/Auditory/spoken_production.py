# Spoken production

from psychopy import visual, event, core, data, sound
import datetime
import pandas as pd
import random
import os
import csv
from sys import platform
import sounddevice as sd
import soundfile as sf
import numpy as np

# Get the current working directory
current_dir = os.getcwd()

# Define the CSV file path
csv_file = os.path.join(current_dir, "stimuli.csv")

# Define directions to search for image and audio files
image_dir = os.path.join(current_dir, "image")
audio_dir = os.path.join(current_dir, "speech")

# Function to find a file in a given directory
def find_file(directory, filename):
    for root, _, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

# Initialize an empty dictionary
data_dict = {}

# Read the CSV file
with open (csv_file, mode = 'r', encoding = 'utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        stimuli = row["name_s1"]
        
        # Extract just the file name 
        visual_filename = os.path.basename(row["visual_s1"])
        audio_filename = os.path.basename(row["auditory_s1"])
        
        # Find the actual file paths in the specified directory
        visual_path = find_file(image_dir, visual_filename)
        audio_path = find_file(audio_dir, audio_filename)
        
        # Store in dictionary
        data_dict[stimuli] = {
            "name": row["name_s1"],
            "object": row["item_s1"],
            "visual": visual_path if visual_path else "Not found",
            "audio": audio_path if audio_path else "Not found",
            }

# Convert the dictionary into a DataFrame
stimuli_df = pd.DataFrame.from_dict(data_dict, orient = 'index')

# Function to save response data to CSV
all_responses = []
current_phase = None

def save_to_csv():
    if not all_responses:
        return
        
    df = pd.DataFrame(all_responses)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file_path = os.path.join(current_dir, "response")
    response_file = os.path.join(output_file_path, f"testing_A_s1_{timestamp}.csv")
    
    # Save to CSV
    if platform == "darwin":
        df.to_csv(response_file, index = False, lineterminator = "\n")
    else:
        df.to_csv(response_file, index = False, line_terminator = "\n")
    print(f"Saved all responses to {response_file})")
    

# Function to map selected responses correctly
def map_selected(selected):
    if pd.isna(selected) or not isinstance(selected, str):
        return selected
    
    selected_basename = os.path.basename(selected)
    
    # Check if selected is an audio file -> map to "name"
    for entry in data_dict.values():
        if entry["audio"] and os.path.basename(entry["audio"]) == selected_basename:
            return entry["name"]
            
    # Check if selected is an image file -> map to "object"
    for entry in data_dict.values():
        if entry["visual"] and os.path.basename(entry["visual"]) == selected_basename:
            return entry["object"]
            
    # If no match found, return as is
    return selected

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for the space bar pressed
def show_message(text):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = 'white', height = 35, pos = (0, 0))
    msg.draw()
    win.flip()

    while True:
        keys = event.getKeys()
        if "space" in keys:
            break
        core.wait(0.1)

# Welcome message
show_message("Speak the correct name alound.\n\n Press the space bar to start.")

# Prepare text and image component
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Extract the filename without the extension to create a subfolder
csv_filename = os.path.splitext(os.path.basename(csv_file))[0]

# Define the folder path inside "respose"
output_folder_path = os.path.join(current_dir, "response")
folder_path = os.path.join(output_folder_path, csv_filename)


# Record settings
fs = 44100
duration = 3

# Set the number of repetitions
n2 = 4

# Experiment loop
terminate_exp = False
event.clearEvents()

for block in range(n2):
    # Shuffle the stimuli order for n2 blocks
    block_stimuli = stimuli_df.sample(frac = 1).reset_index(drop = True)
    
    for index, row in block_stimuli.iterrows():
        # Check for an exit key
        if "escape" in event.getKeys():
            terminate_exp = True
            core.quit()
            
        # 1. Select a random image and its corresponding name
        object_name = row['audio']
        correct_image = row['visual']
        
        random.shuffle([correct_image])
        
        # 2. Display fixation cross
        fixation_display.draw()
        win.flip()
        core.wait(0.5)
        
        # 3. Display the image (2000ms)
        image_display.image = correct_image
        image_display.draw()
        win.flip()
        core.wait(2)
        
        # Setting the recording filename
        audio_filename = os.path.join(folder_path, f"response_sp_{block+1}_{index+1}.wav")
        
        # 4. Wait for the response (3000ms) + record the voice
        # Set default color to white
        response_wait.color = 'white'
        response_wait.draw()
        win.flip()
        
        # Change color to green when recording starts
        response_wait.color = [-0.61, 0.61, -0.61]
        response_wait.draw()
        win.flip()
        
        # Start recording
        response_start = core.getTime()
        recording = sd.rec(int(duration* fs), samplerate = fs, channels = 1, dtype = "int16")
        sd.wait()
        response_end = core.getTime()
        
        sf.write(audio_filename, recording, fs)
        
        # Compute response time
        rt = response_end - response_start
        
        # Change color to red for 0.2 seconds after recording finishes
        response_wait.color = 'red'
        response_wait.draw()
        win.flip()
        core.wait(0.2)
        
        # Stop recording
        core.wait(3)
        
        # 5. Blank space (1000ms)
        fixation_display.draw()
        win.flip()
        core.wait(1)
        
        # Record the response data 
        all_responses.append({
            'block': block + 1,
            'trial': index + 1,
            'object_name': correct_name,
            'selected_image': selected_image,
            'response': audio_filename,
            'response_time': rt * 1000 if rt else 0
        })
        
        event.clearEvents()
        
    if terminate_exp:
        core.quit()
        
    # Break after every 12 trials, except after the last trial
    if (block + 1) % 2 == 0 and block + 1 <n2:
        break_display = visual.TextStim(win, text = "Take a short break.\n\n Press the space bar to continue.", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
        break_display.draw()
        win.flip()
        
        core.wait(0.1)
        
        # Wait for a keypress to continue
        while True:
            keys = event.getKeys(keyList = ["space", "escape"])
            if "escape" in keys:
                terminate_exp = True
                break
            elif "space" in keys:
                break
        event.clearEvents()

# Final save before exit
print("Completed Spoken Production Phase.")
save_to_csv()

# Close the window after the experiment
# End message
show_message("You've completed all the testing phases.\n\n Press the space bar to exit.")

win.close()
core.quit()