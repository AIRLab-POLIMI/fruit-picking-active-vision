from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    return LaunchDescription([
        # Topic arguments
        DeclareLaunchArgument('pointcloud_topic', default_value='/pointcloud'),
        DeclareLaunchArgument('segmented_pointcloud_topic', default_value='/segmented_pointcloud'),
        DeclareLaunchArgument('segmented_pointclouds_array_topic', default_value='/segmented_pointclouds_array'),
        DeclareLaunchArgument('octomap_occupied_cells_vis_topic', default_value='/octomap_occupied_cells_vis'),
        DeclareLaunchArgument('octomap_free_cells_vis_topic', default_value='/octomap_free_cells_vis'),
        DeclareLaunchArgument('octomap_occupied_cells_centers_pointcloud_topic', default_value='/octomap_occupied_cells_centers_pointcloud'),
        DeclareLaunchArgument('octomap_binary_topic', default_value='octomap_binary'),
        DeclareLaunchArgument('octomap_full_topic', default_value='octomap_full'),
        DeclareLaunchArgument('octomap_projected_map_topic', default_value='octomap_projected_map'),    
        DeclareLaunchArgument('octomap_semantic_class_cells_vis_topic', default_value='/octomap_semantic_class_cells_vis'),
        DeclareLaunchArgument('octomap_confidence_cells_vis_topic', default_value='/octomap_confidence_cells_vis_topic'),
        DeclareLaunchArgument('octomap_instances_cells_vis_topic', default_value='/octomap_instances_cells_vis_topic'),

        # Octomap parameters arguments
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
        DeclareLaunchArgument('pointcloud_min_x', default_value=str(float('-inf'))),  # Approximation of -std::numeric_limits<double>::max()
        DeclareLaunchArgument('pointcloud_max_x', default_value=str(float('inf'))),  # Approximation of std::numeric_limits<double>::max()
        DeclareLaunchArgument('pointcloud_min_y', default_value=str(float('-inf'))),  # Approximation of -std::numeric_limits<double>::max()
        DeclareLaunchArgument('pointcloud_max_y', default_value=str(float('inf'))), # Approximation of std::numeric_limits<double>::max()
        DeclareLaunchArgument('pointcloud_min_z', default_value=str(float('-inf'))),  # Approximation of -std::numeric_limits<double>::max()
        DeclareLaunchArgument('pointcloud_max_z', default_value=str(float('inf'))),  # Approximation of std::numeric_limits<double>::max()
        DeclareLaunchArgument('color/r', default_value='1.0'),
        DeclareLaunchArgument('color/g', default_value='1.0'),
        DeclareLaunchArgument('color/b', default_value='1.0'),
        DeclareLaunchArgument('color/a', default_value='1.0'),
        DeclareLaunchArgument('color_free/r', default_value='0.0'),
        DeclareLaunchArgument('color_free/g', default_value='0.0'),
        DeclareLaunchArgument('color_free/b', default_value='1.0'),
        DeclareLaunchArgument('color_free/a', default_value='1.0'),
        DeclareLaunchArgument('process_free_space', default_value='False'),
        DeclareLaunchArgument('publish_free_space', default_value='False'),
        DeclareLaunchArgument('publish_octomap_binary', default_value='False'),
        DeclareLaunchArgument('publish_octomap_full', default_value='False'),
        DeclareLaunchArgument('publish_centers_pointcloud', default_value='False'),
        DeclareLaunchArgument('publish_2d_projected_map', default_value='False'),
        DeclareLaunchArgument('publish_semantic', default_value='False'),
        DeclareLaunchArgument('publish_confidence', default_value='False'),
        DeclareLaunchArgument('publish_instances', default_value='False'),
        DeclareLaunchArgument('semantic_pointcloud_subscription', default_value='False'),
        DeclareLaunchArgument('semantic_pointclouds_array_subscription', default_value='False'),
        DeclareLaunchArgument('message_filter_queue', default_value='5'),
        DeclareLaunchArgument('insert_cloud_init', default_value='True'),
        DeclareLaunchArgument('insert_semantic_init', default_value='True'),


        Node(
            package='fruit_picking_octomap',
            executable='extended_octomap_server',
            output='screen',
            arguments= [
                "--ros-args",
                "--log-level",
                "extended_octomap_server:=debug",
            ],
            remappings=[('cloud_in', LaunchConfiguration('pointcloud_topic')),
                        ('segmented_pointcloud', LaunchConfiguration('segmented_pointcloud_topic')),
                        ('segmented_pointclouds_array', LaunchConfiguration('segmented_pointclouds_array_topic')),
                        ('occupied_cells_vis_array', LaunchConfiguration('octomap_occupied_cells_vis_topic')),
                        ('free_cells_vis_array', LaunchConfiguration('octomap_free_cells_vis_topic')),
                        ('octomap_point_cloud_centers', LaunchConfiguration('octomap_occupied_cells_centers_pointcloud_topic')),
                        ('octomap_binary', LaunchConfiguration('octomap_binary_topic')),
                        ('octomap_full', LaunchConfiguration('octomap_full_topic')),
                        ('projected_map', LaunchConfiguration('octomap_projected_map_topic')),
                        ('semantic_class_cells_vis', LaunchConfiguration('octomap_semantic_class_cells_vis_topic')),
                        ('confidence_cells_vis', LaunchConfiguration('octomap_confidence_cells_vis_topic')),
                        ('instances_cells_vis', LaunchConfiguration('octomap_instances_cells_vis_topic')),
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
                'pointcloud_min_x': LaunchConfiguration('pointcloud_min_x'),
                'pointcloud_max_x': LaunchConfiguration('pointcloud_max_x'),
                'pointcloud_min_y': LaunchConfiguration('pointcloud_min_y'),
                'pointcloud_max_y': LaunchConfiguration('pointcloud_max_y'),
                'pointcloud_min_z': LaunchConfiguration('pointcloud_min_z'),
                'pointcloud_max_z': LaunchConfiguration('pointcloud_max_z'),
                'color/r': LaunchConfiguration('color/r'),
                'color/g': LaunchConfiguration('color/g'),
                'color/b': LaunchConfiguration('color/b'),
                'color/a': LaunchConfiguration('color/a'),
                'color_free/r': LaunchConfiguration('color_free/r'),
                'color_free/g': LaunchConfiguration('color_free/g'),
                'color_free/b': LaunchConfiguration('color_free/b'),
                'color_free/a': LaunchConfiguration('color_free/a'),
                'process_free_space': LaunchConfiguration('process_free_space'),
                'publish_free_space': LaunchConfiguration('publish_free_space'),
                'publish_octomap_binary': LaunchConfiguration('publish_octomap_binary'),
                'publish_octomap_full': LaunchConfiguration('publish_octomap_full'),
                'publish_centers_pointcloud': LaunchConfiguration('publish_centers_pointcloud'),
                'publish_2d_projected_map': LaunchConfiguration('publish_2d_projected_map'),
                'publish_semantic': LaunchConfiguration('publish_semantic'),
                'publish_confidence': LaunchConfiguration('publish_confidence'),
                'publish_instances': LaunchConfiguration('publish_instances'),
                'semantic_pointcloud_subscription': LaunchConfiguration('semantic_pointcloud_subscription'),
                'semantic_pointclouds_array_subscription': LaunchConfiguration('semantic_pointclouds_array_subscription'),
                'message_filter_queue': LaunchConfiguration('message_filter_queue'),
                'insert_cloud_init': LaunchConfiguration('insert_cloud_init'),
                'insert_semantic_init': LaunchConfiguration('insert_semantic_init'),
                }]
        )
    ])
