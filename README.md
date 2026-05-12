# navigation2 workspace

## Overview
- `rc_nav_bringup`: integrated workflow for `Point-LIO + pointcloud_to_laserscan + Nav2`
- `rc_navigation`: pure Nav2 debugging package
- `localization/Point-LIO`: LiDAR-inertial odometry / mapping
- `drivers/livox_ros_driver2`: Livox MID360 driver

## Build
```bash
cd /home/ls/Desktop/navigation2
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Mapping
1. Start the Livox driver.
2. Start the integrated bringup:
```bash
ros2 launch rc_nav_bringup rc_nav_bringup.launch.py mode:=mapping
```
3. Save the map:
```bash
ros2 run nav2_map_server map_saver_cli -f /home/ls/Desktop/navigation2/my_map
```

## Known-map navigation
```bash
ros2 launch rc_nav_bringup rc_nav_bringup.launch.py mode:=known_map map:=/abs/path/to/map.yaml
```

## Nav2 debugging
- Map + AMCL:
```bash
ros2 launch rc_navigation bringup_rc_navigation.py launch_map_server:=True launch_navigation:=False launch_rviz:=True map:=/abs/path/to/map.yaml
```
- Only navigation stack:
```bash
ros2 launch rc_navigation bringup_rc_navigation.py launch_map_server:=False launch_navigation:=True launch_rviz:=True
```

## Notes
- `rc_nav_bringup` is the recommended entry for the real robot workflow.
- `rc_navigation` is for isolated Nav2 component debugging.
- `nav2_params.yaml` already contains the TEB and `costmap_converter` settings.
