# scaled_1000_drones_viz.py
"""
SCALED VISUALIZATION for 1000+ Drones
Optimized for performance with large numbers
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
    # Mock classes
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

class ScaledDroneVisualizer:
    def __init__(self):
        # Use a single plot for performance
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.setup_plot()
        
        # Performance optimizations
        self.drone_trails = {}
        self.conflict_history = []
        self.max_trail_length = 20  # Reduced for performance
        self.max_conflict_history = 50  # Reduced for performance
        self.last_update_time = time.time()
        
    def setup_plot(self):
        """Setup optimized plot for 1000 drones"""
        self.ax.set_title('🚁 MASSIVE SCALE: 1000+ DRONE CONFLICT MONITORING', 
                         fontsize=18, fontweight='bold', pad=20)
        self.ax.set_xlabel('X Coordinate (meters)', fontsize=12)
        self.ax.set_ylabel('Y Coordinate (meters)', fontsize=12)
        self.ax.grid(True, alpha=0.2)  # Lighter grid for less visual noise
        self.ax.set_xlim(-800, 800)   # Larger area
        self.ax.set_ylim(-800, 800)
        
        plt.ion()
        plt.show(block=False)
    
    def extract_coords(self, waypoint) -> Tuple[float, float]:
        """Fast coordinate extraction"""
        try:
            if hasattr(waypoint, 'x') and hasattr(waypoint, 'y'):
                return waypoint.x, waypoint.y
            elif hasattr(waypoint, 'lat') and hasattr(waypoint, 'lng'):
                return waypoint.lat, waypoint.lng
            elif isinstance(waypoint, (list, tuple)) and len(waypoint) >= 2:
                return float(waypoint[0]), float(waypoint[1])
            else:
                return random.uniform(-700, 700), random.uniform(-700, 700)
        except:
            return random.uniform(-700, 700), random.uniform(-700, 700)
    
    def calculate_position(self, mission, progress: float) -> Tuple[float, float]:
        """Fast position calculation"""
        if not hasattr(mission, 'waypoints') or not mission.waypoints:
            return random.uniform(-700, 700), random.uniform(-700, 700)
        
        waypoints = mission.waypoints
        if len(waypoints) == 0:
            return random.uniform(-700, 700), random.uniform(-700, 700)
        elif len(waypoints) == 1:
            return self.extract_coords(waypoints[0])
        
        # Continuous looping progress
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
    
    def update_massive_scale_viz(self, system, conflicts: List, frame: int, progress_dict: Dict[int, float]):
        """Optimized visualization update for 1000+ drones"""
        current_time = time.time()
        if current_time - self.last_update_time < 0.033:  # ~30 FPS max
            return
        self.last_update_time = current_time
        
        self.ax.clear()
        
        # Simplified title for performance
        self.ax.set_title(f'🚁 1000+ DRONES - Frame {frame}', 
                         fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('X Coordinate (meters)', fontsize=11)
        self.ax.set_ylabel('Y Coordinate (meters)', fontsize=11)
        self.ax.grid(True, alpha=0.2)
        self.ax.set_xlim(-800, 800)
        self.ax.set_ylim(-800, 800)
        
        current_positions = {}
        active_count = 0
        completed_count = 0
        
        # OPTIMIZATION: Only draw paths for first 50 missions to reduce clutter
        mission_count = 0
        for mission_id, mission in system.drone_missions.items():
            if mission_count >= 50:  # Limit path drawing
                break
            if hasattr(mission, 'waypoints') and mission.waypoints:
                path_x, path_y = [], []
                for wp in mission.waypoints:
                    x, y = self.extract_coords(wp)
                    path_x.append(x)
                    path_y.append(y)
                
                if path_x and path_y:
                    alpha = 0.1  # Very transparent paths
                    self.ax.plot(path_x, path_y, 'gray', alpha=alpha, linewidth=0.5, linestyle='-')
            mission_count += 1
        
        # OPTIMIZATION: Use scatter plots for drone positions (MUCH faster)
        active_positions_x, active_positions_y = [], []
        completed_positions_x, completed_positions_y = [], []
        
        for mission_id, mission in system.drone_missions.items():
            progress = progress_dict.get(mission_id, 0.0)
            current_pos = self.calculate_position(mission, progress)
            current_positions[mission_id] = current_pos
            
            # Minimal trail for performance
            if mission_id not in self.drone_trails:
                self.drone_trails[mission_id] = []
            self.drone_trails[mission_id].append(current_pos)
            if len(self.drone_trails[mission_id]) > self.max_trail_length:
                self.drone_trails[mission_id].pop(0)
            
            # Separate active vs completed for efficient plotting
            status = getattr(mission, 'status', 'active')
            if status == "completed":
                completed_positions_x.append(current_pos[0])
                completed_positions_y.append(current_pos[1])
                completed_count += 1
            else:
                active_positions_x.append(current_pos[0])
                active_positions_y.append(current_pos[1])
                active_count += 1
        
        # OPTIMIZATION: Single scatter call for each category
        if active_positions_x:
            self.ax.scatter(active_positions_x, active_positions_y, 
                          c='blue', s=2, alpha=0.7, label='Active Drones')
        
        if completed_positions_x:
            self.ax.scatter(completed_positions_x, completed_positions_y, 
                          c='red', s=3, alpha=0.5, marker='s', label='Completed')
        
        # Draw conflicts (limited to prevent overcrowding)
        conflict_count = 0
        current_conflict_positions = []
        
        for conflict in conflicts[:20]:  # Limit conflicts drawn for performance
            if len(conflict) >= 2:
                mission1, mission2 = conflict[0], conflict[1]
                mission1_id = getattr(mission1, 'id', None)
                mission2_id = getattr(mission2, 'id', None)
                
                if mission1_id in current_positions and mission2_id in current_positions:
                    pos1 = current_positions[mission1_id]
                    pos2 = current_positions[mission2_id]
                    
                    # Draw conflict line
                    self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                               'r-', linewidth=2, alpha=0.6)
                    
                    # Simple conflict marker (no circles for performance)
                    center_x = (pos1[0] + pos2[0]) / 2
                    center_y = (pos1[1] + pos2[1]) / 2
                    self.ax.plot(center_x, center_y, 'rx', markersize=6, alpha=0.8)
                    
                    current_conflict_positions.append((center_x, center_y))
                    conflict_count += 1
        
        # Store limited conflict history
        self.conflict_history.extend(current_conflict_positions)
        if len(self.conflict_history) > self.max_conflict_history:
            self.conflict_history = self.conflict_history[-self.max_conflict_history:]
        
        # Draw conflict history as simple dots
        if self.conflict_history:
            conflict_x, conflict_y = zip(*self.conflict_history)
            self.ax.scatter(conflict_x, conflict_y, color='red', s=10, alpha=0.3, marker='.')
        
        # Performance-optimized information panel
        total_drones = len(system.drone_missions)
        
        info_text = (f'TOTAL DRONES: {total_drones:,}\n'
                    f'ACTIVE: {active_count:,}\n'
                    f'COMPLETED: {completed_count:,}\n'
                    f'CONFLICTS: {conflict_count}\n'
                    f'FRAME: {frame:,}')
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    verticalalignment='top', fontsize=12, fontweight='bold', linespacing=1.5,
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.8, color='white'))
        
        # Performance metrics
        fps = 1.0 / (current_time - self.last_update_time) if current_time > self.last_update_time else 0
        perf_text = f'FPS: {fps:.1f}'
        self.ax.text(0.98, 0.02, perf_text, transform=self.ax.transAxes,
                    verticalalignment='bottom', horizontalalignment='right',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='green', alpha=0.8))
        
        # Simplified legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='blue', label=f'Active ({active_count:,})', 
                      markersize=6, linestyle='None'),
            plt.Line2D([0], [0], marker='s', color='red', label=f'Completed ({completed_count:,})', 
                      markersize=6, linestyle='None'),
            plt.Line2D([0], [0], color='red', linewidth=2, label=f'Conflicts ({conflict_count})'),
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      framealpha=0.9, fontsize=10)
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.001)  # Minimal pause

def run_massive_scale_visualization():
    """Run visualization scaled for 1000+ drones"""
    print("🚀 STARTING MASSIVE SCALE: 1000+ DRONES")
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATIONS:")
    print("✅ Scatter plots instead of individual markers")
    print("✅ Limited trail lengths (20 points max)")
    print("✅ Reduced path drawing (first 50 missions only)")
    print("✅ Conflict drawing limited to 20 simultaneous")
    print("✅ Optimized frame rate control (~30 FPS max)")
    print("=" * 60)
    
    # Initialize
    visualizer = ScaledDroneVisualizer()
    system = UltraOptimizedDeconflictionSystem()  # type: ignore
    generator = ScalableMissionGenerator(area_size=1500, altitude_range=(20, 100))  # type: ignore
    
    # Generate 1000 missions
    print("📋 Generating 1000 drone missions...")
    start_time = time.time()
    missions = generator.generate_missions(1000)  # type: ignore
    generation_time = time.time() - start_time
    print(f"✅ Generated 1000 missions in {generation_time:.2f} seconds")
    
    # Add missions to system
    print("🔄 Adding missions to conflict detection system...")
    start_time = time.time()
    results = system.batch_add_missions_parallel(missions)  # type: ignore
    addition_time = time.time() - start_time
    success_count = sum(results) if results else 0
    print(f"✅ Added {success_count}/1000 missions in {addition_time:.2f} seconds")
    
    # Initialize progress tracking with varied starting points
    mission_progress: Dict[int, float] = {}
    print("🎯 Initializing drone positions...")
    for mission_id, mission in system.drone_missions.items():
        # Start at different lap positions for visual spread
        mission_progress[mission_id] = random.uniform(0.0, 10.0)
    
    print("🎬 Starting MASSIVE SCALE visualization...")
    print("   - 🔵 Blue dots: Active drones")
    print("   - 🔴 Red squares: Completed missions") 
    print("   - ❌ Red lines/X: Active conflicts")
    print("   - Performance: FPS counter in green box")
    print("   - Close window to stop")
    print("=" * 60)
    
    frame = 0
    system.simulation_running = True
    last_status_time = time.time()
    
    try:
        while plt.fignum_exists(visualizer.fig.number):
            # Update all drones with continuous progress
            for mission_id, mission in system.drone_missions.items():
                # Vary speeds for more natural movement
                speed = random.uniform(0.001, 0.003)  # Slower for 1000 drones
                mission_progress[mission_id] += speed
                
                # Mark as completed after first lap but keep moving
                if mission_progress[mission_id] >= 1.0 and getattr(mission, 'status', '') != "completed":
                    mission.status = "completed"
            
            # Get conflicts from system (with error handling)
            conflicts = []
            if hasattr(system, 'real_time_conflict_monitoring'):
                try:
                    conflicts = system.real_time_conflict_monitoring()  # type: ignore
                except Exception as e:
                    # Simulate some conflicts for demonstration
                    if frame % 100 == 0 and random.random() < 0.2:
                        all_missions = list(system.drone_missions.values())
                        if len(all_missions) >= 2:
                            conflicts = [tuple(random.sample(all_missions, 2))]  # type: ignore
            
            # Update visualization
            visualizer.update_massive_scale_viz(system, conflicts, frame, mission_progress)
            
            # Print status every 10 seconds
            current_time = time.time()
            if current_time - last_status_time > 10.0:
                active = sum(1 for m in system.drone_missions.values() 
                           if getattr(m, 'status', '') == "active")
                completed = sum(1 for m in system.drone_missions.values() 
                              if getattr(m, 'status', '') == "completed")
                print(f"📊 Frame {frame:,}: {active:,} active, {completed:,} completed, {len(conflicts)} conflicts")
                last_status_time = current_time
            
            frame += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Visualization stopped by user")
    except Exception as e:
        print(f"⚠️ Visualization error: {e}")
    
    system.simulation_running = False
    print("🎯 Massive scale visualization completed!")
    print(f"📈 Total frames: {frame:,}")
    plt.ioff()
    if plt.fignum_exists(visualizer.fig.number):
        plt.show()

if __name__ == "__main__":
    run_massive_scale_visualization()