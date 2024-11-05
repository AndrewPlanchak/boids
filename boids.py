import pygame
import pygame_gui
import random

# Constants
WIDTH, HEIGHT = 1920, 1080
INITIAL_NUM_BOIDS = 500
INITIAL_MAX_SPEED = 6
INITIAL_MAX_FORCE = 0.3
INITIAL_PERCEPTION_RADIUS = 70
AVOIDANCE_RADIUS = INITIAL_PERCEPTION_RADIUS * 0.70
INITIAL_COLOR_BIAS = 0.2

def is_in_cone(boid, other_boid, cone_angle=90):
    to_other = other_boid.position - boid.position
    distance = to_other.length()
    
    if distance == 0:
        return False  # Ignore if the distance is zero to avoid division by zero

    to_other_normalized = to_other.normalize()
    forward = boid.velocity.normalize()

    angle = forward.angle_to(to_other_normalized)

    # Check if the angle is within the cone
    return abs(angle) < cone_angle / 2        # Calculate the angle between the boid's direction and the other boid's position
        
# Boid class
class Boid:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * INITIAL_MAX_SPEED
        self.acceleration = pygame.math.Vector2(0, 0)
        # Initialize with bright colors
        self.color = pygame.Color(
            random.randint(150, 255),  # Red
            random.randint(150, 255),  # Green
            random.randint(150, 255)   # Blue
        )
    def edges(self):
        if self.position.x > WIDTH: self.position.x = 0
        if self.position.x < 0: self.position.x = WIDTH
        if self.position.y > HEIGHT: self.position.y = 0
        if self.position.y < 0: self.position.y = HEIGHT

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity
        self.acceleration *= 0

    def apply_force(self, force):
        self.acceleration += force

    def flock(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohere(boids)
        separation = self.separate(boids)

        alignment *= 1
        cohesion *= 1
        separation *= 1.5

        self.apply_force(alignment)
        self.apply_force(cohesion)
        self.apply_force(separation)

        self.update_color(boids)

    def align(self, boids):
        perception_radius = PERCEPTION_RADIUS
        steering = pygame.math.Vector2(0, 0)
        total = 0

        for other in boids:
            if other != self and self.position.distance_to(other.position) < perception_radius and is_in_cone(self, other):
                steering += other.velocity
                total += 1

        if total > 0:
            steering /= total
            if steering.length() > 0:
                steering = steering.normalize() * MAX_SPEED
                steering -= self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)

        return steering

    def cohere(self, boids):
        perception_radius = PERCEPTION_RADIUS
        steering = pygame.math.Vector2(0, 0)
        total = 0

        for other in boids:
            if other != self and self.position.distance_to(other.position) < perception_radius and is_in_cone(self, other):
                steering += other.position
                total += 1

        if total > 0:
            steering /= total
            steering -= self.position
            if steering.length() > 0:
                steering = steering.normalize() * MAX_SPEED
                steering -= self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)

        return steering

    def separate(self, boids):
        perception_radius = AVOIDANCE_RADIUS
        steering = pygame.math.Vector2(0, 0)
        total = 0

        for other in boids:
            distance = self.position.distance_to(other.position)
            if other != self and distance < perception_radius and distance > 0:
                diff = self.position - other.position
                diff /= distance
                steering += diff
                total += 1

        if total > 0:
            steering /= total
            if steering.length() > 0:
                steering = steering.normalize() * MAX_SPEED
                steering -= self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)

        return steering

    def update_color(self, boids):
        perception_radius = PERCEPTION_RADIUS
        total_color_r = 0
        total_color_g = 0
        total_color_b = 0
        total = 0

        for other in boids:
            if other != self and self.position.distance_to(other.position) < perception_radius:
                total_color_r += other.color.r
                total_color_g += other.color.g
                total_color_b += other.color.b
                total += 1

        if total > 0:
            avg_color_r = total_color_r // total
            avg_color_g = total_color_g // total
            avg_color_b = total_color_b // total

            # Blend towards the average color with bias, but ensure minimum brightness
            self.color.r = int((self.color.r * COLOR_BIAS + avg_color_r * (1 - COLOR_BIAS)))
            self.color.g = int((self.color.g * COLOR_BIAS + avg_color_g * (1 - COLOR_BIAS)))
            self.color.b = int((self.color.b * COLOR_BIAS + avg_color_b * (1 - COLOR_BIAS)))

            # Prevent dullness by ensuring minimum brightness
            min_brightness = 50  # You can adjust this value
            self.color.r = max(min_brightness, self.color.r)
            self.color.g = max(min_brightness, self.color.g)
            self.color.b = max(min_brightness, self.color.b)

            # Ensure color components stay within 0-255 range
            self.color.r = max(0, min(255, self.color.r))
            self.color.g = max(0, min(255, self.color.g))
            self.color.b = max(0, min(255, self.color.b))

# Pygame setup
pygame.init()
pygame.display.set_caption('Boids Simulation')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create sliders
num_boids_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(10, 10, 300, 30),
    start_value=INITIAL_NUM_BOIDS,
    value_range=(1, 2000),
    manager=manager
)

pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(320, 50, 200, 30),
    text='Number of Boids : Min: 1, Max: 2000',
    manager=manager
)

max_speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(10, 50, 300, 30),
    start_value=INITIAL_MAX_SPEED,
    value_range=(1, 10),
    manager=manager
)

pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(320, 50, 200, 30),
    text='Max Speed: Min: 1, Max: 10',
    manager=manager
)

max_force_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(10, 90, 300, 30),
    start_value=INITIAL_MAX_FORCE,
    value_range=(0.01, 1.0),
    manager=manager
)

pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(320, 90, 200, 30),
    text='Max Force: Min: 0.01, Max: 1.0',
    manager=manager
)

perception_radius_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(10, 130, 300, 30),
    start_value=INITIAL_PERCEPTION_RADIUS,
    value_range=(10, 100),
    manager=manager
)

pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(320, 130, 200, 30),
    text='Perception Radius: Min: 10, Max: 100',
    manager=manager
)

color_bias_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(10, 170, 300, 30),
    start_value=INITIAL_COLOR_BIAS * 100,  # To use a percentage
    value_range=(0, 100),
    manager=manager
)

pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(320, 170, 200, 30),
    text='Color Bias: Min: 0%, Max: 100%',
    manager=manager
)

# Create current value labels
current_values = {
    'num_boids': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(450, 10, 100, 30), text=str(INITIAL_NUM_BOIDS), manager=manager),
    'max_speed': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(450, 50, 100, 30), text=str(INITIAL_MAX_SPEED), manager=manager),
    'max_force': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(450, 90, 100, 30), text=str(INITIAL_MAX_FORCE), manager=manager),
    'perception_radius': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(450, 130, 100, 30), text=str(INITIAL_PERCEPTION_RADIUS), manager=manager),
    'color_bias': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(450, 170, 100, 30), text=str(INITIAL_COLOR_BIAS * 100), manager=manager),
}

# Update constants from sliders
NUM_BOIDS = int(num_boids_slider.get_current_value())
MAX_SPEED = max_speed_slider.get_current_value()
MAX_FORCE = max_force_slider.get_current_value()
PERCEPTION_RADIUS = int(perception_radius_slider.get_current_value())
COLOR_BIAS = color_bias_slider.get_current_value() / 100  # Convert back to a fraction

# Update current value labels
current_values['num_boids'].set_text(str(NUM_BOIDS))
current_values['max_speed'].set_text(f"{MAX_SPEED:.2f}")
current_values['max_force'].set_text(f"{MAX_FORCE:.2f}")
current_values['perception_radius'].set_text(str(PERCEPTION_RADIUS))
current_values['color_bias'].set_text(f"{COLOR_BIAS * 100:.1f}")

# Create a reset button
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(10, 210, 100, 30),
    text='Reset',
    manager=manager
)

# Create initial boids
boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(INITIAL_NUM_BOIDS)]

# Initialize the selected boid
selected_boid = random.choice(boids)

def create_boids(num_boids):
    boids = []
    while len(boids) < num_boids:
        new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        # Check if the new boid's position is too close to existing boids
        if all(new_boid.position.distance_to(b.position) >= 5 for b in boids):  # Adjust the threshold as needed
            boids.append(new_boid)
    return boids

# Create initial boids
boids = create_boids(INITIAL_NUM_BOIDS)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == reset_button:
            # Reset values to defaults
            num_boids_slider.set_current_value(INITIAL_NUM_BOIDS)
            max_speed_slider.set_current_value(INITIAL_MAX_SPEED)
            max_force_slider.set_current_value(INITIAL_MAX_FORCE)
            perception_radius_slider.set_current_value(INITIAL_PERCEPTION_RADIUS)
            color_bias_slider.set_current_value(INITIAL_COLOR_BIAS * 100)  # Convert to percentage
            
    manager.process_events(event)

    # Update constants from sliders
    NUM_BOIDS = int(num_boids_slider.get_current_value())
    MAX_SPEED = max_speed_slider.get_current_value()
    MAX_FORCE = max_force_slider.get_current_value()
    PERCEPTION_RADIUS = int(perception_radius_slider.get_current_value())
    COLOR_BIAS = color_bias_slider.get_current_value() / 100  # Convert back to a fraction

    # Update boids if the number changes
    if len(boids) != NUM_BOIDS:
        boids = create_boids(NUM_BOIDS)  # Use the new function to create boids

    for boid in boids:
        boid.flock(boids)
        boid.update()
        boid.edges()

    # Render
    screen.fill((30, 30, 30))
    for boid in boids:
        pygame.draw.circle(screen, boid.color, (int(boid.position.x), int(boid.position.y)), 3)

    manager.update(0.016)  # Update the UI manager
    manager.draw_ui(screen)  # Draw the UI elements

    pygame.display.flip()  # Update the display
    clock.tick(144)  # Frame rate

pygame.quit()