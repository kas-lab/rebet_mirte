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
from nav2_common.launch import ReplaceString


def generate_launch_description():
    launch_config_arg = DeclareLaunchArgument(
        "config", default_value="dev", description="Which config to use: 'dev' or 'frog'"
    )
    # launch_yolo_arg = DeclareLaunchArgument(
    #     "yolo", default_value="true", description="Also launch the yolo node or not"
    # )

    launch_files = os.path.join(get_package_share_directory("rebet_mirte"), "launch")
    config_files = os.path.join(get_package_share_directory("rebet_mirte"), "config")
    schema_files = os.path.join(get_package_share_directory("typedb_tactics"), "schemas")


    dev_config_file = os.path.join(
        config_files,
        'adaptation_engine_config_dev.yaml'
    )

    frog_config_file = os.path.join(
        config_files,
        'adaptation_engine_config_frog.yaml'
    )

    aal = Node(
        package='aal',
        executable='adaptation_layer',
        prefix=EnvironmentVariable('REBET_TERMINAL_PREFIX'),
        name='adaptation_layer_node',
    )

    arborist = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(launch_files, "arborist_config_launch.py")
        )
    )

    typedb = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(get_package_share_directory("typedb_tactics"), "launch",
                         "tactical_retreat_kb.launch.py")
        ),
        launch_arguments={
            "schema_path": f"[{os.path.join(schema_files, 'data_structure', 'data_structure.tql')}, \
                              {os.path.join(schema_files, 'context_model', 'context_model.tql')}, \
                              {os.path.join(schema_files, 'ros_model', 'ros_model.tql')}, \
                              {os.path.join(schema_files, 'logical_expressions', 'logical_expression.tql')}, \
                              {os.path.join(schema_files, 'feature_model', 'feature_model.tql')}, \
                              {os.path.join(schema_files, 'feature_model', 'feature_model_logical_expression.tql')}, \
                              {os.path.join(schema_files, 'tactics_model', 'tactics_model.tql')}, \
                              {os.path.join(schema_files, 'discover_tactics_model', 'discover_tactics_model.tql')}, \
                              {os.path.join(schema_files, 'relaxed', 'relaxed_model.tql')}]",
            # "data_path": f"[{os.path.join(config_files, 'insert_measurement.tql')}]",
            "force_database": "True",
            "force_data": "True",
        }.items(),
    )

    xtext_dir = config_files = os.path.join(get_package_share_directory("rebet_mirte"), "xtext")

    dev_config_file = ReplaceString(
        source_file=dev_config_file,
        replacements={
            "<rebet_mirte_xtext_dir>": (
                xtext_dir
            )
        },
    )

    frog_config_file = ReplaceString(
        source_file=frog_config_file,
        replacements={
            "<rebet_mirte_xtext_dir>": (
                xtext_dir
            )
        },
    )

    frog_adap_engine = Node(
        package="rebet_java",
        executable="adaptation_engine",
        output="screen",
        parameters=[frog_config_file],
        condition=LaunchConfigurationEquals("config", "frog"),
    )

    dev_adap_engine = Node(
        package="rebet_java",
        executable="adaptation_engine",
        output="screen",
        parameters=[dev_config_file],
        condition=LaunchConfigurationEquals("config", "dev"),
    )

    delay_adap_engine = TimerAction(
        period=2.0,  # Delay for 5 seconds
        actions=[frog_adap_engine, dev_adap_engine],
    )

    return LaunchDescription(
        [launch_config_arg, typedb, delay_adap_engine, aal]
        # [typedb, delay_adap_engine, aal, context_model]
        # [typedb, delay_adap_engine, aal, context_model] #, arborist, ]
    )
