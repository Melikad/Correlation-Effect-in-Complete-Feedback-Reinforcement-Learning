import numpy as np
import random
from psychopy import visual, core, event
import pandas as pd
import time
from itertools import combinations
from psychopy import gui, core

# Create a dialog box
participant_info = {'Participant Number': ''}
dlg = gui.DlgFromDict(dictionary=participant_info, title="Experiment Info")

# If the participant presses cancel, quit the experiment
if dlg.OK == False:
    core.quit()

# Get the participant number
participant_number = participant_info['Participant Number']

# Initialize window
win = visual.Window(size=(800, 600), color='white', units='pix')

# Function to show instructions
def show_instructions(text):
    instruction_text = visual.TextStim(win, text=text, color='black')
    instruction_text.draw()
    win.flip()
    event.waitKeys()

# Function to show two images and get the choice
def show_choice_and_get_response(img_left, img_right):
    left_stim = visual.ImageStim(win, image=img_left, pos=(-200, 80))
    right_stim = visual.ImageStim(win, image=img_right, pos=(200, 80))
    left_stim.draw()
    right_stim.draw()
    win.flip()
    
    decision_clock = core.Clock()
    keys = event.waitKeys(keyList=['left', 'right'])
    decision_time = decision_clock.getTime()

    if 'left' in keys:
        return 'left', decision_time
    else:
        return 'right', decision_time

# Function to show inline feedback
def show_inline_feedback(img_left, img_right, value_left, value_right):
    left_stim = visual.ImageStim(win, image=img_left, pos=(-200, 80))
    right_stim = visual.ImageStim(win, image=img_right, pos=(200, 80))

    left_value_text = visual.TextStim(win, text=f"{value_left:.2f}", pos=(-200, -150), color='black')
    right_value_text = visual.TextStim(win, text=f"{value_right:.2f}", pos=(200, -150), color='black')

    left_stim.draw()
    right_stim.draw()
    left_value_text.draw()
    right_value_text.draw()
    win.flip()

    feedback_clock = core.Clock()
    event.waitKeys()
    feedback_time = feedback_clock.getTime()
    
    return feedback_time


# Generate correlated values
#def generate_correlated_values(mean_a, mean_b, var_a, var_b, p, size):
#    cov_ab = p * np.sqrt(var_a) * np.sqrt(var_b)
#    cov_matrix = [[var_a, cov_ab], [cov_ab, var_b]]
#    mean_vector = [mean_a, mean_b]
#    return np.random.multivariate_normal(mean_vector, cov_matrix, size)
def generate_correlated_values(mean1, mean2, var1, var2, correlation, size):
    cov_matrix = [[var1, correlation * np.sqrt(var1 * var2)], [correlation * np.sqrt(var1 * var2), var2]]
    values = np.random.multivariate_normal([mean1, mean2], cov_matrix, size).T
    return values[0], values[1]
    
# Define image paths for each phase and part
images_training = {
    1: 'images/a1_trial.png',
    2: 'images/a2_trial.png',
    3: 'images/b_trial.png',
    4: 'images/c_trial.png'
}

images_learning_negative = {
    1: 'images/a1_N_image.png',
    2: 'images/a2_N_image.png',
    3: 'images/b_N_image.png',
    4: 'images/c_N_image.png'
}

images_learning_zero = {
    1: 'images/a1_Z_image.png',
    2: 'images/a2_Z_image.png',
    3: 'images/b_Z_image.png',
    4: 'images/c_Z_image.png'
}

images_learning_positive = {
    1: 'images/a1_P_image.png',
    2: 'images/a2_P_image.png',
    3: 'images/b_P_image.png',
    4: 'images/c_P_image.png'
}

# Randomize the order of the three parts in phase 2
learning_phases = [
    (images_learning_negative, -0.5),
    (images_learning_zero, 0),
    (images_learning_positive, 0.5)
]
random.shuffle(learning_phases)

# Phase 1: Training
show_instructions("In this task, at each trial you will face two items, each with a value. "
                  "You will gain the value of the item you choose. You can see the values after you make your choice. you have as much as time you need to see these values. Go to the next trial by pressing any key. Try to collect the highest value. Press any key to continue.")
training_score = 0
trial_data = []

for trial in range(5):
    img_left, img_right = random.sample(list(images_training.values()), 2)
    choice, decision_time = show_choice_and_get_response(img_left, img_right)

    value_left = random.randint(1, 100)
    value_right = random.randint(1, 100)

    feedback_time = show_inline_feedback(img_left, img_right, value_left, value_right)

    gained_value = value_left if choice == 'left' else value_right
    training_score += gained_value

    trial_data.append({
        'Participant_number': participant_info['Participant Number'], 'Phase': 'Training', 'Trial': trial + 1, 'Image Left': img_left, 'Image Right': img_right,
        'Value Left': value_left, 'Value Right': value_right, 'Choice': choice,
        'Gained Value': gained_value, 'Decision Time': decision_time, 'Feedback Time': feedback_time
    })


learning_df = pd.DataFrame(trial_data)
estimation_df = pd.DataFrame()

# Phase 2: Learning (shuffled order)

def estimate(win, paired_images, estimation_df):

    # Create a line for the spectrum
    spectrum_line = visual.Line(win, start=(-250, -200), end=(250, -200), lineWidth=5, lineColor='black')

    # Create a vertical line to mark the middle point
    middle_marker = visual.Line(win, start=(0, -230), end=(0, -170), lineWidth=2, lineColor='blue')

    # Create a marker for the selected degree
    marker = visual.Circle(win, radius=10, fillColor='red', lineColor='red')

    # Create a DataFrame to store results
    df = pd.DataFrame(columns=['Image_Left', 'Image_Right', 'Selected_Degree', 'Reaction_Time'])

    # List to hold new rows
    new_rows = []

    # Iterate over the list of paired images
    for image_left_path, image_right_path in paired_images:
        # Load the images
        image_left = visual.ImageStim(win, image=image_left_path, pos=(-200, 100), size=(200, 200))
        image_right = visual.ImageStim(win, image=image_right_path, pos=(200, 100), size=(200, 200))
        
        # Draw the images and the spectrum line
        win.flip()
        image_left.draw()
        image_right.draw()
        spectrum_line.draw()
        middle_marker.draw()
        win.flip()
        
        # Wait for user to click on the spectrum to select a point
        print("Click on the spectrum to select a point.")
        mouse = event.Mouse(win=win)
        
        # Record the start time
        start_time = time.time()
        
        while not mouse.getPressed()[0]:
            x, y = mouse.getPos()
        
        # Record the end time
        end_time = time.time()
        
        # Calculate the selected degree
        selected_degree = (x + 250) / 5  # Adjust based on spectrum line length
        
        # Calculate reaction time
        reaction_time = end_time - start_time

        # Clear window, redraw the images, spectrum line, and middle marker, and draw the selected marker
        win.flip()
        image_left.draw()
        image_right.draw()
        spectrum_line.draw()
        middle_marker.draw()
        marker.pos = (x, -200)  # Adjust y position to be aligned with the spectrum
        marker.draw()

        # Update the window with the selected marker
        win.flip()

        # Print the selected degree and reaction time
        print(f"Selected degree on the spectrum: {selected_degree:.2f}")
        print(f"Reaction time: {reaction_time:.2f} seconds")

        # Add results to new_rows list
        new_rows.append({
            'Participant_number': participant_info['Participant Number'], 
            'Image_Left': image_left_path,
            'Image_Right': image_right_path,
            'Selected_Degree': selected_degree,
            'Reaction_Time': reaction_time
        })

        # Wait a few seconds before moving to the next pair
        core.wait(2)

    df_new = pd.DataFrame(new_rows)
    
    print("###############")
    print(df_new)
    
    # Concatenate the new rows with the original DataFrame
    estimation_df = pd.concat([estimation_df, df_new], ignore_index=True)
    
    return estimation_df



def learning_phase(win, it, part_images, p, learning_df, estimation_df):
    part = 1
    if p == 0:
        part = 2
    elif p == 0.5:
        part = 3
     
    print("@@@@@@@@@@ part: ", part)
        
    ins = "learning phase " + str(it)
    show_instructions(ins)
    a1_values, b_values = generate_correlated_values(64, 54, 13**2, 13**2, p, 100)
    a2_values, c_values = generate_correlated_values(64, 44, 13**2, 13**2, p, 100)

    trial_order = [("a1", "b")] * 35 + [("a2", "c")] * 35
    random.shuffle(trial_order)  # Randomize order for the first 70 trials

    trial = 0
    mean_a1 = 0
    mean_a2 = 0
    
    new_rows = []

    while trial < 70 or (abs(mean_a1 - mean_a2) > 5 and trial < 100):
        print("trial:", trial)
        if trial < 70:
            item, pair = trial_order[trial]  # Random trials in the first 70
        else:
            # Alternating between (a1, b) and (a2, c) for trials beyond 70
            if trial % 2 == 0:
                item, pair = "a1", "b"
            else:
                item, pair = "a2", "c"

        if item == "a1":
            a_value = a1_values[trial]
            b_value = b_values[trial]
            pair_images = (part_images["a1"], part_images["b"])
            value_right = b_value
        else:
            a_value = a2_values[trial]
            c_value = c_values[trial]
            pair_images = (part_images["a2"], part_images["c"])
            value_right = c_value

        value_left = a_value
        
        choice, decision_time = show_choice_and_get_response(pair_images[0], pair_images[1])
        feedback_time = show_inline_feedback(pair_images[0], pair_images[1], value_left, value_right)

        gained_value = value_left if choice == 'left' else value_right

        new_rows.append({
            'Participant_number': participant_info['Participant Number'], 'Phase': f'Learning Part {part}', 'Trial': trial + 1, 'Image Left': pair_images[0], 'Image Right': pair_images[1],
            'Value Left': value_left, 'Value Right': value_right, 'Choice': choice,
            'Gained Value': gained_value, 'Decision Time': decision_time, 'Feedback Time': feedback_time
        })
        
        trial += 1
        mean_a1 = np.mean(a1_values[:trial])
        mean_a2 = np.mean(a2_values[:trial])

        print("Trial {trial}: mean_a1={mean_a1}, mean_a2={mean_a2}")

    print(f"Finished learning phase part with p = {p}. Mean a1: {mean_a1}, Mean a2: {mean_a2}, Trials: {trial}")
    
    df_new = pd.DataFrame(new_rows)
    learning_df = pd.concat([learning_df, df_new], ignore_index=True)
    #learning_df = learning_df.append(df_new, ignore_index=True)
    #learning_df.loc[len(learning_df):] = df_new.values
    
    print(df_new)
    print(new_rows)
    
    image_addresses = list(part_images.values())
    print("addresses created")
    # Generate all possible pairs of image addresses
    paired_images = list(combinations(image_addresses, 2))
    estimation_df = estimate(win, paired_images, estimation_df)
    
    return learning_df, estimation_df

part_images_N = {"a1": "images/tibetian/a1_N.png", 
"a2": "images/tibetian/a2_N.png", 
"b": "images/tibetian/b_N.png", 
"c": "images/tibetian/c_N.png"}

part_images_Z = {"a1": "images/tibetian/a1_Z.png", 
"a2": "images/tibetian/a2_Z.png", 
"b": "images/tibetian/b_Z.png", 
"c": "images/tibetian/c_Z.png"}

part_images_P = {"a1": "images/tibetian/a1_P.png", 
"a2": "images/tibetian/a2_P.png", 
"b": "images/tibetian/b_P.png", 
"c": "images/tibetian/c_P.png"}

print(f"Learning phase")
it = 1
for part_images, correlation in zip([part_images_N, part_images_Z, part_images_P], [-0.5, 0, 0.5]):
    learning_df, estimation_df = learning_phase(win, it, part_images, correlation, learning_df, estimation_df)
    it += 1

# Phase 3: Estimation
show_instructions("Now, please rate your confidence in guessing the value of each item. Press any key to continue.")

a1a2 = [
("images/tibetian/a1_N.png", "images/tibetian/a2_Z.png"),
("images/tibetian/a1_N.png", "images/tibetian/a2_P.png"),
("images/tibetian/a1_Z.png", "images/tibetian/a2_N.png"),
("images/tibetian/a1_Z.png", "images/tibetian/a2_P.png"),
("images/tibetian/a1_P.png", "images/tibetian/a2_N.png"),
("images/tibetian/a1_P.png", "images/tibetian/a2_Z.png")
]

bc = [
("images/tibetian/b_N.png", "images/tibetian/c_Z.png"),
("images/tibetian/b_N.png", "images/tibetian/c_P.png"),
("images/tibetian/b_Z.png", "images/tibetian/c_N.png"),
("images/tibetian/b_Z.png", "images/tibetian/c_P.png"),
("images/tibetian/b_P.png", "images/tibetian/c_N.png"),
("images/tibetian/b_P.png", "images/tibetian/c_Z.png")
]

estimation_df = estimate(win, a1a2, estimation_df)
estimation_df = estimate(win, bc, estimation_df)
    

# Store the data (save to CSV or print)
learning_csv_path = 'learning_data_' + str(participant_info['Participant Number']) + '.csv'
learning_df.to_csv(learning_csv_path, index=False)

estimation_csv_path = 'estimation_data_' + str(participant_info['Participant Number']) + '.csv'
estimation_df.to_csv(estimation_csv_path, index=False)

# Close the window
win.close()
core.quit()
