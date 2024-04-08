// Copyright (c) 2008, Willow Garage, Inc.
// All rights reserved.
//
// Software License Agreement (BSD License 2.0)
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
//
//  * Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//  * Redistributions in binary form must reproduce the above
//    copyright notice, this list of conditions and the following
//    disclaimer in the documentation and/or other materials provided
//    with the distribution.
//  * Neither the name of the Willow Garage nor the names of its
//    contributors may be used to endorse or promote products derived
//    from this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
// FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
// COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
// INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
// BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
// ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.


#pragma once
#ifndef _REDUCED_POINTCLOUD_HPP_
#define _REDUCED_POINTCLOUD_HPP_

#include <functional>
#include <memory>
#include <mutex>
#include <string>

#include "depth_image_proc/visibility.h"
#include <depth_image_proc/conversions.hpp>
#include <depth_image_proc/point_cloud_xyzrgb.hpp>
#include "image_geometry/pinhole_camera_model.h"
#include "message_filters/subscriber.h"
#include "message_filters/synchronizer.h"
#include "message_filters/sync_policies/exact_time.h"
#include "message_filters/sync_policies/approximate_time.h"

#include <image_transport/image_transport.hpp>
#include <image_transport/subscriber_filter.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include "cv_bridge/cv_bridge.h"

#include "rclcpp_components/register_node_macro.hpp"


namespace reduced_pointcloud{
    
    class ReducedPointcloud : public rclcpp::Node{

    public:
        ReducedPointcloud(const rclcpp::NodeOptions& options);

    protected:

        using PointCloud2 = sensor_msgs::msg::PointCloud2;
        using Image = sensor_msgs::msg::Image;
        using CameraInfo = sensor_msgs::msg::CameraInfo;

        // Subscriptions
        image_transport::SubscriberFilter sub_depth_, sub_rgb_;
        message_filters::Subscriber<CameraInfo> sub_info_;
        using SyncPolicy = message_filters::sync_policies::ApproximateTime<Image, Image, CameraInfo>;
        using ExactSyncPolicy = message_filters::sync_policies::ExactTime<Image, Image, CameraInfo>;
        using Synchronizer = message_filters::Synchronizer<SyncPolicy>;
        using ExactSynchronizer = message_filters::Synchronizer<ExactSyncPolicy>;
        std::shared_ptr<Synchronizer> sync_;
        std::shared_ptr<ExactSynchronizer> exact_sync_;

        // Publications
        std::mutex connect_mutex_;
        rclcpp::Publisher<PointCloud2>::SharedPtr pub_point_cloud_;

        image_geometry::PinholeCameraModel model_;


        void connectCb();

        void imageCb(
            const Image::ConstSharedPtr & depth_msg,
            const Image::ConstSharedPtr & rgb_msg,
            const CameraInfo::ConstSharedPtr & info_msg);
        
        template<typename T>
        void convertDepth(
            const sensor_msgs::msg::Image::ConstSharedPtr & depth_msg,
            const sensor_msgs::msg::Image::ConstSharedPtr & rgb_msg,
            sensor_msgs::msg::PointCloud2::SharedPtr & cloud_msg,
            const image_geometry::PinholeCameraModel & model,
            double range_max = 0.0)
        {
            // Use correct principal point from calibration
            float center_x = model.cx();
            float center_y = model.cy();

            // Combine unit conversion (if necessary) with scaling by focal length for computing (X,Y)
            double unit_scaling = depth_image_proc::DepthTraits<T>::toMeters(T(1) );
            float constant_x = unit_scaling / model.fx();
            float constant_y = unit_scaling / model.fy();
            float bad_point = std::numeric_limits<float>::quiet_NaN();

            sensor_msgs::PointCloud2Iterator<float> iter_x(*cloud_msg, "x");
            sensor_msgs::PointCloud2Iterator<float> iter_y(*cloud_msg, "y");
            sensor_msgs::PointCloud2Iterator<float> iter_z(*cloud_msg, "z");
            const T * depth_row = reinterpret_cast<const T *>(&depth_msg->data[0]);
            const uint8_t * rgb_row = &rgb_msg->data[0]; // It obtain the RGB data from the input rgb topic
            int row_step = depth_msg->step / sizeof(T);
            for (int v = 0; v < static_cast<int>(cloud_msg->height); ++v, depth_row += row_step, rgb_row += rgb_msg->step) { // it iterates also through the rgb data
                for (int u = 0; u < static_cast<int>(cloud_msg->width); ++u, ++iter_x, ++iter_y, ++iter_z) {
                T depth = depth_row[u];

                // Get the RGB values
                uint8_t r = rgb_row[u * 3];
                uint8_t g = rgb_row[u * 3 + 1];
                uint8_t b = rgb_row[u * 3 + 2];


                // Check if the RGB value is white (assuming 255,255,255 is white)
                if (r == 255 && g == 255 && b == 255) {
                    continue; // Skip this point
                }

                // Missing points denoted by NaNs
                if (!depth_image_proc::DepthTraits<T>::valid(depth)) {
                    if (range_max != 0.0) {
                    depth = depth_image_proc::DepthTraits<T>::fromMeters(range_max);
                    } else {
                    *iter_x = *iter_y = *iter_z = bad_point;
                    continue;
                    }
                }

                // Fill in XYZ
                *iter_x = (u - center_x) * depth * constant_x;
                *iter_y = (v - center_y) * depth * constant_y;
                *iter_z = depth_image_proc::DepthTraits<T>::toMeters(depth);
                }
            }
        }

    };
    

} // end namespace extended_octomap
#endif