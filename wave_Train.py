import pygame
import math
import numpy as np
import json

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Wave Propagation Simulator with Learning")
clock = pygame.time.Clock()

# Physical Constants
GRID_SIZE = 18
SPACING = 30
FOV = 600
DEFAULT_FREQS = [0, 0, 0]

# Camera Position
camera_x, camera_y, camera_z = 0, 0, -500
camera_angle_x, camera_angle_y = 0, 0

# Training Data Storage
TRAINING_FILE = "training_data.json"

def load_training_data():
    """Load training data from a JSON file."""
    try:
        with open(TRAINING_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_training_data(data):
    """Save updated training data to JSON."""
    with open(TRAINING_FILE, 'w') as file:
        json.dump(data, file, indent=4)

training_data = load_training_data()
wave_memory = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE))

# 3D Points for Cube
cube_points = [((x - GRID_SIZE // 2) * SPACING, 
                (y - GRID_SIZE // 2) * SPACING, 
                (z - GRID_SIZE // 2) * SPACING)
                for x in range(GRID_SIZE)
                for y in range(GRID_SIZE)
                for z in range(GRID_SIZE)]

def project_3d_to_2d(x, y, z):
    """Project 3D points to 2D screen space."""
    scale = FOV / (FOV + z - camera_z)
    px = int(WIDTH // 2 + (x - camera_x) * scale)
    py = int(HEIGHT // 2 - (y - camera_y) * scale)
    return px, py

def get_wave_intensity(x, y, z, sim_time):
    """Calculate wave intensity at a given point."""
    return wave_memory[x % GRID_SIZE, y % GRID_SIZE, z % GRID_SIZE] * np.sin(2 * np.pi * sim_time)

def update_waves(input_text):
    """Update wave memory based on user input and learning model."""
    global training_data

    input_text = input_text.lower().strip()
    if input_text in training_data:
        response_data = training_data[input_text]
        response = response_data["response"]
        confidence = response_data["confidence"]

        print(f"Response: {response} (Confidence: {confidence:.2f})")

        # Encode response into the wave system (stronger response if confidence is high)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                for z in range(GRID_SIZE):
                    wave_memory[x, y, z] = np.random.uniform(-1, 1) * confidence
    else:
        print("I don't know that yet! Teach me?")
        awaiting_feedback.append(input_text)  # Store for learning

def reinforce_learning(input_text, response_text):
    """Update or reinforce the model with user feedback."""
    global training_data

    if input_text in training_data:
        training_data[input_text]["response"] = response_text
        training_data[input_text]["confidence"] = min(1.0, training_data[input_text]["confidence"] + 0.1)  # Increase confidence
    else:
        training_data[input_text] = {"response": response_text, "confidence": 0.5}

    save_training_data(training_data)
    print(f"Learned: '{input_text}' → '{response_text}'")

# Input Handling
running = True
in_input_mode = False
awaiting_feedback = []
user_input = ""

sim_time = 0
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:
                in_input_mode = True
                user_input = ""
            elif in_input_mode:
                if event.key == pygame.K_RETURN:
                    if awaiting_feedback:
                        reinforce_learning(awaiting_feedback.pop(0), user_input)  # Train the model
                    else:
                        update_waves(user_input)
                    in_input_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

    # Camera Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: camera_angle_y -= 0.05
    if keys[pygame.K_RIGHT]: camera_angle_y += 0.05
    if keys[pygame.K_UP]: camera_angle_x -= 0.05
    if keys[pygame.K_DOWN]: camera_angle_x += 0.05
    if keys[pygame.K_w]: camera_z += 20
    if keys[pygame.K_s]: camera_z -= 20
    if keys[pygame.K_a]: camera_x -= 20
    if keys[pygame.K_d]: camera_x += 20

    sim_time += 0.02

    # Render 3D Points
    for x, y, z in cube_points:
        px, py = project_3d_to_2d(x, y, z)
        wave_intensity = get_wave_intensity(x, y, z, sim_time)
        brightness = int(127 + 128 * wave_intensity)
        brightness = max(0, min(255, brightness))
        color = (brightness, brightness, 255)
        pygame.draw.circle(screen, color, (px, py), 3)

    # Display User Input
    if in_input_mode:
        font = pygame.font.SysFont('Arial', 24)
        input_text = font.render(f"Enter text: {user_input}", True, (255, 255, 255))
        screen.blit(input_text, (10, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
