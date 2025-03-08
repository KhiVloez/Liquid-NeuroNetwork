import pygame
import math
import numpy as np
import time  # Import the time module for time-related functions

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Wave Propagation Simulator")
clock = pygame.time.Clock()

# Physical Constants
GRID_SIZE = 18  # Grid size (increased for higher resolution)
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

# Generate wave propagation intensity based on frequency and distance
def get_wave_intensity(x, y, z, sim_time, frequencies):
    """ Calculate wave intensity at a point in space and time. """
    intensity = 0
    for freq in frequencies:
        # Sinusoidal wave function with respect to time and distance from the camera
        distance = math.sqrt((x - camera_x)**2 + (y - camera_y)**2 + (z - camera_z)**2)
        wave = np.sin(2 * np.pi * freq * (sim_time - distance / (1 + freq * 0.01)))
        intensity += wave
    return intensity

# Start with no sound, just the dynamic visual representation
running = True
in_input_mode = False
user_input = ""
selected_frequency_index = None

# Time control for smooth wave animation
sim_time = 0  # Renamed the simulation time variable

# Snapshots
snapshot_start_time = None
snapshot_counter = 0
snapshot_interval = 1  # seconds
snapshot_filename = "cube_snapshots.txt"

# Function to save the state to a text file
def save_snapshot():
    with open(snapshot_filename, 'a') as file:
        file.write(f"Snapshot {snapshot_counter} at time {sim_time}:\n")
        for point in cube_points:
            x, y, z = point
            # Calculate wave intensity
            wave_intensity = get_wave_intensity(x, y, z, sim_time, DEFAULT_FREQS)
            # Save the point and its intensity
            file.write(f"Point: ({x}, {y}, {z}), Intensity: {wave_intensity}\n")
        file.write("\n")

while running:
    clock.tick(60)  # Control loop speed to allow for smoother visuals
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

            # Trigger snapshot saving when "p" is pressed
            if event.key == pygame.K_p:
                snapshot_start_time = time.time()  # Record the start time of the snapshots
                snapshot_counter = 0  # Reset snapshot counter
                # Clear the previous file content
                with open(snapshot_filename, 'w') as file:
                    file.write("Cube Snapshots:\n\n")

    # Camera Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: camera_angle_y -= 0.05
    if keys[pygame.K_RIGHT]: camera_angle_y += 0.05
    if keys[pygame.K_UP]: camera_angle_x -= 0.05
    if keys[pygame.K_DOWN]: camera_angle_x += 0.05
    if keys[pygame.K_w]: camera_z += 20
    if keys[pygame.K_s]: camera_z -= 20
    if keys[pygame.K_a]: camera_x -= 20
    if keys[pygame.K_d]: camera_x += 20

    # Update time for smooth wave animation
    sim_time += 0.02

    # Save snapshot every second for 30 seconds when triggered
    if snapshot_start_time is not None:
        elapsed_time = time.time() - snapshot_start_time
        if elapsed_time >= snapshot_interval * snapshot_counter and snapshot_counter < 30:
            save_snapshot()  # Save the current state
            snapshot_counter += 1  # Increment the snapshot counter

    # Draw dots with increased density
    for point in cube_points:
        x, y, z = point
        px, py = project_3d_to_2d(x, y, z)
        
        # Calculate wave intensity based on time and position
        wave_intensity = get_wave_intensity(x, y, z, sim_time, DEFAULT_FREQS)
        
        # Map wave intensity to brightness
        brightness = int(127 + 128 * wave_intensity)
        
        # Ensure brightness stays within the valid range [0, 255]
        brightness = max(0, min(255, brightness))
        
        # Color with the adjusted brightness
        color = (brightness, brightness, 255)

        pygame.draw.circle(screen, color, (px, py), 3)  # Increase the size of dots for more visibility

    # Display input prompt if in input mode
    if in_input_mode:
        font = pygame.font.SysFont('Arial', 24)
        if selected_frequency_index is None:
            input_text = font.render("Select Frequency (0, 1, 2):", True, (255, 255, 255))
        else:
            input_text = font.render(f"Enter Frequency for {selected_frequency_index}: {user_input}", True, (255, 255, 255))
        screen.blit(input_text, (10, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()