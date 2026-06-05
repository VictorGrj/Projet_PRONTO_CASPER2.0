#####################################################################################################################################################
###################################################################### IMPORTS ######################################################################
#####################################################################################################################################################

# External imports
import pygame
import math
import time 
import threading

class Screen(threading.Thread):
    """
    Class that allows to display different facial expressions:
    - speaking: basic face with mouth animation
    - teaching: face with glasses and mouth animation
    - waiting: face with smile (no animation)
    - thinking: face with smile (no animation) and gears
    
    This class is designed to run as a single persistent thread throughout the robot's lifetime.
    """
#####################################################################################################################################################
#################################################################### CONSTRUCTOR ######################################################################
#####################################################################################################################################################

    def __init__(self, mode="speaking"):
        """
        This function is the constructor of the class.
        In:
            * self: Reference to the current object.
            * mode: Initial display mode ("speaking", "teaching", "waiting" or "thinking")
        Out:
            * A new instance of the class.
        """
        # ---------- initialise parallelism ----------
        super().__init__()
        self.daemon = True  # the thread automatically stops when main thread exits
        self._running = True
        self._lock = threading.Lock()
        self._mode = mode
        self._should_change_mode = False
        self._new_mode = None
        
#############################################################################################################################
#################################################### Thread methods #########################################################
#############################################################################################################################

    def run(self):
        """Main method executed in the thread."""        
        try:
            # Initialize pygame only once at the beginning
            pygame.init()
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            WIDTH, HEIGHT = screen.get_size()

            # Colors and states
            WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (30, 30, 30)

            # scale factor for the face
            additional_boost = 1.3  
            scale_factor = min(WIDTH / 1000, HEIGHT / 800) * additional_boost

            # Dimensions
            eye_radius = int(80 * scale_factor)
            eye_x_offset = int(250 * scale_factor)
            eye_y = HEIGHT // 3
            mouth_y = HEIGHT // 2 + int(30 * scale_factor)
            mouth_width = int(400 * scale_factor)
            mouth_height = int(175 * scale_factor)
            line_thickness = int(20 * scale_factor)

            # Mouth parameters
            centre_x = WIDTH // 2
            centre_y = mouth_y + int(110 * scale_factor)
            radius_x = int(190 * scale_factor)
            radius_y = int(90 * scale_factor)
            base_thickness = int(2 * scale_factor)
            max_open = int(30 * scale_factor)
            angle_bis = 0

            # Glasses points
            left_center = (WIDTH // 2 - int(250 * scale_factor), HEIGHT // 3 + int(20 * scale_factor))
            right_center = (WIDTH // 2 + int(250 * scale_factor), HEIGHT // 3 + int(20 * scale_factor))
            radius = int(150 * scale_factor)

            # Gears parameters (3 small gears in top right corner)
            gear_margin = int(50 * scale_factor)
            
            # Large gear (bottom left of gear group)
            large_gear_x = WIDTH - gear_margin - int(60 * scale_factor)
            large_gear_y = gear_margin + int(60 * scale_factor)
            large_inner_radius = int(18 * scale_factor)
            large_outer_radius = int(28 * scale_factor)
            large_center_radius = int(10 * scale_factor)
            
            # Medium gear (top right of gear group)
            medium_gear_x = WIDTH - gear_margin - int(20 * scale_factor)
            medium_gear_y = gear_margin + int(20 * scale_factor)
            medium_inner_radius = int(12 * scale_factor)
            medium_outer_radius = int(20 * scale_factor)
            medium_center_radius = int(7 * scale_factor)
            
            # Small gear (bottom right of gear group)
            small_gear_x = WIDTH - gear_margin - int(15 * scale_factor)
            small_gear_y = gear_margin + int(80 * scale_factor)
            small_inner_radius = int(10 * scale_factor)
            small_outer_radius = int(16 * scale_factor)
            small_center_radius = int(6 * scale_factor)

            clock = pygame.time.Clock()
            
            # Main display loop - will run until program exits
            while self._running:
                # Check if mode should be changed
                with self._lock:
                    if self._should_change_mode:
                        old_mode = self._mode
                        self._mode = self._new_mode
                        self._should_change_mode = False
                
                # Clear screen
                screen.fill(WHITE)
                
                # Eyes drawing (common to all modes)
                pygame.draw.circle(screen, BLACK, (WIDTH // 2 - eye_x_offset, eye_y + int(20 * scale_factor)), eye_radius)
                pygame.draw.circle(screen, BLACK, (WIDTH // 2 + eye_x_offset, eye_y + int(20 * scale_factor)), eye_radius)
                
                # Mode-specific drawing
                if self._mode in ["speaking", "teaching"]:
                    # Talking mouth animation for speaking and teaching modes
                    open_offset = abs(math.sin(angle_bis)) * max_open
                    angle_bis += 0.2
                    
                    # Mouth shape
                    bottom_arc = []
                    for i in range(50 + 1):
                        angle_val = 0 + (math.pi - 0) * i / 50
                        x = centre_x + radius_x * math.cos(angle_val)
                        y = centre_y + radius_y * math.sin(angle_val) + base_thickness + open_offset
                        bottom_arc.append((x, y))

                    left = (centre_x - radius_x, centre_y - base_thickness)
                    right = (centre_x + radius_x, centre_y - base_thickness)
                    mouth_shape = [left, right] + bottom_arc
                    pygame.draw.lines(screen, BLACK, True, mouth_shape, line_thickness)
                    
                    # Add glasses for teaching mode
                    if self._mode == "teaching":
                        pygame.draw.circle(screen, GRAY, left_center, radius, line_thickness)
                        pygame.draw.circle(screen, GRAY, right_center, radius, line_thickness)
                        pygame.draw.line(screen, GRAY, (left_center[0] + radius, left_center[1]), 
                                        (right_center[0] - radius, right_center[1]), line_thickness)
                        pygame.draw.line(screen, GRAY, (left_center[0] - radius, left_center[1]), 
                                        (left_center[0] - radius - int(120 * scale_factor), left_center[1] - int(40 * scale_factor)), 
                                        line_thickness)
                        pygame.draw.line(screen, GRAY, (right_center[0] + radius, right_center[1]), 
                                        (right_center[0] + radius + int(120 * scale_factor), right_center[1] - int(40 * scale_factor)), 
                                        line_thickness)
                
                elif self._mode in ["waiting", "thinking"]:
                    # Smile arc for both modes
                    pygame.draw.arc(screen, BLACK, (WIDTH // 2 - mouth_width // 2, mouth_y, 
                                                   mouth_width, mouth_height), 3.14, 6.28, line_thickness // 2)
                    
                    if self._mode == "thinking":
                        # Draw the three small black gears in top right corner
                        # Large gear (8 teeth)
                        self.draw_gear(screen, large_gear_x, large_gear_y, large_inner_radius, large_outer_radius, 8, BLACK)
                        pygame.draw.circle(screen, WHITE, (large_gear_x, large_gear_y), large_center_radius)
                        
                        # Medium gear (6 teeth)
                        self.draw_gear(screen, medium_gear_x, medium_gear_y, medium_inner_radius, medium_outer_radius, 6, BLACK)
                        pygame.draw.circle(screen, WHITE, (medium_gear_x, medium_gear_y), medium_center_radius)
                        
                        # Small gear (6 teeth)
                        self.draw_gear(screen, small_gear_x, small_gear_y, small_inner_radius, small_outer_radius, 6, BLACK)
                        pygame.draw.circle(screen, WHITE, (small_gear_x, small_gear_y), small_center_radius)
                    
                        # Smile arc for waiting mode
                        pygame.draw.arc(screen, BLACK, (WIDTH // 2 - mouth_width // 2, mouth_y, 
                                                        mouth_width, mouth_height), 3.14, 6.28, line_thickness // 2)
                        

            
                # Update display
                pygame.display.flip()
                clock.tick(30)  # Limit to 30 FPS to save CPU
    
        except Exception as e:
            print(f"Screen thread error: {e}")

        finally:
            pygame.quit()
    
    def stop(self):
        """
        Stop Screen thread - should only be called when the application is shutting down.
        For normal operation, use change_mode() instead.
        """
        with self._lock:
            self._running = False
    
    def change_mode(self, new_mode):
        """
        Change the display mode without stopping the thread
        In:
            * self: Reference to the current object.
            * new_mode: New display mode ("speaking", "teaching", "waiting" or "thinking")
        Returns:
            * True if mode change request was accepted, False otherwise
        """
        if new_mode not in ["speaking", "teaching", "waiting", "thinking"]:
            print(f"Invalid mode requested: {new_mode}. Staying in current mode: {self._mode}")
            return False
            
        with self._lock:
            if self._mode == new_mode:
                # No change needed
                return True
                
            self._new_mode = new_mode
            self._should_change_mode = True
            
        return True

    def draw_gear(self, screen, center_x, center_y, inner_radius, outer_radius, teeth_count, color):
        """Draw a gear shape with specified parameters."""
        points = []
        angle_step = 2 * math.pi / (teeth_count * 2)
        
        for i in range(teeth_count * 2):
            angle = i * angle_step
            if i % 2 == 0:  # Outer points (teeth tips)
                radius = outer_radius
            else:  # Inner points (between teeth)
                radius = inner_radius
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(screen, color, points)
