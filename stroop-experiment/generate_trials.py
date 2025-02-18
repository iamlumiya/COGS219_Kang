# generate_trials.py

import os
import random

# Make color incongruent
def make_incongruent(color, stimuli):
    incongruent_colors = [stimulus for stimulus in stimuli if stimulus != color]
    random_incongruent_colors = random.choice(incongruent_colors)
    return random_incongruent_colors

# Create a generate trials file
def generate_trials(subj_code, seed, num_repetitions = 25):
    
    # Define key parameters
    colors = ['red', 'orange', 'yellow', 'green', 'blue']
    trial_types = ["congruent", "incongruent"]
    orientations = ["upright", "upside_down"]
    num_repetitions = int(num_repetitions)
    
    # Random seed
    random.seed(int(seed))
    
    # Ensure 'trials' directory exists
    os.makedirs('trials', exist_ok = True)
    
    # Open a trial file
    trial_file = open(os.path.join(os.getcwd(), 'trials', f"{subj_code}_trials.csv"), 'w')
    separator = ","
    header = separator.join(["subj_code", "seed", "word", "color", "trial_type", "orientation"])
    trial_file.write(header+'\n')
    
    # Write code to loop through creating trials here
    trial_data = []
    for i in range(num_repetitions):
        cur_trial_type = random.choice(trial_types)
        cur_orientation = random.choice(orientations)
        cur_word = random.choice(colors)
        
        if cur_trial_type == "incongruent":
            cur_color = make_incongruent(cur_word, colors)
        else:
            cur_color = cur_word
        
        trial_data.append([subj_code, seed, cur_word, cur_color, cur_trial_type, cur_orientation])
    
    # Shuffle the list
    random.shuffle(trial_data)
    
    # Write the tirals to the trials file
    for cur_trial in trial_data:
        trial_file.write(separator.join(map(str, cur_trial)) + '\n')
        
    # Close the file
    trial_file.close()
