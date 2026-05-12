import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('rc_nav_bringup')
    nav2_share = get_package_share_directory('nav2_bringup')
    pointlio_params = os.path.join(pkg_share, 'config', 'pointlio_mid360.yaml')
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    pointlio_rviz_cfg = os.path.join(pkg_share, 'rviz', 'pointlio.rviz')
    nav2_rviz_cfg = os.path.join(nav2_share, 'rviz', 'nav2_default_view.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time', default='False')
    nav_rviz = LaunchConfiguration('nav_rviz', default='True')
    pointlio_rviz = LaunchConfiguration('pointlio_rviz', default='False')
    mode = LaunchConfiguration('mode', default='mapping')
    map_yaml = LaunchConfiguration('map')

    pointlio_node = Node(
        package='point_lio',
        executable='pointlio_mapping',
        name='laserMapping',
        output='screen',
        parameters=[
            pointlio_params,
            {'use_sim_time': use_sim_time}
        ]
    )

    pointcloud_to_laserscan_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('pointcloud_to_laserscan'), 'launch', 'pointcloud_to_laserscan_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'target_frame': 'lidar_link',
            'cloud_in_topic': '/livox/lidar/pointcloud',
            'parent_frame': 'lidar_link',
            'sensor_frame': 'livox_frame',
        }.items()
    ) 

    pointlio_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', pointlio_rviz_cfg],
        condition=IfCondition(pointlio_rviz),
        output='screen'
    )

    nav2_bringup_launch_mapping = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, 'launch', 'bringup_launch.py')),
        condition=IfCondition(PythonExpression(['"', mode, '" == "mapping"'])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam': 'True',
            'map': map_yaml,
            'params_file': nav2_params,
            'autostart': 'True',
            'use_composition': 'False',
            'use_respawn': 'False',
        }.items()
    )

    nav2_bringup_launch_known_map = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, 'launch', 'bringup_launch.py')),
        condition=IfCondition(PythonExpression(['"', mode, '" == "known_map"'])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam': 'False',
            'map': map_yaml,
            'params_file': nav2_params,
            'autostart': 'True',
            'use_composition': 'False',
            'use_respawn': 'False',
        }.items()
    )

    nav2_rviz_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, 'launch', 'rviz_launch.py')),
        condition=IfCondition(nav_rviz),
        launch_arguments={'rviz_config': nav2_rviz_cfg}.items()
    )

    ld = LaunchDescription()
    ld.add_action(DeclareLaunchArgument('use_sim_time', default_value='False'))
    ld.add_action(DeclareLaunchArgument('mode', default_value='mapping', choices=['mapping', 'known_map']))
    ld.add_action(DeclareLaunchArgument('map', default_value='', description='Known-map yaml, required when mode:=known_map'))
    ld.add_action(DeclareLaunchArgument('nav_rviz', default_value='True'))
    ld.add_action(DeclareLaunchArgument('pointlio_rviz', default_value='False'))
    ld.add_action(pointlio_node)
    ld.add_action(pointlio_rviz_node)
    ld.add_action(nav2_bringup_launch_mapping)
    ld.add_action(nav2_bringup_launch_known_map)
    ld.add_action(nav2_rviz_node)
    ld.add_action(pointcloud_to_laserscan_launch)
    return ld
