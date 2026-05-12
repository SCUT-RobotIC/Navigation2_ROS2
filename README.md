# navigation2 workspace

## Overview
- `drivers/livox_ros_driver2`: Livox MID360 driver
- `localization/Point-LIO`: LiDAR-inertial odometry / mapping
- `rc_nav_bringup`: integrated workflow for `Point-LIO + pointcloud_to_laserscan + Nav2`
- `rc_navigation`: Packages related to navigation
    - `rc_navigation_test`: pure Nav2 debugging package
- `rc_perception`: Packages to process pointcloud
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
- Check the map
```bash
ros2 launch rc_navigation map_server_launch.py map:=/home/ls/Desktop/navigation2/src/rc_nav_bringup/map/TestMap.yaml
```
- rviz2
```bash
ros2 launch rc_navigation rviz_launch.py
```

## Setting Points
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 1.2, z: 0.0}, orientation: {z: 0.0, w: 1.0}}}}"
```

## Notes
- `rc_nav_bringup` is the recommended entry for the real robot workflow.
- `nav2_params.yaml` already contains the TEB and `costmap_converter` settings.
