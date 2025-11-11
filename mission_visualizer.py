# mission_visualizer.py
"""
Standalone Mission Visualization GUI
Clean version without formatting errors
"""

import matplotlib.pyplot as plt
import numpy as np
import threading
from flask import Flask, jsonify
import time
from ultra_optimized_deconfliction import UltraOptimizedDeconflictionSystem
from mission_generator import ScalableMissionGenerator

class SimpleMissionVisualizer:
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        self.fig.suptitle('Drone Mission Visualization', fontsize=14, fontweight='bold')
        self.setup_plots()
        
    def setup_plots(self):
        """Initialize plots"""
        self.ax1.set_title('Mission Paths')
        self.ax1.set_xlabel('X Coordinate')
        self.ax1.set_ylabel('Y Coordinate')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_title('Mission Status')
        self.ax2.set_xlabel('X Coordinate')
        self.ax2.set_ylabel('Y Coordinate')
        self.ax2.grid(True, alpha=0.3)
        
        plt.ion()
        plt.show(block=False)
    
    def safe_extract_coordinates(self, waypoints):
        """Safely extract coordinates from waypoints"""
        if not waypoints:
            return [], []
        
        try:
            # Try different waypoint formats
            if hasattr(waypoints[0], 'x') and hasattr(waypoints[0], 'y'):
                x_vals = [wp.x for wp in waypoints]
                y_vals = [wp.y for wp in waypoints]
            elif hasattr(waypoints[0], 'lat') and hasattr(waypoints[0], 'lng'):
                x_vals = [wp.lat for wp in waypoints]
                y_vals = [wp.lng for wp in waypoints]
            elif isinstance(waypoints[0], (list, tuple)) and len(waypoints[0]) >= 2:
                x_vals = [wp[0] for wp in waypoints]
                y_vals = [wp[1] for wp in waypoints]
            else:
                return [], []
        except Exception:
            return [], []
        
        return x_vals, y_vals
    
    def plot_missions(self, system, frame):
        """Plot all missions"""
        self.ax1.clear()
        self.ax1.set_title(f'Mission Paths - Frame {frame}')
        self.ax1.set_xlabel('X Coordinate')
        self.ax1.set_ylabel('Y Coordinate')
        self.ax1.grid(True, alpha=0.3)
        
        mission_count = 0
        for mission_id, mission in system.drone_missions.items():
            if hasattr(mission, 'waypoints') and mission.waypoints:
                x_vals, y_vals = self.safe_extract_coordinates(mission.waypoints)
                if x_vals and y_vals:
                    # Simple color based on mission ID
                    color = plt.cm.Set3(mission_id % 12)
                    
                    # Plot path
                    self.ax1.plot(x_vals, y_vals, color=color, linewidth=2, alpha=0.7)
                    
                    # Plot waypoints
                    self.ax1.scatter(x_vals, y_vals, color=color, s=30, alpha=0.6)
                    
                    mission_count += 1
        
        self.ax1.text(0.02, 0.98, f'Missions: {mission_count}', 
                     transform=self.ax1.transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def plot_status(self, system, conflicts, frame):
        """Plot mission status"""
        self.ax2.clear()
        self.ax2.set_title(f'Mission Status - Frame {frame}')
        self.ax2.set_xlabel('X Coordinate')
        self.ax2.set_ylabel('Y Coordinate')
        self.ax2.grid(True, alpha=0.3)
        
        active_count = 0
        completed_count = 0
        conflict_count = 0
        
        # Plot mission centers
        for mission_id, mission in system.drone_missions.items():
            if hasattr(mission, 'waypoints') and mission.waypoints:
                x_vals, y_vals = self.safe_extract_coordinates(mission.waypoints)
                if x_vals and y_vals:
                    x, y = x_vals[0], y_vals[0]  # Use first waypoint
                    
                    status = getattr(mission, 'status', 'unknown')
                    if status == "active":
                        color = 'blue'
                        marker = 'o'
                        active_count += 1
                    elif status == "completed":
                        color = 'green'
                        marker = 's'
                        completed_count += 1
                    else:
                        color = 'gray'
                        marker = '^'
                    
                    self.ax2.plot(x, y, marker, color=color, markersize=8, alpha=0.8)
        
        # Plot conflicts
        for conflict in conflicts:
            if len(conflict) >= 2:
                mission1, mission2 = conflict[0], conflict[1]
                if (hasattr(mission1, 'waypoints') and mission1.waypoints and
                    hasattr(mission2, 'waypoints') and mission2.waypoints):
                    
                    x1, y1 = self.safe_extract_coordinates(mission1.waypoints)
                    x2, y2 = self.safe_extract_coordinates(mission2.waypoints)
                    
                    if x1 and y1 and x2 and y2:
                        # Draw line between first waypoints
                        self.ax2.plot([x1[0], x2[0]], [y1[0], y2[0]], 
                                    'r-', linewidth=2, alpha=0.6)
                        conflict_count += 1
        
        status_text = f'Active: {active_count}\nCompleted: {completed_count}\nConflicts: {conflict_count}'
        self.ax2.text(0.02, 0.98, status_text, 
                     transform=self.ax2.transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def update(self, system, conflicts, frame):
        """Update visualization"""
        try:
            self.plot_missions(system, frame)
            self.plot_status(system, conflicts, frame)
            plt.tight_layout()
            plt.draw()
            plt.pause(0.001)
        except Exception as e:
            # Don't print the error to avoid clutter
            pass

class SimpleWebDashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.data = {
            'missions': [],
            'conflicts': [],
            'statistics': {}
        }
        
        @self.app.route('/')
        def dashboard():
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Drone Mission Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { text-align: center; background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }
                    .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }
                    .stat-card { background: white; padding: 15px; border-radius: 8px; text-align: center; }
                    .stat-number { font-size: 24px; font-weight: bold; color: #2c3e50; }
                    .mission-list { background: white; padding: 15px; border-radius: 8px; max-height: 300px; overflow-y: auto; }
                    .mission-item { padding: 8px; margin: 5px 0; background: #ecf0f1; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚁 Drone Mission Dashboard</h1>
                        <p>Real-time Mission Monitoring</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div>Total Missions</div>
                            <div class="stat-number" id="totalMissions">0</div>
                        </div>
                        <div class="stat-card">
                            <div>Active Missions</div>
                            <div class="stat-number" id="activeMissions">0</div>
                        </div>
                        <div class="stat-card">
                            <div>Completed</div>
                            <div class="stat-number" id="completedMissions">0</div>
                        </div>
                        <div class="stat-card">
                            <div>Conflicts</div>
                            <div class="stat-number" id="conflictCount">0</div>
                        </div>
                    </div>
                    
                    <div class="mission-list" id="missionList">
                        Loading mission data...
                    </div>
                </div>
                
                <script>
                    function updateDashboard() {
                        fetch('/api/data')
                            .then(r => r.json())
                            .then(data => {
                                document.getElementById('totalMissions').textContent = data.statistics.total_missions || 0;
                                document.getElementById('activeMissions').textContent = data.statistics.active_missions || 0;
                                document.getElementById('completedMissions').textContent = data.statistics.completed_missions || 0;
                                document.getElementById('conflictCount').textContent = data.statistics.conflict_count || 0;
                                
                                const missions = data.missions.slice(0, 15).map(m => 
                                    `<div class="mission-item">Mission ${m.id}: ${m.status}</div>`
                                ).join('');
                                document.getElementById('missionList').innerHTML = missions;
                            })
                            .catch(e => console.error('Error:', e));
                    }
                    
                    setInterval(updateDashboard, 2000);
                    updateDashboard();
                </script>
            </body>
            </html>
            '''
        
        @self.app.route('/api/data')
        def api_data():
            return jsonify(self.data)
    
    def update_data(self, system, conflicts):
        """Update dashboard data"""
        active = sum(1 for m in system.drone_missions.values() if getattr(m, 'status', '') == "active")
        completed = sum(1 for m in system.drone_missions.values() if getattr(m, 'status', '') == "completed")
        total = len(system.drone_missions)
        
        self.data = {
            'missions': [
                {'id': mid, 'status': getattr(m, 'status', 'unknown')}
                for mid, m in list(system.drone_missions.items())[:20]
            ],
            'conflicts': [{'id': i} for i in range(len(conflicts))],
            'statistics': {
                'total_missions': total,
                'active_missions': active,
                'completed_missions': completed,
                'conflict_count': len(conflicts)
            }
        }
    
    def run(self, port=5001):
        """Run dashboard"""
        threading.Thread(target=lambda: self.app.run(
            debug=False, port=port, use_reloader=False, host='0.0.0.0'
        ), daemon=True).start()
        print(f"📊 Web Dashboard: http://localhost:{port}")

def run_clean_visualization():
    """Run clean visualization without errors"""
    print("🚀 Starting Clean Mission Visualization")
    print("=" * 40)
    
    # Initialize systems
    visualizer = SimpleMissionVisualizer()
    dashboard = SimpleWebDashboard()
    dashboard.run(port=5001)
    time.sleep(2)
    
    # Create mission data
    system = UltraOptimizedDeconflictionSystem()
    generator = ScalableMissionGenerator(area_size=1000, altitude_range=(20, 100))
    
    print("Generating missions...")
    missions = generator.generate_missions(30)  # Smaller set for clarity
    results = system.batch_add_missions_parallel(missions)
    
    # Activate missions
    for mission, success in zip(missions, results):
        if success:
            mission.status = "active"
    
    print(f"✅ Loaded {sum(results)} missions")
    print("🎨 Starting visualization...")
    print("   - Close matplotlib window to stop")
    
    # Simulation loop
    system.simulation_running = True
    
    try:
        for frame in range(500):  # Run for 500 frames
            # Update simulation
            if hasattr(system, 'current_sim_time'):
                system.current_sim_time += getattr(system, 'time_step', 0.1)
            if hasattr(system, 'update_drone_positions_fast'):
                system.update_drone_positions_fast()
            
            # Check conflicts occasionally
            conflicts = []
            if frame % 15 == 0 and hasattr(system, 'real_time_conflict_monitoring'):
                conflicts = system.real_time_conflict_monitoring()
            
            # Update visualization every 10 frames
            if frame % 10 == 0:
                visualizer.update(system, conflicts, frame)
                dashboard.update_data(system, conflicts)
            
            # Progress update
            if frame % 50 == 0:
                active = sum(1 for m in system.drone_missions.values() if getattr(m, 'status', '') == "active")
                completed = sum(1 for m in system.drone_missions.values() if getattr(m, 'status', '') == "completed")
                print(f"   Frame {frame}: {active} active, {completed} completed, {len(conflicts)} conflicts")
            
            time.sleep(0.02)  # Smooth animation
    
    except KeyboardInterrupt:
        print("\n🛑 Visualization stopped by user")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    system.simulation_running = False
    print("🎯 Visualization completed!")
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_clean_visualization()