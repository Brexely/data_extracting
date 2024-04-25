import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def convert_to_pascal(value):
    return (value - 1) * 4 * 100000  # Conversion formula from bar to Pascal

def process_folder(folder_path):
    # Iterate over each subfolder in the main folder
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            
            # Output folder to save the extracted CSV files for this subfolder
            output_folder = os.path.join(folder_path, "extracted_data")
            
            # Create the output folder if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Iterate over each file in the subfolder
            for filename in os.listdir(folder_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(folder_path, filename)
                    
                    try:
                        # Read the CSV file, skipping the first 7 rows
                        df = pd.read_csv(file_path, skiprows=7)
                        
                        # Convert 'Date/Time' column to datetime objects
                        df['Date/Time'] = pd.to_datetime(df['Date/Time'])
                        
                        # Calculate time difference in seconds from the first timestamp
                        first_timestamp = df['Date/Time'].iloc[0]
                        df['Time(seconds)'] = (df['Date/Time'] - first_timestamp).dt.total_seconds()
                        
                        # Update column names according to the actual names in the DataFrame
                        channel_0_col = df.columns[2]  # Assuming the column is at index 2
                        channel_1_col = df.columns[3]  # Assuming the column is at index 3
                        
                        # Extract columns and convert to Pascal
                        extracted_data = df[[channel_0_col, channel_1_col, 'Time(seconds)']]
                        extracted_data['CHANNEL0_Pa'] = convert_to_pascal(extracted_data[channel_0_col])
                        extracted_data['CHANNEL1_Pa'] = convert_to_pascal(extracted_data[channel_1_col])
                        
                        # Save the extracted data to a new CSV file in the output folder
                        extracted_file_path = os.path.join(output_folder, f'extracted_data_{filename}')
                        extracted_data.to_csv(extracted_file_path, index=False)
                        print(f"Processed: {filename}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_folder(folder_path)

# Create a Tkinter window
root = tk.Tk()
root.title("Select Folder")

# Button to select folder
button = tk.Button(root, text="Select Folder", command=select_folder)
button.pack()

root.mainloop()
