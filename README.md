# navigation2 工作区

## 概览
- `drivers/livox_ros_driver2`：Livox MID360 驱动
- `localization/Point-LIO`：激光雷达-IMU 里程计与建图
- `rc_nav_bringup`：`Point-LIO + pointcloud_to_laserscan + Nav2` 的集成启动入口
- `rc_navigation`：导航相关功能包
- `rc_navigation_test`：纯 Nav2 调试用功能包
- `rc_perception`：点云处理相关功能包

## 系统架构

### 雷达点云 / 激光消息流向

真实机器人推荐从 `rc_nav_bringup` 进入整套流程。

1. `livox_ros_driver2`
   - 发布 `/livox/lidar`，类型为 `livox_ros_driver2/msg/CustomMsg`
   - 发布 `/livox/lidar/pointcloud`，类型为 `sensor_msgs/msg/PointCloud2`
   - 发布 `/livox/imu`，类型为 `sensor_msgs/msg/Imu`

2. `point_lio`（可执行文件为 `pointlio_mapping`）
   - 根据雷达类型订阅 `/livox/lidar` 或 `/livox/lidar/pointcloud`
   - 订阅 `/livox/imu`
   - 发布 `/aft_mapped_to_init`，类型为 `nav_msgs/msg/Odometry`
   - 发布 `/path`，类型为 `nav_msgs/msg/Path`
   - 发布 `cloud_registered`、`cloud_registered_body`、`cloud_effected`、`Laser_map`

3. `pointcloud_to_laserscan`
   - 订阅 `/livox/lidar/pointcloud`
   - 将 3D 点云转换为 2D 激光 `/scan`
   - `slam_toolbox` 与 `amcl` 都使用 `/scan`

4. `slam_toolbox` 或 `amcl`
   - 订阅 `/scan`
   - 结合 `lidar_odom` 坐标系下的里程计信息
   - 生成 `map -> lidar_odom` 这条全局定位变换

5. Nav2
   - 全局规划工作在 `map` 坐标系
   - 局部控制与局部代价地图主要工作在 `lidar_odom`
   - 机器人基坐标系为 `lidar_link`

### TF 链路

当前工作区使用的核心 TF 链如下：

`map -> lidar_odom -> lidar_link -> livox_frame`

各功能包负责发布的 TF 为：

- `point_lio`
  - 发布 `lidar_odom -> lidar_link`
  - 同时发布 `/aft_mapped_to_init`，其 `header.frame_id = lidar_odom`
- `pointcloud_to_laserscan` 的 launch
  - 启动静态 TF：`lidar_link -> livox_frame`
- `slam_toolbox`
  - 在 `mode:=mapping` 下发布 `map -> lidar_odom`
- `amcl`
  - 在 `mode:=known_map` 下发布 `map -> lidar_odom`

需要注意：

- `Point-LIO` 不直接提供 Nav2 所需的全局 `map` 坐标系
- `Point-LIO` 负责的是局部里程计，也就是 `lidar_odom`
- 全局定位由 `slam_toolbox` 或 `amcl` 补上

### Point-LIO、slam_toolbox、amcl 的作用与关系

`Point-LIO`
- 用 LiDAR + IMU 生成高频局部里程计
- 定义局部里程计坐标系 `lidar_odom`
- 发布机器人在 `lidar_odom` 下的位姿，以及 `lidar_odom -> lidar_link`
- 它本身不是 Nav2 的全局定位模块

`slam_toolbox`
- 用于 `mode:=mapping`
- 使用 `/scan` 一边运动一边建图 / 对地图进行匹配
- 发布 `map -> lidar_odom`
- 作用是把 `Point-LIO` 提供的局部坐标系放到全局地图中

`amcl`
- 用于 `mode:=known_map`
- 使用 `/scan` 和一张已知的栅格地图进行定位
- 发布 `map -> lidar_odom`
- 当已有地图时，它替代 `slam_toolbox`

三者关系可以理解为：

- `Point-LIO` 解决“机器人当前局部怎么动”
- `slam_toolbox` 在建图模式下解决“这个局部 odom 坐标系在正在构建的地图里在哪里”
- `amcl` 在已知地图模式下解决“这个局部 odom 坐标系在已有地图里在哪里”

### mapping 模式与 known_map 模式

`mode:=mapping`
- 启动 `pointlio_mapping`
- 启动 `pointcloud_to_laserscan`
- 通过 Nav2 bringup 传入 `slam:=True`
- Nav2 官方 bringup 会进一步间接启动 `slam_toolbox`
- 最终由 `slam_toolbox` 发布 `map -> lidar_odom`

`mode:=known_map`
- 启动 `pointlio_mapping`
- 启动 `pointcloud_to_laserscan`
- 通过 Nav2 bringup 传入 `slam:=False`
- Nav2 官方 bringup 会进入 localization 分支
- 最终由 `amcl` 发布 `map -> lidar_odom`

这也是为什么在 `src/rc_nav_bringup/launch/rc_nav_bringup.launch.py` 里看不到直接启动 `slam_toolbox` 的节点，但它仍然会在建图模式下运行。

**local_costmap 中的 global_frame 参数需设置为map，否则规划频率跟不上**

## 编译
```bash
cd /home/ls/Desktop/navigation2
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 建图模式
1. 启动 Livox 驱动
```bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```
2. 启动集成流程

`rc_nav_bringup.launch.py` 已经会启动 `pointlio_mapping`、`pointcloud_to_laserscan`、Nav2，
并且在 `mapping` 模式下通过 `nav2_bringup` 间接启动 `slam_toolbox`。

```bash
ros2 launch rc_nav_bringup rc_nav_bringup.launch.py mode:=mapping
```
3. 保存地图
```bash
ros2 run nav2_map_server map_saver_cli -f /home/ls/Desktop/navigation2/my_map
```

## 已知地图导航
```bash
ros2 launch rc_nav_bringup rc_nav_bringup.launch.py mode:=known_map map:=/abs/path/to/map.yaml
```

## Nav2 调试
- 检查地图
```bash
ros2 launch rc_navigation_test map_server_launch.py map:=/home/ls/Desktop/navigation2/src/rc_nav_bringup/map/TestMap.yaml
```
- rviz2
```bash
ros2 launch rc_navigation_test rviz_launch.py
```

## 发送导航目标点
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 1.2, z: 0.0}, orientation: {z: 0.0, w: 1.0}}}}"
```

## 说明
- `rc_nav_bringup` 是真实机器人流程的推荐入口
- `nav2_params.yaml` 中已经包含 TEB 和 `costmap_converter` 的相关配置
