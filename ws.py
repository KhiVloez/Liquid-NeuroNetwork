import pygame
import math
import numpy as np
import time  # Import the time module for time-related functions
import librosa
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Wave Propagation Simulator")
clock = pygame.time.Clock()

# Physical Constants
GRID_SIZE = 10  # Grid size (increased for higher resolution)
SPACING = 30  # Spacing between dots
FOV = 600
DEFAULT_FREQS = [0, 0, 0]  # Default frequencies

# Camera Position
camera_x, camera_y, camera_z = 0, 0, -500
camera_angle_x, camera_angle_y = 0, 0

# 3D Points for Cube
cube_points = []
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        for z in range(GRID_SIZE):
            cube_points.append(((x - GRID_SIZE // 2) * SPACING, 
                                (y - GRID_SIZE // 2) * SPACING, 
                                (z - GRID_SIZE // 2) * SPACING))

def project_3d_to_2d(x, y, z):
    """ Converts 3D coordinates to 2D for rendering. """
    scale = FOV / (FOV + z - camera_z)
    px = int(WIDTH // 2 + (x - camera_x) * scale)
    py = int(HEIGHT // 2 - (y - camera_y) * scale)
    return px, py

# Define a wave origin at the center of the grid
wave_origin = (0, 0, 0)

# Generate wave propagation intensity based on frequency and distance
def get_wave_intensity(x, y, z, sim_time, frequencies, external_input):
    """ Compute wave intensity influenced by external input (audio/video). """
    intensity = 0
    distance = math.sqrt((x - wave_origin[0])**2 + (y - wave_origin[1])**2 + (z - wave_origin[2])**2)
    
    for freq in frequencies:
        wave = np.sin(2 * np.pi * freq * (sim_time - distance / (1 + freq * 0.01)))
        intensity += wave

    # Inject external input (audio/video)
    intensity += external_input[x % GRID_SIZE, y % GRID_SIZE] * 0.5  # Scale appropriately
    return intensity

# Function to encode audio into a 2D grid pattern
def encode_audio(audio_file, grid_size):
    # Load audio and compute spectrogram
    y, sr = librosa.load(audio_file, sr=22050)
    S = np.abs(librosa.stft(y, n_fft=grid_size**2))
    
    # Normalize and reshape to match the grid
    S = S / np.max(S)
    return S.reshape((grid_size, grid_size))

# Extract features from the wave environment
def extract_features(grid, sim_time, audio_input):
    """ Flatten the 3D wave states into a feature vector. """
    return np.array([get_wave_intensity(x, y, z, sim_time, DEFAULT_FREQS, audio_input) for x, y, z in cube_points]).flatten()

# Set up the logistic regression model for readout layer
clf = LogisticRegression(max_iter=1000)

# Simulation time control
sim_time = 0  # Renamed the simulation time variable

# Initialize variables for input mode
running = True
in_input_mode = False
user_input = ""
selected_frequency_index = None

# Snapshots
snapshot_start_time = None
snapshot_counter = 0
snapshot_interval = 1  # seconds
snapshot_filename = "cube_snapshots.txt"

# Time control for smooth wave animation
sim_time = 0

# Training data for the readout layer (audio-based features)
X_train, y_train = [], []

# Encode some initial audio data for training
audio_input = encode_audio("audio.wav", GRID_SIZE)

# Generate training data (for this example, using random labels)
for _ in range(100):  # Generate 100 training samples
    X_train.append(extract_features(cube_points, sim_time, audio_input))
    y_train.append(np.random.randint(0, 2))  # Random binary labels for simplicity

# Train a simple logistic regression classifier
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2)
clf.fit(X_train, y_train)

# Main simulation loop
while running:
    clock.tick(15)  # Control loop speed to allow for smoother visuals
    screen.fill((0, 0, 0))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Start input mode when the "" key is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:  # "" key for input mode
                in_input_mode = True
                user_input = ""  # Clear the input string
                selected_frequency_index = None  # Reset frequency index selection

            elif in_input_mode:
                if selected_frequency_index is None:
                    # If no frequency index selected, prompt for one
                    if event.key in [pygame.K_0, pygame.K_1, pygame.K_2]:
                        selected_frequency_index = int(event.unicode)  # Set the selected frequency index
                        user_input = ""  # Clear user input for the frequency value
                elif event.key == pygame.K_RETURN:
                    # Update the selected frequency when the user presses Enter
                    try:
                        new_freq = float(user_input)
                        DEFAULT_FREQS[selected_frequency_index] = new_freq  # Update the selected frequency
                    except ValueError:
                        pass  # If invalid input, just ignore
                    in_input_mode = False  # Exit input mode
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]  # Delete last character
                else:
                    user_input += event.unicode  # Add character to input string

        # Mouse dragging for rotation
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button click
                mouse_dragging = True
                last_x, last_y = event.pos  # Store the mouse position when dragging starts

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button release
                mouse_dragging = False  # Stop dragging

        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging:
                dx, dy = event.pos[0] - last_x, event.pos[1] - last_y  # Get the change in mouse position
                camera_angle_y += dx * 0.1  # Rotate around the y-axis (left/right)
                camera_angle_x += dy * 0.1  # Rotate around the x-axis (up/down)
                last_x, last_y = event.pos  # Update the last mouse position

    # Camera Controls (keyboard)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: camera_z += 20
    if keys[pygame.K_s]: camera_z -= 20
    if keys[pygame.K_a]: camera_x -= 20
    if keys[pygame.K_d]: camera_x += 20

    # Update time for smooth wave animation
    sim_time += 0.02

    # Draw dots with increased density
    for point in cube_points:
        x, y, z = point

        # Rotate point around the x and y axes based on the camera angles
        rotated_x = x * math.cos(camera_angle_y) - z * math.sin(camera_angle_y)
        rotated_z = x * math.sin(camera_angle_y) + z * math.cos(camera_angle_y)
        rotated_y = y * math.cos(camera_angle_x) - rotated_z * math.sin(camera_angle_x)
        rotated_z = y * math.sin(camera_angle_x) + rotated_z * math.cos(camera_angle_x)

        # Project the rotated 3D point to 2D space
        px, py = project_3d_to_2d(rotated_x, rotated_y, rotated_z)
        
        # Calculate wave intensity based on time and position
        wave_intensity = get_wave_intensity(x, y, z, sim_time, DEFAULT_FREQS, audio_input)
        
        # Map wave intensity to brightness
        brightness = int(127 + 128 * wave_intensity)
        
        # Ensure brightness stays within the valid range [0, 255]
        brightness = max(0, min(255, brightness))
        
        # Color with the adjusted brightness
        color = (brightness, brightness, 255)

        pygame.draw.circle(screen, color, (px, py), 3)  # Increase the size of dots for more visibility

    # Use the trained classifier to predict
    if len(X_train) > 0:
        pred = clf.predict([extract_features(cube_points, sim_time, audio_input)])
        print("Prediction:", pred)  # Print prediction (for debugging)

    pygame.display.flip()

pygame.quit()
