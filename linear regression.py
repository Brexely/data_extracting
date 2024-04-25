import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from matplotlib.widgets import Slider, Button
from tkinter import filedialog
import tkinter as tk
from scipy.signal import savgol_filter

# Define constants for permeability coefficient calculation
V = 1.97E-03  # m^3, vessel volume
L = 2.50E-02  # m, sample length
A = 1.33E-04  # m^2, sample cross-sectional area

def smooth_data(data, window_length=31, polyorder=10):
    return savgol_filter(data, window_length, polyorder)

def detect_linear_region(smoothed_data, threshold=0.01, min_r_squared=0.9):
    slopes = np.gradient(smoothed_data)
    diff_slopes = np.abs(np.diff(slopes))
    linear_region_indices = np.where(diff_slopes < threshold)[0]
    
    # Iterate through linear regions and calculate R-squared
    for i in range(len(linear_region_indices) - 1):
        start_index = linear_region_indices[i]
        end_index = linear_region_indices[i + 1]
        
        # Perform linear regression on the subset of data
        subset_data = smoothed_data[start_index:end_index]
        x = np.arange(len(subset_data))
        slope, intercept, r_value, _, _ = linregress(x, subset_data)
        
        # Check if R-squared meets the threshold
        if r_value ** 2 >= min_r_squared:
            return start_index, end_index
            
    return None, None

def update_plot(val):
    x_min = slider_min.val
    x_max = slider_max.val

    ax.clear()

    # Smooth the data
    smoothed_pressure = smooth_data(extracted_data['CHANNEL1_Pa'])

    # Plot the original data
    # ax.plot(extracted_data['Time(seconds)'], extracted_data['CHANNEL1_Pa'], label='Original Data')

    # Plot the smoothed data
    ax.plot(extracted_data['Time(seconds)'], smoothed_pressure, label='Smoothed Data', color='green')

    # Perform linear regression on the original data within the specified range
    subset_original_data = extracted_data[(extracted_data['Time(seconds)'] >= x_min) & (extracted_data['Time(seconds)'] <= x_max)]
    slope, intercept, r_value, _, _ = linregress(subset_original_data['Time(seconds)'], subset_original_data['CHANNEL1_Pa'])

    # Plot the linear regression line
    ax.plot(subset_original_data['Time(seconds)'], slope * subset_original_data['Time(seconds)'] + intercept, color='red', linestyle='--', label='Linear Regression')

    # Highlight the area under the regression line
    ax.fill_between(subset_original_data['Time(seconds)'], subset_original_data['CHANNEL1_Pa'], slope * subset_original_data['Time(seconds)'] + intercept, color='lightblue')

    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Pressure (Pa)')
    ax.set_title('Original Data and Smoothed Data with Linear Regression')
    ax.legend()

    plt.draw()

    return slope, intercept, r_value, subset_original_data['CHANNEL0_Pa'].mean()

def detect_linear_region_button(event):
    global start_index, end_index
    smoothed_pressure = smooth_data(extracted_data['CHANNEL1_Pa'])
    start_index, end_index = detect_linear_region(smoothed_pressure)
    slider_min.set_val(extracted_data.iloc[start_index]['Time(seconds)'])
    slider_max.set_val(extracted_data.iloc[end_index - 1]['Time(seconds)'])
    update_plot(None)

def save_regression_data(event):
    slope, intercept, r_value, average_pressure_p0 = update_plot(None)
    
    # Check if valid data is available
    if np.isnan(slope):
        print("No valid data available.")
        return

    new_pm = (average_pressure_p0 + 100000) / 2
    permeability_coefficient = (slope / ((average_pressure_p0 + 100000) / 2)) * ((V * L) / A)
    
    # Check if R^2 is less than 0.9
    if r_value ** 2 < 0.90:
        print("R-squared too small. Regression not reliable.") 
        # Reset the sliders to their initial positions
        slider_min.reset()
        slider_max.reset()
        # Update the plot with the initial borders
        update_plot(None)
        return
    
    # Add the results to the linear_regression_results list
    linear_regression_results.append({'filename': filename, 'slope': slope, 'intercept': intercept, 'r_value': r_value, 'average_pressure_p0': average_pressure_p0, 'permeability_coefficient': permeability_coefficient, 'pm': new_pm})
    
    # Convert the list to a DataFrame
    df_results = pd.DataFrame(linear_regression_results)
    
    # Save DataFrame to CSV file
    if output_file_path:
        df_results.to_csv(output_file_path, index=False)
        print("Linear regression data saved.")
        print("Permeability coefficient saved.")
    
    # Close the plot window
    plt.close()

def select_output_file():
    global output_file_path
    output_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

linear_regression_results = []

root = tk.Tk()
root.withdraw()

# Get the folder path for the input files
folder_path = filedialog.askdirectory(title="Select folder with input files")

# Prompt the user to select the output file name
select_output_file()

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        
        channel_0_col = df.columns[0]  # Assuming the column is at index 0
        channel_1_col = df.columns[1]  # Assuming the column is at index 1
        extracted_data = df[['Time(seconds)', 'CHANNEL1_Pa', 'CHANNEL0_Pa']]

        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.4)

        # Add sliders for setting x range
        axcolor = 'lightgoldenrodyellow'
        ax_slider_min = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
        ax_slider_max = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)

        slider_min = Slider(ax_slider_min, 'X Min', 0, extracted_data['Time(seconds)'].max(), valinit=0)
        slider_max = Slider(ax_slider_max, 'X Max', 0, extracted_data['Time(seconds)'].max(), valinit=extracted_data['Time(seconds)'].max())

        slider_min.on_changed(update_plot)
        slider_max.on_changed(update_plot)

        # Add button to detect linear region
        ax_button_detect = plt.axes([0.1, 0.02, 0.2, 0.05])
        button_detect = Button(ax_button_detect, 'Detect Linear Region', color='lightgoldenrodyellow', hovercolor='0.975')
        button_detect.on_clicked(detect_linear_region_button)

        # Add button to save linear regression data
        ax_button_save = plt.axes([0.8, 0.02, 0.1, 0.05])
        button_save = Button(ax_button_save, 'Save', color='lightgoldenrodyellow', hovercolor='0.975')
        button_save.on_clicked(save_regression_data)

        plt.show()
