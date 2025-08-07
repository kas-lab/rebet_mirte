from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.actions import Node
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.conditions import LaunchConfigurationEquals
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import EnvironmentVariable
import os


def generate_launch_description():
    which_world_arg = DeclareLaunchArgument(
        "which_world", default_value="empty", description="Which of the worlds to use e.g. robocupathome"
    )

    robocup_launch_file = os.path.join(get_package_share_directory("robocup_home_simulation"),
                                  "launch", "new_mirte_robocup.launch.py")
    gz_launch_file = os.path.join(get_package_share_directory("mirte_gazebo"),
                                  "launch", "mirte_simulation_fortress.launch.py")

    launch_files = os.path.join(get_package_share_directory("rebet_mirte"), "launch")


    empty_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(gz_launch_file),
        launch_arguments={}.items(),
        condition=LaunchConfigurationEquals("which_world", "empty")
    )
    robocup_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(robocup_launch_file),
        launch_arguments={}.items(),
        condition=LaunchConfigurationEquals("which_world", "robocupathome")
    )

    arborist = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(launch_files, "arborist_config_launch.py")
        )
    )



    start = Node(
        package="rebet_mirte",
        executable="tree_action_client.py",
        arguments=["ROAM"],
        parameters=[
            {
                'autostart': False,
            }
        ],
        prefix=EnvironmentVariable('REBET_TERMINAL_PREFIX'),
    )



    return LaunchDescription(
        [which_world_arg, empty_launch, robocup_launch, arborist, start]
    )
