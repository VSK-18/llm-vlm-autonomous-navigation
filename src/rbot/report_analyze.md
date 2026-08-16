# Technical Analysis Report: rbot Simulation Stack

This report evaluates the `rbot` repository as the simulation foundation for the final-year project: **"Edge Deployed Agentic AI for ROS2 Service Using Small Language Modelling"**.

---

## A. Repository Architecture

The `rbot` repository is a modular, well-structured ROS 2 workspace targetting **ROS 2 Jazzy** and **Gazebo Harmonic (gz-sim 8.x)** on **Ubuntu 24.04**. It follows the standard ROS 2 package layout and separates concerns across simulation, description, control, perception, localization, mapping, and navigation.

### ROS 2 Packages & Roles

| Package | Build Type | Purpose / Description |
| :--- | :--- | :--- |
| **`rlai_bringup`** | `ament_python` | Top-level orchestrating package. Holds launch files to launch Gazebo, EKF, AMCL, Nav2, and RViz under a unified entrypoint. |
| **`rlai_description`** | `ament_cmake` | Robot URDF/Xacro files containing links, joints, and sensor mount configurations (camera, LiDAR, IMU, GPS). |
| **`rlai_meshes`** | `ament_cmake` | Holds the binary CAD files (STL format) for the robot components (chassis, wheels, payload platform). |
| **`rlai_gazebo`** | `ament_cmake` | Manages Gazebo Harmonic worlds, custom static models (shelves, pallets, jacks), and the ROS-Gazebo bridge configuration. |
| **`rlai_control`** | `ament_cmake` | Configures `ros2_control` to manage hardware interfaces (`diff_drive_controller` and `joint_state_broadcaster`). Also runs a `nav2_velocity_smoother` lifecycle node to smooth `/cmd_vel` inputs. |
| **`rlai_teleop`** | `ament_python` | Manual joystick/keyboard control and a software-based emergency stop node publishing zero velocity. |
| **`rlai_localization`** | `ament_python` | Performs sensor fusion using `robot_localization` (EKF node) fusing wheel odometry and filtered IMU data. Also configures `nav2_amcl` for global particle filter localization. |
| **`rlai_mapping`** | `ament_python` | Configures and launches SLAM Toolbox (`async_slam_toolbox_node`) for real-time occupancy grid mapping. |
| **`rlai_navigation`** | `ament_python` | Configures Nav2 planning and control nodes, including the MPPI controller, SMAC Hybrid-A* planner, behavior trees, and a programmatic action client (`nav_client.py`). |
| **`rlai_camera_processing`**| `ament_cmake` | Combines standard ROS 2 composable nodes (`depth_image_proc` and `stereo_image_proc`) in a shared container for rectifying frames and generating depth point clouds. |
| **`rlai_lidar_processing`**  | `ament_cmake` | C++ node using PCL to filter 3D LiDAR point clouds by height (Z axis) and downsample using voxel grids. |
| **`rlai_isaac`** | `ament_python` | Scaffolding/placeholder package for future NVIDIA Isaac Sim integration. Currently contains no code. |
| **`rlai_utils`** | `ament_python` | Placeholder package for shared Python utilities. |

---

## B. What Already Works

1. **Simulation World & Asset Spawning**: Loading custom worlds and spawning the physical `rlai_bot` robot with mesh visualization, material properties, and collision physics in Gazebo Harmonic.
2. **Drive Actuation & Control**: Velocity commands published to `/cmd_vel` are smoothed and converted by `ros2_control`'s `diff_drive_controller` to actuate Gazebo wheels.
3. **Odometry & EKF Fusion**: The EKF node fuses raw wheel odometry and IMU data (`/imu/data_raw` filtered via `imu_filter_madgwick`) to produce a smooth `/odometry/filtered` topic and the `odom -> base_footprint` TF.
4. **Perception pipeline**: Raw depth camera images are successfully converted to 3D point clouds (`/depth_camera/points`) via composable nodes.
5. **Mapping & Localization**:
   - SLAM Toolbox online async mapping creates and saves 2D occupancy grids.
   - AMCL loads a saved map and provides global localization by publishing the `map -> odom` TF.
6. **Autonomous Navigation**: Nav2 stack executes paths using the SMAC Hybrid-A* global planner and follows them using the MPPI local controller. A Python action client supports single-goal dispatching and patrolling.
7. **Verification Tooling**: Built-in test script (`tests/test_gazebo_assets.py`) checks that Gazebo models and world specifications conform to SDFormat 1.11.

---

## C. What We Can Reuse

- **Xacro / URDF Base & Joints**: The physical robot dimensions (0.35m wheel separation, 0.0625m wheel radius) and joint dynamics in `rlai_description` are directly reusable.
- **TF Ownership Design**: The clean isolation of TF publishers (EKF for `odom -> base_footprint`, AMCL/SLAM for `map -> odom`, and `robot_state_publisher` for link transforms) is robust and reusable.
- **Nav2 MPPI & SMAC Parameters**: The tuned MPPI critic weights (Cost, Constraint, Goal, Path Align) and SMAC turning radius parameters represent a high-quality baseline.
- **ROS-Gazebo Bridges**: The custom mapping files (`ros_gz_bridge.yaml`) map ROS 2 Jazzy topics to Gazebo Harmonic topics natively and correctly.

---

## D. What We Need to Modify

- **URDF/Xacro Sensor Specs**:
  - The 2D LiDAR is configured for a generic RPLIDAR A3. To match the RPLIDAR S2, we should tweak the range limits to `0.05m` - `30.0m` (currently `0.30m` - `25.0m`) in `gazebo_sensors.urdf.xacro`.
- **Physical Robot Transition**:
  - When moving to the physical robot, we must disable Gazebo plugins and instead launch actual hardware drivers (e.g. `rplidar_ros` and `realsense2_camera`). These drivers must map their outputs to the standard `/scan` and `/depth_camera` topics or be remapped in Nav2/perception launch files.
- **Agentic Task & Semantic Memory Integration**:
  - The repository contains **no AI/VLM/LLM components**. To satisfy the project's agentic AI goals, we must write a new ROS 2 package (e.g. `rlai_agent`) implementing natural-language command parsers, an agentic task planner, a spatial/semantic memory system (e.g., using a vector database), and bridges to LLMs/VLMs.

---

## E. What We Should NOT Use

- **`rlai_isaac`**: Scaffolding package only. Since Gazebo Harmonic is the target simulator, this package can be ignored.
- **`rlai_lidar_processing`**: This C++ package processes 3D LiDAR (Velodyne VLP-16) point clouds. Since the physical robot will use a 2D LiDAR (RPLIDAR S2) and an RGB-D camera, this package is redundant and should be disabled to save laptop CPU/VRAM.
- **`rlai_camera_processing` Stereo Nodes**: The physical robot will use a depth camera, not a stereo camera rig. The stereo rectification and disparity nodes in `camera_processing.launch.py` should remain disabled.

---

## F. Sensor Compatibility (RPLIDAR S2 + Intel RealSense)

1. **Intel RealSense**:
   - **Simulation**: Already supported. Setting the parameter `camera_model:=intel_d435i` loads a camera model configured with the exact D435i horizontal FOV (87° / 1.5184 rad) and range. The depth topic `/depth_camera/depth` is transformed to a point cloud `/depth_camera/points`, matching RealSense outputs.
   - **Physical**: Extremely compatible. The `realsense2_camera` driver publishes identical standard image/depth topics.
2. **Slamtec RPLIDAR S2**:
   - **Simulation**: Trivial to adapt. The simulated RPLIDAR A3 in `gazebo_sensors.urdf.xacro` can be matched to S2 specifications (10 Hz update, 0.05m to 30.0m range) with minor edits.
   - **Physical**: Fully compatible. The `rplidar_ros` package publishes standard `/scan` messages which SLAM Toolbox and Nav2 consume directly.

---

## G. Laptop Feasibility

### Development System Specs
- **GPU**: NVIDIA RTX 4050 Laptop GPU (6 GB VRAM)
- **CPU**: Intel Core 7
- **RAM**: 16 GB
- **OS**: Ubuntu 24.04 (X11)

### Assessment
- **Simulation + Navigation (Fully Feasible)**: The RTX 4050 handles Gazebo physics and sensor rendering comfortably. The Intel Core 7 has sufficient cores for the EKF, SLAM, and Nav2 nodes.
  - *Optimization Note*: Nav2's MPPI controller is CPU-intensive due to sampling 2000 trajectories. If control loop rate warnings appear, reduce the batch size in `nav2_params.yaml` to `500` or `1000`.
- **LLM/VLM Integration (Bottleneck)**: Running a 3D simulation with rendering *plus* local execution of a VLM/SLM (e.g. Llama-3.2-3B or Florence-2) will quickly exceed 6 GB VRAM, causing OOM (Out Of Memory) crashes or slow CPU fallback.
  - *Recommendation*: During simulation development, call cloud-based LLM/VLM APIs (like the Gemini API) to perform agentic planning and perception. If offline execution is required on the edge Jetson Orin Nano later, deploy highly quantized models (e.g., INT4/INT8 GGUF) and run Gazebo headlessly (`--headless`) during testing to free up VRAM.

---

## H. Dependency / Build Risks

### The `ament_python` rosdep issue

- **Cause**: The 7 Python packages (`rlai_localization`, `rlai_utils`, `rlai_bringup`, `rlai_teleop`, `rlai_isaac`, `rlai_navigation`, `rlai_mapping`) declare `<buildtool_depend>ament_python</buildtool_depend>` in their `package.xml` files. 
- **The Issue**: In ROS 2, `ament_python` is a build *type* declared under `<export><build_type>ament_python</build_type></export>`. It is not an actual package or a dependency registered in the official rosdep database. As a result, rosdep reports: `Cannot locate rosdep definition for [ament_python]`.
- **Workspace Impact**: This does **not** break compilation with `colcon build` because `colcon` parses the `<build_type>` export tag directly. However, it **does** cause standard `rosdep install` commands to fail, blocking the automatic resolution of other system dependencies.
- **Mitigation**: The package developers bypassed this by adding `--skip-keys "ament_python"` to the install script. The correct fix is to delete the `<buildtool_depend>ament_python</buildtool_depend>` lines from the `package.xml` of all 7 packages.

---

## I. Recommended Next Steps

1. **Clean up dependencies**: Remove the `<buildtool_depend>ament_python</buildtool_depend>` lines from the `package.xml` files of the 7 affected packages to allow clean `rosdep` runs.
2. **Build and Validate Locally**: Run the install and build scripts natively:
   ```bash
   bash scripts/install_deps.sh
   bash scripts/build.sh
   ```
3. **Execute Mapping Baseline**: Test the simulation and mapping stack using the quick-start path to build a map of the `small_warehouse` environment.
4. **Create AI Integration Package**: Create a new package `rlai_agent` to house the LLM client, task planner, and semantic database, interfacing with Nav2 via the `nav_client` interface.
