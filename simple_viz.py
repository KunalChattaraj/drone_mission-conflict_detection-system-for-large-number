# simple_viz.py
import matplotlib.pyplot as plt
from ultra_optimized_deconfliction import UltraOptimizedDeconflictionSystem
from mission_generator import ScalableMissionGenerator
import time

def simple_visualization():
    print("🚀 Simple Mission Visualization")
    
    # Generate missions
    system = UltraOptimizedDeconflictionSystem()
    generator = ScalableMissionGenerator(area_size=1000, altitude_range=(20, 100))
    missions = generator.generate_missions(20)
    system.batch_add_missions_parallel(missions)
    
    # Setup plot
    plt.figure(figsize=(12, 6))
    plt.ion()
    
    for frame in range(100):
        plt.clf()
        
        # Plot all missions
        for mission_id, mission in system.drone_missions.items():
            if hasattr(mission, 'waypoints') and mission.waypoints:
                try:
                    x_vals = [wp[0] if isinstance(wp, (list, tuple)) else wp.x for wp in mission.waypoints]
                    y_vals = [wp[1] if isinstance(wp, (list, tuple)) else wp.y for wp in mission.waypoints]
                    plt.plot(x_vals, y_vals, 'o-', alpha=0.7, label=f'Mission {mission_id}')
                except:
                    continue
        
        plt.title(f'Drone Missions - Frame {frame}')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.draw()
        plt.pause(0.1)
        
        # Update simulation
        if hasattr(system, 'update_drone_positions_fast'):
            system.update_drone_positions_fast()
    
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    simple_visualization()