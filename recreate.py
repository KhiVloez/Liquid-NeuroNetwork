import pygame
import time

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Recreate Snapshot")

# Grid parameters
GRID_SIZE = 18
SPACING = 30

# Color setup
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Dot class for storing each dot's position and intensity
class Dot:
    def __init__(self, x, y, z, intensity):
        self.x = x
        self.y = y
        self.z = z
        self.intensity = intensity

    def draw(self):
        color = (int(255 * abs(self.intensity)), 0, int(255 * (1 - abs(self.intensity))))
        pygame.draw.circle(screen, color, (self.x, self.y), 5)

# Load snapshots from the file
def load_snapshots(filename="cube_snapshots.txt"):
    snapshots = []
    with open(filename, 'r') as file:
        snapshot_data = file.read().split("\n\n")
        
        for snapshot in snapshot_data:
            lines = snapshot.split("\n")
            
            if len(lines) > 0 and "at time" in lines[0]:
                try:
                    time_stamp_str = lines[0].split("at time")[1].strip()
                    time_stamp = float(time_stamp_str.split(":")[0])
                except (IndexError, ValueError) as e:
                    print(f"Error processing time from snapshot: {e}")
                    continue

                points = []
                for line in lines[1:]:
                    if line.startswith("Point"):
                        try:
                            parts = line.split(",")
                            point_data = parts[0].split(":")[1].strip()[1:-1].split(",")
                            x, y, z = map(int, point_data)
                            intensity = float(parts[1].split(":")[1].strip())
                            points.append((x, y, z, intensity))
                        except (IndexError, ValueError) as e:
                            print(f"Error processing point: {e} - Line: {line}")
                            continue

                snapshots.append((time_stamp, points))

    return snapshots

# Main loop for recreating the snapshot
def recreate_snapshots():
    snapshots = load_snapshots()
    if not snapshots:
        print("No snapshots found!")
        return

    for snapshot in snapshots:
        time_stamp, points = snapshot
        dots = [Dot(x, y, z, intensity) for x, y, z, intensity in points]

        screen.fill(BLACK)

        # Simulate the environment by drawing the dots
        for dot in dots:
            dot.draw()

        pygame.display.flip()
        time.sleep(1)  # Show each snapshot for 1 second

# Start the recreation process
recreate_snapshots()

pygame.quit()
