#!/usr/bin/env python3

import os

from ament_index_python.packages import (
    get_package_share_directory
)

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription
)
from launch.launch_description_sources import (
    PythonLaunchDescriptionSource
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    parking_share = get_package_share_directory(
        't_parking_sim'
    )

    real_t_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                parking_share,
                'launch',
                'real_t_parking.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'false',

            'map':
                LaunchConfiguration('map'),

            'front_scan_topic':
                '/front/scan',

            'rear_scan_topic':
                '/rear/scan',

            'auto_start':
                'false',

            'execute':
                LaunchConfiguration('execute'),

            'target_slot':
                'auto',

            'start_rviz':
                'false',

            # two_plus_real이 LiDAR TF를 소유
            'start_robot_state_publisher':
                'false',

            'mode_topic':
                '/drive_mode',

            # 현재 two_plus_ws 자체 테스트에서는
            # 외부 MCU 상태 노드를 요구하지 않음.
            'require_mcu_status':
                LaunchConfiguration('require_mcu_status'),
        }.items()
    )

    parallel_config = os.path.join(
        parking_share,
        'config',
        'parallel_parking_auto.yaml'
    )

    parallel_parking = Node(
        package='t_parking_sim',
        executable='auto_parallel_parking.py',
        name='parallel_parking_auto',
        output='screen',

        parameters=[
            parallel_config,
            {
                'use_sim_time': False,
                'auto_start': False,
                'execute': ParameterValue(
                    LaunchConfiguration('execute'),
                    value_type=bool
                ),
                'target_slot': 'auto',
                'freeze_slam_during_execution': False,
            }
        ],

        remappings=[
            ('/scan', '/front/scan'),
            ('/scan_rear', '/rear/scan'),
        ]
    )

    router = Node(
        package='lidar_ws_plus_bringup',
        executable='parking_mode_router',
        name='parking_mode_router',
        output='screen',
        parameters=[{
            'mode_topic': '/drive_mode',

            # 안전을 위해 기본 false.
            # 실제 자동 모드 전환 시험 때 true로 변경.
            'auto_trigger': ParameterValue(
                LaunchConfiguration('auto_trigger'),
                value_type=bool
            ),
        }]
    )

    default_map = os.path.join(
        parking_share,
        'maps',
        'combined_parking_map_real_vehicle.yaml'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'map',
            default_value=default_map
        ),

        DeclareLaunchArgument(
            'execute',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'auto_trigger',
            default_value='false'
        ),

        DeclareLaunchArgument(
            'require_mcu_status',
            default_value='false'
        ),

        real_t_launch,
        parallel_parking,
        router,
    ])
