from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.actions import Node
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.conditions import LaunchConfigurationEquals
from ament_index_python.packages import get_package_share_directory
import os
from launch.substitutions import EnvironmentVariable
from launch.actions import GroupAction
from launch_ros.actions import SetParameter
from launch.actions import TimerAction


def generate_launch_description():
    here_launch_files = os.path.join(get_package_share_directory("rebet_mirte"), "launch")
    nav_launch_files = os.path.join(get_package_share_directory("mirte_navigation"), "launch")

    arborist = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(here_launch_files, "arborist_config_launch.py")
        )
    )

    simulation = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(here_launch_files, "simulation_rebet_mirte.launch.py")
        ),
        launch_arguments={
            "which_world": "robocupathome",
        }.items(),
    )

    navigation = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(nav_launch_files, "robot_navigation.launch.py")
        ),
        launch_arguments={
            "use_sim_time": "true",
        }.items()
    )

    return LaunchDescription(
        [arborist, simulation, navigation]
    )
