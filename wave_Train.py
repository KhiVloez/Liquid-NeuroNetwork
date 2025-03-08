import pygame
import math
import numpy as np
import time

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

# Learning Model Data
training_data = {"hello": "how are you"}  # Simple memory for learning
wave_memory = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE))

# 3D Points for Cube
cube_points = []
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        for z in range(GRID_SIZE):
            cube_points.append(((x - GRID_SIZE // 2) * SPACING, 
                                (y - GRID_SIZE // 2) * SPACING, 
                                (z - GRID_SIZE // 2) * SPACING))

def project_3d_to_2d(x, y, z):
    scale = FOV / (FOV + z - camera_z)
    px = int(WIDTH // 2 + (x - camera_x) * scale)
    py = int(HEIGHT // 2 - (y - camera_y) * scale)
    return px, py

def get_wave_intensity(x, y, z, sim_time):
    return wave_memory[x % GRID_SIZE, y % GRID_SIZE, z % GRID_SIZE] * np.sin(2 * np.pi * sim_time)

def update_waves(input_text):
    if input_text in training_data:
        response = training_data[input_text]
        print("Response:", response)
        # Encode response into the wave system
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                for z in range(GRID_SIZE):
                    wave_memory[x, y, z] = np.random.uniform(-1, 1) if response else 0
    else:
        print("I don't know that yet.")
        training_data[input_text] = "?"  # Placeholder for learning

running = True
in_input_mode = False
user_input = ""
sim_time = 0
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:
                in_input_mode = True
                user_input = ""
            elif in_input_mode:
                if event.key == pygame.K_RETURN:
                    update_waves(user_input)
                    in_input_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

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

    for point in cube_points:
        x, y, z = point
        px, py = project_3d_to_2d(x, y, z)
        wave_intensity = get_wave_intensity(x, y, z, sim_time)
        brightness = int(127 + 128 * wave_intensity)
        brightness = max(0, min(255, brightness))
        color = (brightness, brightness, 255)
        pygame.draw.circle(screen, color, (px, py), 3)

    if in_input_mode:
        font = pygame.font.SysFont('Arial', 24)
        input_text = font.render(f"Enter text: {user_input}", True, (255, 255, 255))
        screen.blit(input_text, (10, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
