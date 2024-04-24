#pragma once
#ifndef _EXTENDED_OCTOMAP_SERVER_HPP_
#define _EXTENDED_OCTOMAP_SERVER_HPP_

#include <fruit_picking_octomap/octomap_server.hpp>
#include "fruit_picking_interfaces/msg/pointcloud_array.hpp"


namespace extended_octomap_server{

    enum semantic{
        none,
        tomato
    };
    
    class ExtendedOctomapData{
    
    public:

        ExtendedOctomapData(){
            this->confidence = 0.0;
            this->semantic_class = none;
            setConfidenceColor(0.0);
            setSemanticColor(none);
        }

        ExtendedOctomapData(semantic semantic_class){
            this->confidence = 0.0;
            this->semantic_class = semantic_class;
            setConfidenceColor(0.0);
            setSemanticColor(semantic_class);
        }
        
        ExtendedOctomapData(float confidence, semantic semantic_class){
            this->confidence = confidence;
            this->semantic_class = semantic_class;
            setConfidenceColor(confidence);
            setSemanticColor(semantic_class);
        }

        void setSemanticColor(semantic semantic_class){
            if (semantic_class == tomato){
                this->semantic_r = 1.0;
                this->semantic_g = 0.0;
                this->semantic_b = 0.0;
            }
            else if (semantic_class == none){
                this->semantic_r = 1.0;
                this->semantic_g = 1.0;
                this->semantic_b = 1.0;
            }
            this->semantic_a = 1.0;
        }

        void setConfidenceColor(float confidence){
            this->confidence_r = confidence;
            this->confidence_g = confidence;
            this->confidence_b = confidence;
            this->confidence_a = 1.0;
        }

        float confidence;
        semantic semantic_class;
        float semantic_r, semantic_g, semantic_b, semantic_a;
        float confidence_r, confidence_g, confidence_b, confidence_a;
    };



    typedef octomap::unordered_ns::unordered_map<octomap::OcTreeKey, ExtendedOctomapData, octomap::OcTreeKey::KeyHash> ExtendedOctomapMap;

    
    class ExtendedOctomapServer : public octomap_server::OctomapServer{

    protected:

        std::shared_ptr<message_filters::Subscriber<
                            sensor_msgs::msg::PointCloud2>> m_reducedPointCloudSub;
        std::shared_ptr<tf2_ros::MessageFilter<
                            sensor_msgs::msg::PointCloud2>> m_tfReducedPointCloudSub;
        std::shared_ptr<message_filters::Subscriber<
                            fruit_picking_interfaces::msg::PointcloudArray>> m_reducedPointCloudArraySub;
        std::shared_ptr<tf2_ros::MessageFilter<
                            fruit_picking_interfaces::msg::PointcloudArray>> m_tfReducedPointCloudArraySub;

        rclcpp::Publisher<visualization_msgs::msg::MarkerArray
                          >::SharedPtr confidenceMarkerPub;

        rclcpp::Publisher<visualization_msgs::msg::MarkerArray
                          >::SharedPtr semanticClassMarkerPub;

        std::shared_ptr<ExtendedOctomapMap> extended_octomap_map;

        octomap::KeySet global_free_cells, global_occupied_cells;

        bool m_processFreeSpace;
        bool publishConfidence;
        bool publishSemantic;
        bool pointcloudArraySubscription;

        virtual void onInit();        


        virtual void insertScan(
            const geometry_msgs::msg::Vector3  &sensorOrigin,
            const PCLPointCloud& ground,
            const PCLPointCloud& nonground);

        virtual void insertSemanticCallback(const sensor_msgs::msg::PointCloud2::ConstSharedPtr &reduced_cloud);
        virtual void insertSemanticArrayCallback(const fruit_picking_interfaces::msg::PointcloudArray::ConstSharedPtr &reduced_cloud_array);


        void publishConfidenceMarkers(const rclcpp::Time &) const;

        void publishSemanticClassMarkers(const rclcpp::Time &) const;


    public:

        explicit ExtendedOctomapServer(
            const rclcpp::NodeOptions &options,
            const std::string node_name = "extended_octomap_server");

        virtual ~ExtendedOctomapServer();

        virtual void insertCloudCallback(
            const sensor_msgs::msg::PointCloud2::ConstSharedPtr &);
        
    };

} // end namespace extended_octomap
#endif