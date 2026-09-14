#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    lidar_share = get_package_share_directory(
        'lidar_ws_plus_bringup'
    )

    mission_share = get_package_share_directory(
        'mission_manager'
    )

    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                lidar_share,
                'launch',
                'real_vehicle.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'false',

            'enable_lidar':
                LaunchConfiguration('enable_lidar'),

            'enable_rear_lidar':
                LaunchConfiguration('enable_rear_lidar'),

            'enable_lidar_tf':
                LaunchConfiguration('enable_lidar'),

            'enable_rear_tf':
                LaunchConfiguration('enable_rear_lidar'),

            'enable_motion_detector':
                LaunchConfiguration('enable_lidar'),

            'enable_avoidance':
                LaunchConfiguration('enable_avoidance'),

            'enable_mux': 'true',

            'front_serial_port':
                LaunchConfiguration('front_serial_port'),

            'rear_serial_port':
                LaunchConfiguration('rear_serial_port'),

            'route_file':
                LaunchConfiguration('avoidance_route_file'),

            'avoidance_auto_start':
                LaunchConfiguration('avoidance_auto_start'),

            # two_plus_ws 내부에서는 mission_manager의 숫자 mode 사용
            'mode_topic': '/drive_mode',

            'use_rviz':
                LaunchConfiguration('use_rviz'),
        }.items()
    )

    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                mission_share,
                'launch',
                'dr_real_segmented_follower.launch.py'
            )
        ),
        launch_arguments={
            'network_path':
                LaunchConfiguration('network_path'),

            'start_segment':
                LaunchConfiguration('start_segment'),

            'auto_start':
                LaunchConfiguration('mission_auto_start'),
        }.items()
    )

    mcu_adapter = Node(
        package='mission_manager',
        executable='simple_mcu_command_adapter',
        name='simple_mcu_command_adapter',
        output='screen',
        parameters=[{
            # dr_real_segmented_follower의 일반주행 출력
            'gps_drive_topic': '/gps_drive',
            'gps_wheel_topic': '/gps_wheel',

            # command_mux의 유일한 최종 LiDAR 출력
            'lidar_drive_topic': '/lidar_drive',
            'lidar_wheel_topic': '/lidar_wheel',

            'mode_topic': '/drive_mode',

            'mcu_drive_topic': '/mcu/cmd_drive',
            'mcu_wheel_topic': '/mcu/cmd_wheel',
            'mcu_stop_topic': '/mcu/cmd_stop',

            'max_steer_deg': 22,
            'command_timeout_s': 0.35,
            'publish_rate_hz': 20.0,
        }]
    )

    default_network = os.path.join(
        mission_share,
        'routes',
        'route_network_segmented_10.csv'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'enable_lidar',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'enable_rear_lidar',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'enable_avoidance',
            default_value='true'
        ),

        DeclareLaunchArgument(
            'front_serial_port',
            default_value='/dev/ttyUSB0'
        ),

        DeclareLaunchArgument(
            'rear_serial_port',
            default_value='/dev/ttyUSB1'
        ),

        DeclareLaunchArgument(
            'avoidance_route_file',
            default_value=''
        ),

        DeclareLaunchArgument(
            'avoidance_auto_start',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'network_path',
            default_value=default_network
        ),

        DeclareLaunchArgument(
            'start_segment',
            default_value='START_A'
        ),

        DeclareLaunchArgument(
            'mission_auto_start',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'use_rviz',
            default_value='false'
        ),

        lidar_launch,
        mission_launch,
        mcu_adapter,
    ])
