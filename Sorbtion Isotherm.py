import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import PillowWriter

class PulsePlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated Pulse Chart Plotter")
        self.root.geometry("900x700")

        # Button to open file
        self.btn_open = tk.Button(root, text="Open CSV File", command=self.load_file)
        self.btn_open.pack(pady=10)

        # Settings Frame
        self.settings_frame = tk.Frame(root)
        self.settings_frame.pack(pady=10)

        # Dropdown for framerate
        tk.Label(self.settings_frame, text="Frame Rate (ms):").grid(row=0, column=0)
        self.framerate_var = tk.StringVar(value="500")
        self.framerate_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.framerate_var, values=["100", "250", "500", "1000"])
        self.framerate_dropdown.grid(row=0, column=1)

        # Dropdown for line style
        tk.Label(self.settings_frame, text="Line Style:").grid(row=1, column=0)
        self.line_style_var = tk.StringVar(value="-")
        self.line_style_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.line_style_var, values=["-", "--", "-.", ":"])
        self.line_style_dropdown.grid(row=1, column=1)

        # Dropdown for marker style
        tk.Label(self.settings_frame, text="Marker Style:").grid(row=2, column=0)
        self.marker_var = tk.StringVar(value="o")
        self.marker_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.marker_var, values=["o", "s", "d", "^", "x", ""])
        self.marker_dropdown.grid(row=2, column=1)

        # Dropdown for color
        tk.Label(self.settings_frame, text="Line Color:").grid(row=3, column=0)
        self.color_var = tk.StringVar(value="blue")
        self.color_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.color_var, values=["blue", "red", "green", "black", "orange", "purple"])
        self.color_dropdown.grid(row=3, column=1)

        # Entry for title
        tk.Label(self.settings_frame, text="Graph Title:").grid(row=4, column=0)
        self.title_entry = tk.Entry(self.settings_frame)
        self.title_entry.grid(row=4, column=1)
        self.title_entry.insert(0, "Pulse Chart (Animated)")

        # Button to save animation
        self.btn_save = tk.Button(root, text="Save as GIF", command=self.save_animation, state=tk.DISABLED)
        self.btn_save.pack(pady=10)

        # Progress bar and label
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(pady=10)

        self.progress_label = tk.Label(self.progress_frame, text="Progress: 0%")
        self.progress_label.grid(row=0, column=0, padx=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=0, column=1, padx=5)

        # Create Matplotlib figure and axis
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.df = None
        self.ani = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find where "Pulse Chart" starts
        start_idx = next(i for i, line in enumerate(lines) if "Pulse Chart" in line) + 3  # Skip header lines
        
        # Extract only relevant numerical data
        pulse_data = []
        for line in lines[start_idx:]:
            values = line.strip().split(",")
            if len(values) == 3:  # Ensure only valid rows are processed
                try:
                    pulse_data.append([int(values[1]), float(values[2])])
                except ValueError:
                    continue  # Skip bad rows

        # Convert to DataFrame
        self.df = pd.DataFrame(pulse_data, columns=["Pulse Number", "Signal"])

        # Enable save button after successful load
        self.btn_save["state"] = tk.NORMAL

        # Start animated plot
        self.animate_plot()

    def animate_plot(self):
        # Get user-selected settings
        framerate = int(self.framerate_var.get())
        line_style = self.line_style_var.get()
        marker_style = self.marker_var.get()
        line_color = self.color_var.get()
        title = self.title_entry.get()

        self.ax.clear()
        self.ax.set_xlabel("Pulse Number")
        self.ax.set_ylabel("Signal (uV*sec)")
        self.ax.set_title(title)
        self.ax.grid(True)

        x_data, y_data = [], []
        line, = self.ax.plot([], [], marker=marker_style, linestyle=line_style, color=line_color)

        # Initialize progress bar
        self.progress_bar["maximum"] = len(self.df)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Progress: 0%")

        def update(frame):
            if frame < len(self.df):
                x_data.append(self.df["Pulse Number"].iloc[frame])
                y_data.append(self.df["Signal"].iloc[frame])
                line.set_data(x_data, y_data)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()

                # Update progress bar and label
                self.progress_bar["value"] = frame + 1
                progress_percent = int((frame + 1) / len(self.df) * 100)
                self.progress_label.config(text=f"Progress: {progress_percent}%")
                self.root.update_idletasks()  # Refresh the Tkinter window

                print(f"Frame {frame}: {x_data[-1]}, {y_data[-1]}")  # Debugging print
            return line,

        self.ani = animation.FuncAnimation(self.fig, update, frames=len(self.df), interval=framerate, repeat=True)

    def save_animation(self):
        if self.ani:
            filename = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
            if filename:
                writer = PillowWriter(fps=5)
                self.ani.save(filename, writer=writer)
                print(f"Animation saved as {filename}")

# Run the Tkinter application
root = tk.Tk()
app = PulsePlotter(root)
root.mainloop()