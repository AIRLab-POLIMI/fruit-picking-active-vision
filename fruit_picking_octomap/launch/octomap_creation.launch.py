from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('input_cloud_topic', default_value='/fruit_picking/pointcloud/pointcloud_processed'),
        DeclareLaunchArgument('reduced_input_cloud_topic', default_value='/fruit_picking/reduced_pointcloud/pointcloud_processed'),
        DeclareLaunchArgument('reduced_input_cloud_array_topic', default_value='/fruit_picking/reduced_pointcloud/pointcloud_array_processed'),
        DeclareLaunchArgument('output_confidence_vis', default_value='/confidence_vis'),
        DeclareLaunchArgument('output_semantic_class_vis', default_value='/semantic_class_vis'),
        DeclareLaunchArgument('resolution', default_value='0.02'),
        DeclareLaunchArgument('frame_id', default_value='igus_rebel_base_link'),
        DeclareLaunchArgument('base_frame_id', default_value='igus_rebel_base_link'),
        DeclareLaunchArgument('height_map', default_value='False'),
        DeclareLaunchArgument('colored_map', default_value='False'),
        DeclareLaunchArgument('color_factor', default_value='0.8'),
        DeclareLaunchArgument('filter_ground', default_value='False'),
        DeclareLaunchArgument('filter_speckles', default_value='False'),
        DeclareLaunchArgument('ground_filter/distance', default_value='0.04'),
        DeclareLaunchArgument('ground_filter/angle', default_value='0.15'),
        DeclareLaunchArgument('ground_filter/plane_distance', default_value='0.07'),
        DeclareLaunchArgument('compress_map', default_value='True'),
        DeclareLaunchArgument('incremental_2D_projection', default_value='False'),
        DeclareLaunchArgument('sensor_model/max_range', default_value='-1.0'),
        DeclareLaunchArgument('sensor_model/hit', default_value='0.7'),
        DeclareLaunchArgument('sensor_model/miss', default_value='0.4'),
        DeclareLaunchArgument('sensor_model/min', default_value='0.12'),
        DeclareLaunchArgument('sensor_model/max', default_value='0.97'),
        DeclareLaunchArgument('color/r', default_value='1.0'),
        DeclareLaunchArgument('color/g', default_value='1.0'),
        DeclareLaunchArgument('color/b', default_value='1.0'),
        DeclareLaunchArgument('color/a', default_value='1.0'),
        DeclareLaunchArgument('color_free/r', default_value='0.0'),
        DeclareLaunchArgument('color_free/g', default_value='0.0'),
        DeclareLaunchArgument('color_free/b', default_value='1.0'),
        DeclareLaunchArgument('color_free/a', default_value='1.0'),
        DeclareLaunchArgument('publish_free_space', default_value='False'),
        DeclareLaunchArgument('publish_confidence', default_value='False'),
        DeclareLaunchArgument('publish_semantic', default_value='False'),
        DeclareLaunchArgument('process_free_space', default_value='False'),
        DeclareLaunchArgument('pointcloud_array_subscription', default_value='False'),
        Node(
            package='fruit_picking_octomap',
            executable='extended_octomap_server',
            output='screen',
            remappings=[('cloud_in', LaunchConfiguration('input_cloud_topic')),
                        ('reduced_cloud_in', LaunchConfiguration('reduced_input_cloud_topic')),
                        ('reduced_cloud_array_in', LaunchConfiguration('reduced_input_cloud_array_topic')),
                        ('occupied_cells_vis_array', LaunchConfiguration('output_occupied_cells_vis')),
                        ('free_cells_vis_array', LaunchConfiguration('output_free_cells_vis')),
                        ('octomap_point_cloud_centers', LaunchConfiguration('output_occupied_cells_centers')),
                        ('octomap_binary', LaunchConfiguration('output_octomap_binary')),
                        ('octomap_full', LaunchConfiguration('output_octomap_full')),
                        ('projected_map', LaunchConfiguration('output_projected_map')),
                        ('confidence_vis_array', LaunchConfiguration('output_confidence_vis')),
                        ('semantic_class_vis_array', LaunchConfiguration('output_semantic_class_vis')),
                    ],
            parameters=[
                {'use_sim_time': LaunchConfiguration('use_sim_time'),
                'resolution': LaunchConfiguration('resolution'),
                'frame_id': LaunchConfiguration('frame_id'),
                'base_frame_id': LaunchConfiguration('base_frame_id'),
                'height_map': LaunchConfiguration('height_map'),
                'colored_map': LaunchConfiguration('colored_map'),
                'color_factor': LaunchConfiguration('color_factor'),
                'filter_ground': LaunchConfiguration('filter_ground'),
                'filter_speckles': LaunchConfiguration('filter_speckles'),
                'ground_filter/distance': LaunchConfiguration('ground_filter/distance'),
                'ground_filter/angle': LaunchConfiguration('ground_filter/angle'),
                'ground_filter/plane_distance': LaunchConfiguration('ground_filter/plane_distance'),
                'compress_map': LaunchConfiguration('compress_map'),
                'incremental_2D_projection': LaunchConfiguration('incremental_2D_projection'),
                'sensor_model/max_range': LaunchConfiguration('sensor_model/max_range'),
                'sensor_model/hit': LaunchConfiguration('sensor_model/hit'),
                'sensor_model/miss': LaunchConfiguration('sensor_model/miss'),
                'sensor_model/min': LaunchConfiguration('sensor_model/min'),
                'sensor_model/max': LaunchConfiguration('sensor_model/max'),
                'color/r': LaunchConfiguration('color/r'),
                'color/g': LaunchConfiguration('color/g'),
                'color/b': LaunchConfiguration('color/b'),
                'color/a': LaunchConfiguration('color/a'),
                'color_free/r': LaunchConfiguration('color_free/r'),
                'color_free/g': LaunchConfiguration('color_free/g'),
                'color_free/b': LaunchConfiguration('color_free/b'),
                'color_free/a': LaunchConfiguration('color_free/a'),
                'publish_free_space': LaunchConfiguration('publish_free_space'),
                'publish_confidence': LaunchConfiguration('publish_confidence'),
                'publish_semantic': LaunchConfiguration('publish_semantic'),
                'process_free_space': LaunchConfiguration('process_free_space'),
                'pointcloud_array_subscription': LaunchConfiguration('pointcloud_array_subscription'),}]
        )
    ])
