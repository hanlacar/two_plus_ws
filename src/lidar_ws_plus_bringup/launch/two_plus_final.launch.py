#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    share = get_package_share_directory(
        'lidar_ws_plus_bringup'
    )

    real_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                share,
                'launch',
                'two_plus_real.launch.py'
            )
        ),
        launch_arguments={
            'enable_lidar':
                LaunchConfiguration('enable_lidar'),

            'enable_rear_lidar':
                LaunchConfiguration('enable_rear_lidar'),

            'enable_avoidance':
                LaunchConfiguration('enable_avoidance'),

            'front_serial_port':
                LaunchConfiguration('front_serial_port'),

            'rear_serial_port':
                LaunchConfiguration('rear_serial_port'),

            'avoidance_route_file':
                LaunchConfiguration('avoidance_route_file'),

            'avoidance_auto_start':
                LaunchConfiguration('avoidance_auto_start'),

            'network_path':
                LaunchConfiguration('network_path'),

            'start_segment':
                LaunchConfiguration('start_segment'),

            'mission_auto_start':
                LaunchConfiguration('mission_auto_start'),

            'use_rviz':
                LaunchConfiguration('use_rviz'),
        }.items()
    )

    parking_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                share,
                'launch',
                'two_plus_parking.launch.py'
            )
        ),
        condition=IfCondition(
            LaunchConfiguration('enable_parking_stack')
        ),
        launch_arguments={
            'map':
                LaunchConfiguration('parking_map'),

            'execute':
                LaunchConfiguration('parking_execute'),

            'auto_trigger':
                LaunchConfiguration('parking_auto_trigger'),

            'require_mcu_status':
                LaunchConfiguration('parking_require_mcu_status'),
        }.items()
    )

    return LaunchDescription([

        # --------------------------
        # LiDAR
        # --------------------------
        DeclareLaunchArgument(
            'enable_lidar',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'enable_rear_lidar',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'front_serial_port',
            default_value='/dev/ttyUSB0'
        ),

        DeclareLaunchArgument(
            'rear_serial_port',
            default_value='/dev/ttyUSB1'
        ),

        # --------------------------
        # Mode 5 avoidance
        # --------------------------
        DeclareLaunchArgument(
            'enable_avoidance',
            default_value='true'
        ),

        DeclareLaunchArgument(
            'avoidance_route_file',
            default_value=''
        ),

        DeclareLaunchArgument(
            'avoidance_auto_start',
            default_value='false'
        ),

        # --------------------------
        # Main segmented route
        # --------------------------
        DeclareLaunchArgument(
            'network_path',
            default_value=os.path.join(
                get_package_share_directory('mission_manager'),
                'routes',
                'route_network_segmented_10.csv'
            )
        ),

        DeclareLaunchArgument(
            'start_segment',
            default_value='START_A'
        ),

        DeclareLaunchArgument(
            'mission_auto_start',
            default_value='false'
        ),

        # --------------------------
        # Modes 7 / 10 parking
        # --------------------------
        DeclareLaunchArgument(
            'enable_parking_stack',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'parking_map',
            default_value=''
        ),

        DeclareLaunchArgument(
            'parking_execute',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'parking_auto_trigger',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'parking_require_mcu_status',
            default_value='false'
        ),

        # --------------------------
        # Visualization
        # --------------------------
        DeclareLaunchArgument(
            'use_rviz',
            default_value='false'
        ),

        real_launch,
        parking_launch,
    ])
