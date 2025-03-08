import numpy as np
import pygame
import math

# Simulation parameters
GRID_SIZE = 18
SPACING = 30
CLOCK_TICK = 15
DEFAULT_FREQS = [0, 0, 0]

def text_to_frequencies(text):
    """Convert a string into a list of frequency values."""
    return [ord(char) % 10 + 1 for char in text]  # Simple ASCII-based mapping

def get_wave_intensity(x, y, z, sim_time, frequencies):
    """Compute wave response to input frequencies"""
    intensity = 0
    for i, freq in enumerate(frequencies):
        distance = math.sqrt(x**2 + y**2 + z**2)
        wave = np.sin(2 * np.pi * freq * (sim_time - distance / (1 + freq * 0.01)))
        intensity += wave * (0.9 ** i)  # Add decay to spread learning effect
    return intensity

def capture_state():
    """Save the system state as an array of wave intensities."""
    state_matrix = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE))
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for z in range(GRID_SIZE):
                state_matrix[x, y, z] = get_wave_intensity(x, y, z, 0, DEFAULT_FREQS)
    return state_matrix

def compute_loss(predicted_state, target_state):
    """Calculate error between actual wave state and expected output."""
    return np.mean((predicted_state - target_state) ** 2)  # Mean Squared Error (MSE)

def train_network(input_text, target_text, epochs=100):
    """Train the wave system to respond to an input correctly."""
    global DEFAULT_FREQS
    input_frequencies = text_to_frequencies(input_text)
    target_frequencies = text_to_frequencies(target_text)

    for epoch in range(epochs):
        DEFAULT_FREQS = input_frequencies  # Set initial state
        predicted_state = capture_state()
        
        # Simulate expected output state
        DEFAULT_FREQS = target_frequencies
        target_state = capture_state()

        # Compute loss
        loss = compute_loss(predicted_state, target_state)
        print(f"Epoch {epoch + 1}, Loss: {loss}")

        # Adjust frequencies to minimize error
        DEFAULT_FREQS = [f - 0.01 * loss for f in DEFAULT_FREQS]  # Learning step

def wave_to_text(wave_state):
    """Convert final wave intensities back into text."""
    char_list = [chr(int(abs(val) * 10) % 128) for val in wave_state.flatten()[:15]]
    return "".join(char_list)

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    sim_time = 0
    running = True
    
    # Training the network
    train_network("hello how are you", "I am fine", epochs=50)
    
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    response_wave = capture_state()
                    ai_response = wave_to_text(response_wave)
                    print(f"AI Response: {ai_response}")
        
        pygame.display.flip()
        sim_time += 0.1
        clock.tick(CLOCK_TICK)
    
    pygame.quit()

if __name__ == "__main__":
    main()
