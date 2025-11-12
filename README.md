# Drone Mission Conflict Detection System (GUI)

**Check a single *primary* mission against 1,000 simulated drone missions — with a simple GUI.**

This repository provides a lightweight simulator + conflict detector and a minimal GUI so you can:

- Load or define a single *primary* mission (the mission you care about).
- Generate 1,000 simulated missions (randomized start/end/waypoints, speeds, and schedules).
- Run a time‑synchronized conflict check between the primary mission and all simulated missions.
- Visualize missions and conflicts in a simple GUI (PyQt5) so you can inspect the primary mission, the colliding missions, and the conflict timestamps / distances.

---

> This README is written as a ready-to-drop `README.md` for the repository. It also contains a minimal example configuration and run instructions.

---

## What this repo contains

- `sim/` — mission generation utilities (primary + simulated missions).
- `detection/` — core conflict detection logic (time sampling + pairwise checks against primary mission).
- `gui/` — PyQt5 GUI to run the simulation, control parameters, and visualize results.
- `examples/primary_mission.json` — example primary mission file you can edit and load.
- `requirements.txt` — (recommended) package list.

---

## Quick features

- Generate exactly **1,000** simulated missions (configurable).
- Sample positions using a configurable `time_step` and check Euclidean distance at synchronized timestamps.
- Flag conflicts where distance &lt; `safety_distance` and show them in GUI with mission ID and time.
- Visualize 2D plan (top-down) with primary mission highlighted and conflicting missions colored.

---

## Prerequisites

- Python 3.8+
- Recommended: virtual environment (`venv` or `conda`).

Install dependencies:

```bash
pip install -r requirements.txt
# or, if you don't have the file:
pip install numpy PyQt5 matplotlib
```

> If you see `externally-managed-environment` errors, make sure you're inside a virtual environment or use `--user` for local installs.

---

## Example primary mission format

Save this as `examples/primary_mission.json` (or edit the provided one):

```json
{
  "mission_id": "primary-001",
  "start_time": 0,
  "end_time": 60,
  "waypoints": [
    [0, 0],
    [50, 0],
    [100, 50]
  ],
  "speed_m_s": 5
}
```

- `start_time` and `end_time` are in seconds.
- `waypoints` is a list of `[x, y]` positions in meters.
- `speed_m_s` is the nominal speed used to parameterize the path.

---

## How the detector works (short)

1. The primary mission path is parameterized over time using constant speed between waypoints.
2. Simulated missions are generated with randomized start times, speeds, and waypoints inside a configurable bounding box.
3. At each sampled timestamp (0..end in steps of `time_step`), the detector computes the primary mission position and the simulated mission position(s).
4. If the Euclidean distance between primary and any simulated mission is less than `safety_distance`, a conflict is recorded with mission-id, timestamp, and distance.

---

## Configuration options (GUI + code)

- `NUM_SIM_MISSIONS` (default `1000`) — number of simulated missions.
- `TIME_STEP` (default `0.5` seconds) — sampling frequency.
- `SAFETY_DISTANCE` (default `5.0` meters) — threshold to declare a conflict.
- `SIM_BOUNDING_BOX` — `[[xmin, ymin], [xmax, ymax]]` region where simulated missions are generated.

---

## Run the GUI (example)

1. Ensure `examples/primary_mission.json` exists.
2. Launch the GUI entry point. The exact filename may be `gui/main.py` or `main.py` at repo root. Example:

```bash
python gui/main.py --primary examples/primary_mission.json
```

3. GUI controls you will see:
- **Load Primary** — select a primary mission JSON file.
- **Generate 1000 Missions** — creates and displays simulated missions.
- **Start Detection** — runs the synchronized detection loop and highlights conflicts.
- **Pause / Stop** — control execution.
- **Settings** — adjust `time_step`, `safety_distance`, and `num_missions` (though the default will generate 1000).

The GUI draws a top-down 2D view. The primary mission is drawn with a thick blue line; any collided mission is drawn red; non-colliding missions are grey.

---

## Minimal implementation notes (helper code snippets)

The repo includes working files. If you need a small copy-paste implementation for the core detection loop (for reference), here is a compact Python snippet showing the core logic (not the GUI):

```python
# core_detector.py  (compact)
import numpy as np

def interp_path(waypoints, total_time, speed):
    # Build cumulative distances and times across segments, then create a function
    pts = np.array(waypoints)
    seg_vecs = pts[1:] - pts[:-1]
    seg_lens = np.linalg.norm(seg_vecs, axis=1)
    total_len = seg_lens.sum()
    if total_len == 0:
        return lambda t: pts[0]
    # param t in [0, total_time]
    seg_times = seg_lens / speed
    cum_t = np.concatenate(([0], np.cumsum(seg_times)))

    def pos_at(t):
        t = np.clip(t, 0, cum_t[-1])
        idx = np.searchsorted(cum_t, t, side='right') - 1
        if idx >= len(seg_vecs):
            return pts[-1]
        local_t = (t - cum_t[idx]) / (seg_times[idx] if seg_times[idx]>0 else 1)
        return pts[idx] + seg_vecs[idx] * local_t

    return pos_at


def detect_conflicts(primary, sims, time_step=0.5, safety_dist=5.0):
    # primary: dict with waypoints, speed, start_time, end_time
    ppos = interp_path(primary['waypoints'], primary['end_time']-primary['start_time'], primary['speed_m_s'])
    conflicts = []
    times = np.arange(primary['start_time'], primary['end_time'] + 1e-9, time_step)
    for sim in sims:
        spos = interp_path(sim['waypoints'], sim['end_time']-sim['start_time'], sim['speed_m_s'])
        for t in times:
            # map t into each mission's local time if missions have offsets
            p = ppos(t - primary['start_time'])
            s = spos(t - sim['start_time'])
            d = np.linalg.norm(p - s)
            if d < safety_dist:
                conflicts.append({'sim_id': sim['mission_id'], 'time': t, 'distance': float(d)})
                break  # optionally record first conflict only
    return conflicts
```

This snippet gives you the core idea. The GUI code wraps around this: generating `sims` (1,000 missions), calling `detect_conflicts`, and plotting results.

---

## Performance and scaling tips

- Generating 1,000 missions and sampling with small `time_step` can be CPU-heavy. Use `numpy` vectorization and precompute arrays when possible.
- To reduce pairwise checks: only test simulated missions whose bounding boxes overlap the primary mission bounding box extended by `safety_distance`.
- Consider `scipy.spatial.cKDTree` for fast nearest-neighbor checks on each timestamp.
- For GUI responsiveness, run the detection in a background thread and emit signals to the GUI to update (PyQt `QThread` or `concurrent.futures`).

---

## Troubleshooting

- **No GUI / ImportError**: Ensure PyQt5 is installed and you are running the script from the repo root (or have PYTHONPATH set).
- **Very slow**: Increase `time_step` or reduce the number of simulated missions while testing.
- **Conflicts not found**: Check `safety_distance`, mission time windows, and that missions overlap in time.

---

## Tests and examples
- `examples/demo_run.sh` — a small headless script to run detection against 1000 sims and output `conflicts.json`.
- `tests/test_detector.py` — unit tests for the detection function.

---

## Contributing
Feel free to open issues or PRs for:
- Better visualization and mission controls (hover, highlight, jump-to-time).
- More realistic mission kinematics and altitude handling (this repo uses 2D planar motion as default).
- Exporting conflict reports (CSV/JSON) and mission replays.

---

## License
Add a `LICENSE` file (MIT recommended for open-source small projects).

---

If you'd like, I can also:

- Generate a ready-to-use `gui/main.py` (PyQt5) that implements the exact GUI described above, or
- Produce `requirements.txt` from the repo's imports, or
- Create the `examples/demo_run.sh` script that runs the headless simulation for 1000 missions and produces a `conflicts.json` output.

Tell me which one you want next and I will add it in the repo.

