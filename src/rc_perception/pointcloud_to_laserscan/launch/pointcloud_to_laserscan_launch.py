from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
import yaml
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "target_frame",
            default_value="lidar_link",# 输出扫描数据的目标坐标系
            description="target frame of the output scan data"
        ),
        DeclareLaunchArgument(
            "cloud_in_topic",
            default_value="/livox/lidar/pointcloud",# 输入点云数据的主题
            description="input point cloud topic"
        ),
        DeclareLaunchArgument(
            "parent_frame",
            default_value="lidar_link",
            description="parent frame for the static sensor transform"
        ),
        DeclareLaunchArgument(
            "sensor_frame",
            default_value="livox_frame",
            description="sensor frame published by the driver"
        ),
        # lidar_link 与 livox_frame 的静态 TF
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0',
                '--qx', '0', '--qy', '0', '--qz', '0', '--qw', '1',
                '--frame-id', LaunchConfiguration('parent_frame'),
                '--child-frame-id', LaunchConfiguration('sensor_frame')
            ]
        ),
        # 使用 pointcloud_to_laserscan 将 3D 点云转为 2D 激光扫描
        Node(
            package='pointcloud_to_laserscan', executable='pointcloud_to_laserscan_node',
            remappings=[('cloud_in', [LaunchConfiguration('cloud_in_topic')]),
                        ('scan', ['/scan'])],
            parameters=[
                os.path.join(
                get_package_share_directory('pointcloud_to_laserscan'),
                    'config',
                    'parameters.yaml'
                    ),
                {'target_frame': LaunchConfiguration('target_frame')}
                ],
            name='pointcloud_to_laserscan'
        )
    ])
