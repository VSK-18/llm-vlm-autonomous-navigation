# LLM-VLM Autonomous Navigation Readme File 

A ROS 2 Jazzy based autonomous mobile robot simulation and navigation project developed as a final-year engineering project.

The project focuses on building a complete autonomous navigation pipeline using LiDAR, RGB-D/depth sensing, localization, mapping, Nav2 and ROS 2 Control, with **LLM/VLM-based intelligent navigation planned as the next major development stage**.

---

## Project Overview

The overall objective is to develop an autonomous mobile robot capable of:

- Perceiving its environment using LiDAR and depth cameras
- Building and using maps
- Localizing itself within the environment
- Planning collision-free paths
- Navigating autonomously to target locations
- Understanding higher-level natural-language commands
- Using Vision-Language Models (VLMs) for scene understanding
- Using Large Language Models (LLMs) for task reasoning and navigation planning

The project is being developed in simulation first and is intended to support future deployment on real robotic hardware.

---

## Current Architecture

```text
                 ┌──────────────────────┐
                 │      LLM / VLM       │
                 │  High-Level Reasoning│
                 └──────────┬───────────┘
                            │
                       Navigation Goal
                            │
                            ▼
┌──────────────┐     ┌───────────────┐
│  RPLIDAR S2  │────►│               │
└──────────────┘     │               │
                     │  Perception   │
┌──────────────┐     │      +        │
│ RealSense    │────►│ Localization  │
│ RGB-D Camera │     │      +        │
└──────────────┘     │    Mapping    │
                     │               │
┌──────────────┐     │               │
│     IMU      │────►│               │
└──────────────┘     └───────┬───────┘
                             │
                             ▼
                        ┌─────────┐
                        │  Nav2   │
                        └────┬────┘
                             │
                             ▼
                      ┌────────────┐
                      │ ROS 2      │
                      │ Control    │
                      └─────┬──────┘
                            │
                            ▼
                    Differential Drive
                         Robot
````

---

# Technology Stack

| Component              | Technology                |
| ---------------------- | ------------------------- |
| Operating System       | Ubuntu 24.04              |
| Middleware             | ROS 2 Jazzy               |
| Simulation             | Gazebo Sim 8.11.0         |
| Navigation             | Nav2                      |
| SLAM                   | SLAM Toolbox              |
| Localization           | AMCL / robot_localization |
| Robot Control          | ROS 2 Control             |
| LiDAR                  | Slamtec RPLIDAR S2        |
| Depth Camera           | Intel RealSense           |
| Visualization          | RViz2 / RQt               |
| Point Cloud Processing | PCL                       |
| Image Processing       | OpenCV / image_proc       |
| Future AI              | LLM + VLM                 |

---

# Robot Simulation

The current Gazebo simulation contains a custom autonomous mobile robot with:

* Custom chassis
* Differential-drive wheels
* Payload platform
* Depth-camera housing
* Camera sensors
* 2D LiDAR
* IMU
* ROS 2 Control interface

The simulation also includes a warehouse-style environment for testing autonomous navigation.

---

# Sensors

## 2D LiDAR

The simulation provides:

```text
/scan
```

The simulated LiDAR has been verified to publish at approximately **10 Hz**.

Example:

```bash
ros2 topic hz /scan
```

The LiDAR configuration supports a range of approximately:

```text
0.30 m → 25 m
```

The intended physical LiDAR for deployment is:

**Slamtec RPLIDAR S2**

---

## RGB-D / Depth Camera

The simulated depth camera publishes:

```text
/depth_camera/image_raw
/depth_camera/depth
/depth_camera/camera_info
```

The depth image configuration is:

```text
Resolution: 640 × 480
Encoding:   32FC1
```

The depth stream has been verified at approximately **20 Hz**.

The simulation produced valid depth measurements in the approximate range:

```text
0.25 m → 6.67 m
```

The intended physical camera is an:

**Intel RealSense depth camera**

---

## IMU

The simulated IMU publishes:

```text
/imu/data_raw
```

This data will be used for localization and sensor fusion.

---

# Verified ROS 2 Topics

Current sensor and state topics include:

```text
/depth_camera/camera_info
/depth_camera/depth
/depth_camera/image_raw

/imu/data_raw

/scan

/gazebo/ground_truth/odom

/stereo/left/camera_info
/stereo/left/image_raw

/stereo/right/camera_info
/stereo/right/image_raw
```

---

# ROS 2 Packages

The workspace currently contains the following project packages:

```text
rlai_bringup
rlai_camera_processing
rlai_control
rlai_description
rlai_gazebo
rlai_isaac
rlai_lidar_processing
rlai_localization
rlai_mapping
rlai_meshes
rlai_navigation
rlai_teleop
rlai_utils
```

### Package Responsibilities

### `rlai_description`

Contains the robot URDF/Xacro description and sensor configuration.

### `rlai_meshes`

Contains the custom robot visual meshes:

```text
chassis.stl
wheel.stl
wheel_cap.stl
depth_camera_housing.stl
depth_camera_lens.stl
payload_platform.stl
logo_ai.stl
logo_robolabs.stl
```

### `rlai_gazebo`

Responsible for:

* Gazebo world
* Robot spawning
* Gazebo configuration
* Simulation plugins
* Sensor simulation

### `rlai_control`

Responsible for:

* ROS 2 Control
* Differential-drive controller
* Joint state broadcaster
* Velocity control

### `rlai_lidar_processing`

Handles LiDAR processing.

### `rlai_camera_processing`

Handles camera and depth processing.

### `rlai_localization`

Contains:

* EKF configuration
* AMCL configuration
* IMU filtering
* Localization launch files

### `rlai_mapping`

Contains:

* SLAM Toolbox configuration
* Map server
* Mapping launch files
* RViz configuration

### `rlai_navigation`

Contains:

* Nav2 configuration
* Navigation launch files
* Navigation behavior trees

### `rlai_teleop`

Provides manual robot control and emergency-stop functionality.

### `rlai_bringup`

Provides system-level launch files.

---

# Launch Files

Important launch files currently available:

```text
rlai_bringup
└── simulation.launch.py

rlai_gazebo
├── gazebo.launch.py
└── spawn_robot.launch.py

rlai_control
└── control.launch.py

rlai_localization
├── localization.launch.py
└── localization_amcl.launch.py

rlai_mapping
├── mapping.launch.py
└── map_server.launch.py

rlai_navigation
└── navigation.launch.py

rlai_camera_processing
└── camera_processing.launch.py

rlai_lidar_processing
└── lidar_processing.launch.py

rlai_teleop
└── teleop.launch.py
```

---

# Installation

## Requirements

The project has been tested with:

```text
Ubuntu 24.04
ROS 2 Jazzy
Gazebo Sim 8.11.0
```

Install the required ROS 2 dependencies before building the workspace.

---

# Building the Project

Navigate to the workspace:

```bash
cd ~/final_year_project_ws
```

Source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Build:

```bash
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

Verify the project packages:

```bash
ros2 pkg list | grep rlai
```

---

# Running the Simulation

Source both ROS 2 and the project workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/final_year_project_ws/install/setup.bash
```

Launch Gazebo:

```bash
ros2 launch rlai_gazebo gazebo.launch.py
```

Or launch the complete simulation:

```bash
ros2 launch rlai_bringup simulation.launch.py
```

The Gazebo environment should load the warehouse world and spawn the custom robot.

---

# Sensor Verification

Check available sensor topics:

```bash
ros2 topic list | grep -E "scan|image|depth|camera|imu|odom"
```

Check LiDAR:

```bash
ros2 topic hz /scan
```

Check RGB camera:

```bash
ros2 topic hz /depth_camera/image_raw
```

Check depth:

```bash
ros2 topic hz /depth_camera/depth
```

Inspect depth data:

```bash
ros2 topic echo /depth_camera/depth --once
```

---

# Depth Visualization

A standalone depth visualization tool is included in:

```text
tools/depth_visualizer.py
```

Run:

```bash
source /opt/ros/jazzy/setup.bash

python3 ~/final_year_project_ws/tools/depth_visualizer.py
```

Open RQt Image View in another terminal:

```bash
source /opt/ros/jazzy/setup.bash

ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/depth_camera/depth_visualized
```

The visualization converts the floating-point depth image into an 8-bit grayscale image.

Closer objects appear brighter while farther objects appear darker.

The depth range can be changed using ROS parameters:

```bash
python3 ~/final_year_project_ws/tools/depth_visualizer.py \
    --ros-args \
    -p min_depth:=0.5 \
    -p max_depth:=5.0
```

---

# Autonomous Navigation Pipeline

The planned navigation pipeline is:

```text
LiDAR ────────────────┐
                      │
Depth Camera ─────────┤
                      │
IMU ──────────────────┤
                      ▼
                Perception
                      │
                      ▼
             Localization
                      │
                      ▼
                SLAM / Map
                      │
                      ▼
                    Nav2
                      │
          ┌───────────┴───────────┐
          │                       │
       Planner                Controller
          │                       │
          └───────────┬───────────┘
                      ▼
                ROS 2 Control
                      │
                      ▼
                Robot Motion
```

---

# LLM / VLM Integration

The long-term objective is to add an AI reasoning layer above the conventional navigation stack.

For example, a user could provide a command such as:

```text
"Go to the charging station and avoid the boxes."
```

The planned architecture is:

```text
Natural Language Command
          │
          ▼
        LLM
          │
   Task decomposition
          │
          ▼
        VLM
          │
   Scene understanding
          │
          ▼
   Navigation Goal
          │
          ▼
        Nav2
          │
          ▼
       Robot
```

The LLM/VLM layer is currently a **planned development stage** and is not represented as fully implemented functionality in the current version.

---

# Current Project Status

## Completed

* [x] ROS 2 Jazzy workspace created
* [x] `rbot` base repository integrated
* [x] Custom project packages built successfully
* [x] Gazebo simulation working
* [x] Warehouse environment working
* [x] Custom robot spawned
* [x] Custom robot meshes installed
* [x] Gazebo mesh path issue resolved
* [x] `gz_ros2_control` plugin loading resolved
* [x] Controller manager initialized
* [x] Differential-drive controller working
* [x] LiDAR simulation verified
* [x] RGB camera verified
* [x] Depth camera verified
* [x] IMU topic available
* [x] Depth data numerically validated
* [x] RQt Image View configured
* [x] Standalone depth visualization tool created
* [x] Localization infrastructure available
* [x] SLAM infrastructure available
* [x] Nav2 infrastructure available

## Currently Being Developed

* [ ] Full SLAM mapping validation
* [ ] AMCL localization validation
* [ ] Autonomous Nav2 navigation
* [ ] Obstacle avoidance testing
* [ ] Waypoint navigation
* [ ] Recovery behaviors
* [ ] Advanced perception
* [ ] RealSense hardware integration
* [ ] RPLIDAR S2 hardware integration
* [ ] LLM integration
* [ ] VLM integration
* [ ] Natural-language navigation
* [ ] Simulation-to-real deployment

---

# Hardware Target

The simulation is being developed with eventual deployment to a physical autonomous robot.

Target sensors:

```text
Slamtec RPLIDAR S2
        +
Intel RealSense Depth Camera
        +
IMU
```

The goal is to maintain the same ROS 2 topic and software architecture between simulation and real hardware wherever possible.

---

# Repository Structure

```text
llm-vlm-autonomous-navigation/
│
├── src/
│   └── rbot/
│       ├── docs/
│       ├── maps/
│       ├── scripts/
│       └── src/
│           ├── bringup/
│           ├── control/
│           ├── localization/
│           ├── mapping/
│           ├── navigation/
│           ├── perception/
│           ├── robot/
│           ├── simulation/
│           └── utils/
│
├── tools/
│   └── depth_visualizer.py
│
├── .gitignore
└── README.md
```

Build-generated directories such as:

```text
build/
install/
log/
```

are intentionally excluded from Git.

---

# Development Roadmap

## Phase 1 — Simulation Foundation

* Robot model
* Gazebo world
* Sensor simulation
* ROS 2 Control

**Status: Completed**

## Phase 2 — Autonomous Navigation

* SLAM
* Localization
* Nav2
* Path planning
* Obstacle avoidance
* Waypoint navigation

**Status: In Progress**

## Phase 3 — Real Hardware

* RPLIDAR S2
* Intel RealSense
* IMU
* Motor controller
* Odometry

**Status: Planned**

## Phase 4 — AI Perception

* Object detection
* Depth-based perception
* Scene understanding
* Visual reasoning

**Status: Planned**

## Phase 5 — LLM/VLM Navigation

* Natural-language commands
* VLM scene understanding
* LLM task decomposition
* Intelligent goal generation
* Context-aware navigation

**Status: Planned**

## Phase 6 — Simulation-to-Real

* Hardware deployment
* Sensor calibration
* Navigation benchmarking
* Failure recovery
* Safety validation
* Final autonomous demonstration

**Status: Planned**

---

# Project Status

**Current milestone: Simulation and ROS 2 autonomous-navigation foundation**

The robot simulation, sensor streams, ROS 2 Control and core navigation infrastructure are operational. The next major milestone is to validate complete **SLAM → localization → Nav2 autonomous navigation** in the simulated warehouse before moving toward real RPLIDAR S2 and Intel RealSense hardware.

---

## License

See the license files included in the repository.

````

After creating it, run:

```bash
cd ~/final_year_project_ws

git add README.md
git commit -m "Add project README and documentation"
git push
````

This version is deliberately honest about the current stage: **the simulation and navigation foundation are working; LLM/VLM is the next development layer.**
