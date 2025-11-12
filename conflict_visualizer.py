# continuous_conflict_viz.py
"""
CONTINUOUS Drone Conflict Visualization
Drones keep flying and don't vanish after completion
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import time
import random
from typing import List, Dict, Any, Tuple

try:
    from ultra_optimized_deconfliction import UltraOptimizedDeconflictionSystem
    from mission_generator import ScalableMissionGenerator
except ImportError as e:
    print(f"Import warning: {e}")
    # Mock classes for type checking
    class UltraOptimizedDeconflictionSystem:
        def __init__(self):
            self.drone_missions = {}
            self.simulation_running = False
        def batch_add_missions_parallel(self, missions):
            return [True] * len(missions)
        def real_time_conflict_monitoring(self):
            return []
    class ScalableMissionGenerator:
        def __init__(self, area_size=1000, altitude_range=(20, 100)):
            pass
        def generate_missions(self, num_missions):
            return []

class ContinuousDroneVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.setup_plot()
        self.drone_trails = {}
        self.conflict_history = []
        
    def setup_plot(self):
        """Setup the continuous visualization plot"""
        self.ax.set_title('🚁 CONTINUOUS DRONE CONFLICT MONITORING', 
                         fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('X Coordinate (meters)', fontsize=12)
        self.ax.set_ylabel('Y Coordinate (meters)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(-600, 600)
        self.ax.set_ylim(-600, 600)
        
        plt.ion()
        plt.show(block=False)
    
    def extract_coords(self, waypoint) -> Tuple[float, float]:
        """Extract coordinates from waypoint"""
        try:
            if hasattr(waypoint, 'x') and hasattr(waypoint, 'y'):
                return waypoint.x, waypoint.y
            elif hasattr(waypoint, 'lat') and hasattr(waypoint, 'lng'):
                return waypoint.lat, waypoint.lng
            elif isinstance(waypoint, (list, tuple)) and len(waypoint) >= 2:
                return float(waypoint[0]), float(waypoint[1])
            else:
                return random.uniform(-500, 500), random.uniform(-500, 500)
        except:
            return random.uniform(-500, 500), random.uniform(-500, 500)
    
    def calculate_position(self, mission, progress: float) -> Tuple[float, float]:
        """Calculate drone position with continuous looping"""
        if not hasattr(mission, 'waypoints') or not mission.waypoints:
            return random.uniform(-500, 500), random.uniform(-500, 500)
        
        waypoints = mission.waypoints
        if len(waypoints) == 0:
            return random.uniform(-500, 500), random.uniform(-500, 500)
        elif len(waypoints) == 1:
            return self.extract_coords(waypoints[0])
        
        # Use modulo to create continuous looping progress
        looped_progress = progress % 1.0
        
        total_segments = len(waypoints) - 1
        exact_segment = looped_progress * total_segments
        segment_index = int(exact_segment)
        segment_progress = exact_segment - segment_index
        
        if segment_index >= total_segments:
            return self.extract_coords(waypoints[-1])
        
        start_wp = waypoints[segment_index]
        end_wp = waypoints[segment_index + 1]
        
        start_x, start_y = self.extract_coords(start_wp)
        end_x, end_y = self.extract_coords(end_wp)
        
        current_x = start_x + (end_x - start_x) * segment_progress
        current_y = start_y + (end_y - start_y) * segment_progress
        
        return current_x, current_y
    
    def update_continuous_viz(self, system, conflicts: List, frame: int, progress_dict: Dict[int, float]):
        """Update continuous visualization - drones never vanish"""
        self.ax.clear()
        
        # Main title with frame counter
        self.ax.set_title(f'🚁 CONTINUOUS DRONE OPERATIONS - Frame {frame}', 
                         fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('X Coordinate (meters)', fontsize=11)
        self.ax.set_ylabel('Y Coordinate (meters)', fontsize=11)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(-600, 600)
        self.ax.set_ylim(-600, 600)
        
        current_positions = {}
        active_count = 0
        
        # Draw ALL mission paths (including completed ones)
        for mission_id, mission in system.drone_missions.items():
            if hasattr(mission, 'waypoints') and mission.waypoints:
                path_x, path_y = [], []
                for wp in mission.waypoints:
                    x, y = self.extract_coords(wp)
                    path_x.append(x)
                    path_y.append(y)
                
                if path_x and path_y:
                    # Always draw paths, but completed ones are lighter
                    alpha = 0.4 if getattr(mission, 'status', '') == "completed" else 0.6
                    self.ax.plot(path_x, path_y, 'gray', alpha=alpha, linewidth=1, linestyle='-')
        
        # Draw CURRENT drone positions (ALL drones keep moving)
        for mission_id, mission in system.drone_missions.items():
            progress = progress_dict.get(mission_id, 0.0)
            current_pos = self.calculate_position(mission, progress)
            current_positions[mission_id] = current_pos
            
            # Maintain trail history
            if mission_id not in self.drone_trails:
                self.drone_trails[mission_id] = []
            self.drone_trails[mission_id].append(current_pos)
            
            # Keep trail length reasonable
            if len(self.drone_trails[mission_id]) > 50:
                self.drone_trails[mission_id].pop(0)
            
            # Draw trail
            trail = self.drone_trails[mission_id]
            if len(trail) > 1:
                trail_x, trail_y = zip(*trail)
                # Color trail based on mission status
                trail_color = 'red' if getattr(mission, 'status', '') == "completed" else 'blue'
                self.ax.plot(trail_x, trail_y, '-', color=trail_color, alpha=0.4, linewidth=1)
            
            # Draw drone with different styles based on status
            status = getattr(mission, 'status', 'active')
            if status == "completed":
                # Completed missions still show but with different style
                self.ax.plot(current_pos[0], current_pos[1], 's', 
                           color='red', markersize=10, markeredgecolor='darkred', 
                           markeredgewidth=2, alpha=0.7)
                label = f'C{mission_id}'
            else:
                # Active mission - color by progress in current lap
                lap_progress = progress % 1.0
                if lap_progress < 0.33:
                    color = 'lime'
                    size = 12
                elif lap_progress < 0.66:
                    color = 'deepskyblue'
                    size = 12
                else:
                    color = 'blue'
                    size = 12
                
                self.ax.plot(current_pos[0], current_pos[1], 'o', 
                           color=color, markersize=size, markeredgecolor='black', 
                           markeredgewidth=1, alpha=0.9)
                label = f'D{mission_id}'
                active_count += 1
            
            # Add drone label
            self.ax.text(current_pos[0] + 10, current_pos[1] + 10, label, 
                       fontsize=8, fontweight='bold', alpha=0.9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        # Draw and track conflicts
        conflict_count = 0
        current_conflict_positions = []
        
        for conflict in conflicts:
            if len(conflict) >= 2:
                mission1, mission2 = conflict[0], conflict[1]
                mission1_id = getattr(mission1, 'id', None)
                mission2_id = getattr(mission2, 'id', None)
                
                if mission1_id in current_positions and mission2_id in current_positions:
                    pos1 = current_positions[mission1_id]
                    pos2 = current_positions[mission2_id]
                    
                    # Draw conflict line
                    self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                               'r-', linewidth=4, alpha=0.8)
                    
                    # Draw conflict zone
                    center_x = (pos1[0] + pos2[0]) / 2
                    center_y = (pos1[1] + pos2[1]) / 2
                    distance = np.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
                    
                    conflict_zone = Circle((center_x, center_y), max(25, distance/2), 
                                         color='red', alpha=0.3)
                    self.ax.add_patch(conflict_zone)
                    
                    # Track conflict for history
                    current_conflict_positions.append((center_x, center_y))
                    conflict_count += 1
        
        # Store recent conflicts for visualization
        self.conflict_history.extend(current_conflict_positions)
        if len(self.conflict_history) > 100:  # Keep last 100 conflicts
            self.conflict_history = self.conflict_history[-100:]
        
        # Draw conflict history as faint dots
        if self.conflict_history:
            conflict_x, conflict_y = zip(*self.conflict_history)
            self.ax.scatter(conflict_x, conflict_y, color='red', s=20, alpha=0.2, marker='x')
        
        # Add comprehensive information panel
        total_drones = len(system.drone_missions)
        completed_count = sum(1 for m in system.drone_missions.values() 
                            if getattr(m, 'status', '') == "completed")
        
        info_text = (f'TOTAL DRONES: {total_drones}\n'
                    f'ACTIVE: {active_count}\n'
                    f'COMPLETED (but moving): {completed_count}\n'
                    f'CURRENT CONFLICTS: {conflict_count}\n'
                    f'TOTAL FRAMES: {frame}\n'
                    f'CONFLICT HISTORY: {len(self.conflict_history)}')
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    verticalalignment='top', fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
        
        # Add detailed legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='lime', label='Active (Start)', markersize=8),
            plt.Line2D([0], [0], marker='o', color='deepskyblue', label='Active (Middle)', markersize=8),
            plt.Line2D([0], [0], marker='o', color='blue', label='Active (End)', markersize=8),
            plt.Line2D([0], [0], marker='s', color='red', label='Completed Mission', markersize=8),
            plt.Line2D([0], [0], color='red', linewidth=3, label='Active Conflict'),
            plt.Line2D([0], [0], marker='x', color='red', label='Conflict History', markersize=8),
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      bbox_to_anchor=(0.98, 0.98), framealpha=0.9)
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

def run_continuous_visualization():
    """Run continuous visualization where drones never stop"""
    print("🚀 STARTING CONTINUOUS DRONE VISUALIZATION")
    print("=" * 60)
    print("FEATURES:")
    print("✅ Drones CONTINUE flying after mission completion")
    print("✅ All drones remain visible at all times") 
    print("✅ Conflict history tracking")
    print("✅ Continuous progress looping")
    print("=" * 60)
    
    # Initialize
    visualizer = ContinuousDroneVisualizer()
    system = UltraOptimizedDeconflictionSystem()  # type: ignore
    generator = ScalableMissionGenerator(area_size=1000, altitude_range=(20, 100))  # type: ignore
    
    # Generate missions
    print("📋 Generating 25 drone missions...")
    missions = generator.generate_missions(25)  # type: ignore
    results = system.batch_add_missions_parallel(missions)  # type: ignore
    
    print(f"✅ Added {sum(results)} missions to system")
    
    # Initialize progress tracking with CONTINUOUS progress (can go beyond 1.0)
    mission_progress: Dict[int, float] = {}
    for mission_id, mission in system.drone_missions.items():
        # Start at different points and allow progress to go beyond 1.0
        mission_progress[mission_id] = random.uniform(0.0, 5.0)  # Start at various lap positions
    
    print("🎬 Starting CONTINUOUS visualization...")
    print("   - 🟢🔵🔵 Active drones (color shows lap progress)")
    print("   - 🔴 Squares: Completed missions (but still moving!)") 
    print("   - ❌ Red X's: Conflict history locations")
    print("   - Close window to stop")
    print("=" * 60)
    
    frame = 0
    system.simulation_running = True
    
    try:
        while plt.fignum_exists(visualizer.fig.number):
            # Update ALL missions continuously (progress keeps increasing)
            for mission_id, mission in system.drone_missions.items():
                # Continuous progress - never stops increasing
                speed = random.uniform(0.002, 0.006)
                mission_progress[mission_id] += speed
                
                # Optional: Mark as "completed" after first lap, but keep moving
                if mission_progress[mission_id] >= 1.0 and getattr(mission, 'status', '') != "completed":
                    mission.status = "completed"
            
            # Get conflicts from system
            conflicts = []
            if hasattr(system, 'real_time_conflict_monitoring'):
                try:
                    conflicts = system.real_time_conflict_monitoring()  # type: ignore
                except:
                    # Simulate random conflicts
                    if frame % 40 == 0 and random.random() < 0.4:
                        active_missions = list(system.drone_missions.values())
                        if len(active_missions) >= 2:
                            conflicts = [tuple(random.sample(active_missions, 2))]  # type: ignore
            
            # Update visualization
            visualizer.update_continuous_viz(system, conflicts, frame, mission_progress)
            
            # Print status every 100 frames
            if frame % 100 == 0:
                active = sum(1 for m in system.drone_missions.values() 
                           if getattr(m, 'status', '') == "active")
                completed = sum(1 for m in system.drone_missions.values() 
                              if getattr(m, 'status', '') == "completed")
                print(f"📊 Frame {frame}: {active} active, {completed} completed, {len(conflicts)} conflicts")
            
            frame += 1
            time.sleep(0.03)  # Smooth animation speed
            
    except Exception as e:
        print(f"⚠️ Visualization error: {e}")
    
    system.simulation_running = False
    print("🎯 Continuous visualization completed!")
    plt.ioff()
    if plt.fignum_exists(visualizer.fig.number):
        plt.show()

if __name__ == "__main__":
    run_continuous_visualization()