import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog
import os

# Define constants
V = 1.97E-03  # m^3, vessel volume
L = 2.50E-02  # m, sample length
A = 1.33E-04  # m^2, sample cross-sectional area
M = 2.80E-02  # kg*mol^-1, Molekulargewicht N2
T = 298  # Temperature in Kelvin
R = 8.3145  # Ideal gas constant
pi = np.pi
mu = 1.76E-05  # Pa*s, fluid (nitrogen) viscosity (20°C)

# Define the function to calculate the permeability coefficient K
def calculate_K(slope, pm):
    return (slope / ((((pm)*2))) * ((V * L) / A))

# Function to process a single CSV file
def process_csv(file_path):
    # Load the data
    data = pd.read_csv(file_path)
    
    # Calculate K for each data point
    data['K'] = calculate_K(data['slope'], data['pm'])

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress((data['pm'] ), data['K'])

    # Calculate the slip coefficient
    slip_coefficient = (0.75 * intercept) / np.sqrt(8 * T * R / (pi * M))

    # Calculate the viscous permeability coefficient
    viscous_permeability_coefficient = slope * mu

    # Calculate the Knudsen Number
    knudsen_number = viscous_permeability_coefficient * 1013249966000  # Pa*m^2 to mm^2

    # Append the output data to the list
    output_data.append({
        'Filename': os.path.splitext(os.path.basename(file_path))[0],
        'Slip Coefficient': slip_coefficient,
        'Slope of the regression line': slope,
        'Intercept of the regression line': intercept,
        'Viscous Permeability Coefficient': viscous_permeability_coefficient,
        'Knudsen Number': knudsen_number
    })

    # Plot K against (pm)
    plt.plot(data['pm'], data['K'], marker='o', linestyle=' ')
    plt.xlabel('Average Pressure (pm)')
    plt.ylabel('Permeability Coefficient (K)')
    
    # Add the regression line to the plot
    plt.plot((data['pm']), slope * ((data['pm'] ) ) + intercept, color='red', linestyle='--', label='Linear Regression')

    # Add the equation of the regression line to the plot
    equation = f'y = {slope:.2f}x + {intercept:.2f}\nR-squared = {r_value**2:.2f}'
    plt.text(0.1, 0.9, equation, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

    plt.legend()

    # Save plot with the given name
    plot_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}_plot.png")
    plt.savefig(plot_file_path)

    plt.close()

# Create Tkinter window to select the folder
root = tk.Tk()
root.withdraw()  # Hide the main window

# Prompt the user to select the folder containing CSV files
folder_path = filedialog.askdirectory(title="Select folder containing CSV files")

# Create a list to hold all the output data
output_data = []

# Create output folder
output_folder = os.path.join(folder_path, "output_data")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate over each CSV file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        process_csv(file_path)

# Save the data to a CSV file
output_file_path = os.path.join(output_folder, "combined_output_data.csv")
pd.DataFrame(output_data).to_csv(output_file_path, index=False)

print("All data processed and saved.")
plt.show()
