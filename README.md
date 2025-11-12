# Drone Mission Conflict Detection System — Large-Scale

A toolkit for generating, detecting, resolving, and visualizing conflicts among *large numbers* of simulated drone missions.  
This repository focuses on scale — optimized detection algorithms and visualizers for both small sets (25) and large sets (1,000+ missions).

---

## Table of contents

- [About](#about)  
- [Key features](#key-features)  
- [Repository layout](#repository-layout)  
- [Requirements & installation](#requirements--installation)  
- [Quick start](#quick-start)  
- [Typical workflows & usage examples](#typical-workflows--usage-examples)  
- [Scripts & modules (what each does)](#scripts--modules-what-each-does)  
- [Configuration & file formats](#configuration--file-formats)  
- [Example output & performance notes](#example-output--performance-notes)  
- [Troubleshooting](#troubleshooting)  
- [Contributing](#contributing)  

---

## About

This project provides:

- Mission generation (large synthetic datasets)
- Multiple conflict-detection algorithms optimized for scale
- A final validation / benchmark runner that wires generation + detection for end-to-end tests
- Visualization utilities for small (25) and large (1000+) mission sets

Primary design goal: reliably detect and (optionally) resolve conflicts for *n* concurrent drone missions while keeping runtime and memory practical for large *n*.

---

## Key features

- Fast mission generator to produce thousands of time-tagged missions for stress testing  
- Optimized and ultra-optimized deconfliction implementations (spatial indexing, temporal windowing, multi-stage filtering)  
- `final_validation_test_optimized.py` — the main usage/benchmark script that ties everything together  
- Visualizers:
  - `conflict_visualizer.py` — 4D visualization for ~25 missions (for detailed inspection)
  - `scaled_1000_viz.py` — visualization tools tuned for large sets (1000+ missions)

---

## Repository layout

```
.
├── final_validation_test_optimized.py    # Main runner: generate -> detect -> validate/benchmark
├── mission_generator.py                  # Generate n simulated missions; uses optimized deconfliction
├── optimized_deconfliction.py            # Optimized deconfliction helpers used by generator / tests
├── ultra_optimized_deconfliction.py      # Independent ultra-optimized detection implementation
├── conflict_visualizer.py                # 4D visualizer for small sets (25 missions)
├── scaled_1000_viz.py                    # Visualization and logging tuned for 1000+ missions
├── README.md
```

---

## Requirements & installation

```bash
# create + activate venv (macOS / Linux)
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# install dependencies
pip install --upgrade pip
pip install numpy pandas shapely matplotlib pyproj tqdm
```

## Quick start

1. Run the final validation / benchmark runner:
```bash
python final_validation_test_optimized.py
```

2. Visualize results:
- For 25 missions:
```bash
python conflict_visualizer.py
```
- For 1000 missions:
```bash
python scaled_1000_viz.py
```

---

## Typical workflows & usage examples

### A. End-to-end benchmark (generate → detect → validate)
```bash
python final_validation_test_optimized.py
```

### B. Run ultra-optimized version directly
```bash
python ultra_optimized_deconfliction.py 
```

---

## Scripts & modules (what each does)

| Script | Description |
|--------|--------------|
| **mission_generator.py** | Generates synthetic missions with time, altitude, and path data; integrates conflict logic during generation. |
| **optimized_deconfliction.py** | Provides efficient pairwise conflict detection utilities (used internally). |
| **ultra_optimized_deconfliction.py** | Independent ultra-fast version using vectorization, indexing, and reduced complexity loops. |
| **final_validation_test_optimized.py** | Main entry point combining mission generation, detection, resolution, and throughput benchmarking. |
| **conflict_visualizer.py** | 4D (spatial + temporal) visualization for smaller mission sets (e.g., 25). |
| **scaled_1000_viz.py** | Large-scale real-time visualizer for 1000+ active missions with frame updates and statistics display. |

---

## Configuration & file formats

Typical mission CSV structure:
```
mission_id, waypoint_id, latitude, longitude, altitude, timestamp
```

---

## Example output & performance notes

Sample output from the terminal:

```
Addition time: 0.87 seconds
Throughput: 2299.1 missions/second
Conflicts prevented: 3

Starting real-time simulation with 1997 active missions...
Frame 50: 1997 active, 78 conflicts, frame: 44.2ms
Frame 100: 1997 active, 108 conflicts, frame: 40.9ms
...
```

Performance optimizations include:
- Spatial filtering via bounding boxes
- Time-window pruning
- Vectorized geometry computations
- Adaptive visualization frame skipping for high throughput

---

## Troubleshooting

- **Visualization not starting:** Check matplotlib / GUI backend installation.  
- **Slow performance:** Reduce mission count or disable live plotting.  
- **Conflicts missing:** Verify spatial and temporal thresholds in config.

---

## Contributing

Contributions are welcome!  
1. Fork the repo  
2. Create a feature branch (`feat/new-optimization`)  
3. Add your code and tests  

---
