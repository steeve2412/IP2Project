from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import json

app = Flask(__name__)

data = []  # List to store collected keystroke data
id_counter = 1  # Counter to assign unique IDs

# Load the existing data from the Excel file, if it exists
try:
    df = pd.read_excel('keystrokes.xlsx')
    data = df.to_dict('records')
    id_counter = df['ID'].max() + 1
    email_ids = {email: entry_id for email, entry_id in zip(df['Email'], df['ID'])}
except FileNotFoundError:
    data = []
    id_counter = 1
    email_ids = {}

@app.route('/', methods=['GET'])
def index():
    success_message = request.args.get('success_message')
    return render_template('index.html', success_message=success_message)

@app.route('/submit', methods=['POST'])
def submit():
    # Get the parameters from the form
    username = request.form.get('username')
    email = request.form.get('email')
    keystrokes_json = request.form.get('keystrokes')

    # Convert the JSON string to a list of keystrokes
    keystrokes = json.loads(keystrokes_json)

    # Calculate key hold time, key flight time, key press/release timings, and key combinations
    hold_times = []
    flight_times = []
    press_release_timings = []
    combinations = []
    for i in range(len(keystrokes)-1):
        hold_time = keystrokes[i+1]['time'] - keystrokes[i]['time']
        hold_times.append(hold_time)

        if keystrokes[i]['action'] == 'press' and keystrokes[i+1]['action'] == 'release':
            flight_time = keystrokes[i+1]['time'] - keystrokes[i]['time']
            flight_times.append(flight_time)
            press_release_timings.append((keystrokes[i]['time'], keystrokes[i+1]['time']))
            combinations.append((keystrokes[i]['key'], keystrokes[i+1]['key']))

    # Check if the email ID already has an assigned ID
    if email in email_ids:
        entry_id = email_ids[email]
    else:
        # Assign a new ID for the email ID
        global id_counter
        entry_id = id_counter
        id_counter += 1
        email_ids[email] = entry_id

    # Create a dictionary with the collected data
    entry_data = {
        'ID': entry_id,
        'Username': username,
        'Email': email,
        'Hold Times': hold_times,
        'Flight Times': flight_times,
        'Press/Release Timings': press_release_timings,
        'Key Combinations': combinations
    }

    # Calculate Total Hold Time
    total_hold_time = sum(hold_times)

    # Calculate Total Flight Time
    total_flight_time = sum(flight_times)

    # Calculate Total Press/Release Timings
    total_press_release_timings = len(press_release_timings)

    # Calculate Total Key Combinations
    total_key_combinations = len(combinations)

    # Append the data to the list
    data.append(entry_data)

    # Update the entry_data dictionary with the totals
    entry_data['Total Hold Time'] = total_hold_time
    entry_data['Total Flight Time'] = total_flight_time
    entry_data['Total Press/Release Timings'] = total_press_release_timings
    entry_data['Total Key Combinations'] = total_key_combinations

    # Create a DataFrame with the collected data
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    df.to_excel('keystrokes.xlsx', index=False)

    # Display a success message
    success_message = "Form submitted successfully!"

    # Redirect back to the index page with the success message
    return redirect(url_for('index', success_message=success_message))

if __name__ == '__main__':
    app.run(debug=True)
