import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as SensorImage
from cv_bridge import CvBridge
from std_msgs.msg import String
import json

import cv2
from lang_sam import LangSAM
from PIL import Image
import torch
import numpy as np

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rosgraph_msgs.msg import Clock
from diagnostic_msgs.msg import KeyValue

from fruit_picking_segmentation_lang_sam.utils import merge_masks_images, convert_masks_to_images, rgba_to_rgb_with_white_background

from fruit_picking_interfaces.msg import ImageArray, Confidence



class LANGSAMPubSub(Node):

    def __init__(self):
        super().__init__('lang_sam_pub_sub')
        
        # Create bridge between cv2 images and sensor_msgs/Image type
        self.bridge = CvBridge()



        # Load parameters
        self.declare_parameters(
            namespace="",
            parameters=[
                ("model_type", "vit_h"),
                ("input_image_topic", "/virtual_camera_link/rgbd_camera/image_raw"),
                ("output_image_topic", "/fruit_picking/segmentation/lang_sam/image"),
                ("output_image_array_topic", "/fruit_picking/segmentation/lang_sam/image_array"),
                ("output_boxes_topic", "/fruit_picking/segmentation/lang_sam/boxes"),
                ("output_confidences_topic", "/fruit_picking/segmentation/lang_sam/confidences"),
                ("segmentation_prompt", "tomato"),
            ],
        )

        self._sam_model_type = self.get_parameter("model_type").value
        self._input_image_topic = self.get_parameter("input_image_topic").value
        self._output_image_topic = self.get_parameter("output_image_topic").value
        self._output_image_array_topic = self.get_parameter("output_image_array_topic").value
        self._output_boxes_topic = self.get_parameter("output_boxes_topic").value
        self._output_confidences_topic = self.get_parameter("output_confidences_topic").value
        self._lang_sam_segmentation_prompt = self.get_parameter("segmentation_prompt").value




    
        # Load LANG SAM model
        self.get_logger().info(
            f"[INIT] Loading LANG SAM model '{self._sam_model_type}'. This may take some time..."
        )

        self._lang_sam = LangSAM(
            self._sam_model_type,
        )

        self.get_logger().info("[INIT] LANG SAM model loaded.")




        # Define callback groups for multi-threading
        clock_subscriber_group = MutuallyExclusiveCallbackGroup()
        segment_group = MutuallyExclusiveCallbackGroup()


        # Define image subscriber and segmentation callback
        self.subscription = self.create_subscription(
            SensorImage, self._input_image_topic, self.segment, 10, callback_group=segment_group)


        # Define image, image array, boxes and confidences publishers
        self.image_publisher = self.create_publisher(SensorImage, self._output_image_topic, 10)
        self.image_array_publisher = self.create_publisher(ImageArray, self._output_image_array_topic, 10)
        self.boxes_publisher = self.create_publisher(String, self._output_boxes_topic, 10)
        self.confidences_publisher = self.create_publisher(Confidence, self._output_confidences_topic, 10)
    

        # Initialize clock subscriber
        self.clock_subscriber = self.create_subscription(Clock, '/clock', self.clock_sub, 10, callback_group=clock_subscriber_group)

        self.get_logger().info(f'[INIT] Pub-Sub client is ready.')






    def clock_sub(self, msg):
        pass



    def publish_image_segmentation(self, image_msg):
        self.image_publisher.publish(image_msg)
        self.get_logger().info('[Image-pub] Image published.')



    def publish_image_array_segmentation(self, image_array_msg):
        self.image_array_publisher.publish(image_array_msg)
        self.get_logger().info('[ImageArray-pub] Image array published.')



    def publish_boxes_segmentation(self, boxes, masks_names):
        # Convert boxes tensor in list of lists and publish as a json string, together with a header
        boxes = boxes.tolist()
        boxes_dict = dict(zip(masks_names, boxes))
        boxes_json_str = json.dumps(boxes_dict)  # Serialize dictionary to JSON string
        msg_boxes = String()
        msg_boxes.data = boxes_json_str # to deserialize: confidences_dict = json.loads(confidences_json_str)

        self.boxes_publisher.publish(msg_boxes)
        self.get_logger().info('[Boxes-pub] Boxes published.')



    def publish_confidences_segmentation(self, confidences, masks_names, frame_id, stamp):
        # Convert confidences tensor in list of float rounded at the 3rd digit and 
        confidences = [round(logit.item(), 3) for logit in confidences]

        confidences_dict = dict(zip(masks_names, confidences))
        msg_confidences = Confidence()
        msg_confidences.data = [KeyValue(key=k, value=str(v)) for k, v in confidences_dict.items()] 
        msg_confidences.header.frame_id = frame_id
        msg_confidences.header.stamp = stamp

        self.confidences_publisher.publish(msg_confidences)
        self.get_logger().info('[Confidences-pub] Confidences published.')   
    



    def segment(self, msg):

        # Get input image from input topic, and size
        self.get_logger().info('------------------------------------------------')
        self.get_logger().info('[LANG-SAM] Original image received.')
        self.original_image = msg



        # Format input image from sensor_msgs/Image to cv2 format
        img = cv2.cvtColor(self.bridge.imgmsg_to_cv2(self.original_image), cv2.COLOR_BGR2RGB)
        img_query = Image.fromarray(img) # from OpenCv to PIL image
        img_shape = img.shape



        # Get prompt
        text_prompt_query = self._lang_sam_segmentation_prompt



        # Segmentation
        start_seg = self.get_clock().now().nanoseconds

        self.get_logger().info(
            f"[LANG-SAM] Segmenting image of shape {img_shape} with text prompt prior: {text_prompt_query}..."
        )
        self.get_logger().info(
            f"[LANG-SAM] Inference starting time: {start_seg}."
        )

        masks, boxes, phrases, confidences = self._lang_sam.predict(img_query, text_prompt_query)

        end_seg = self.get_clock().now().nanoseconds

        self.get_logger().info(
            f"[LANG-SAM] Segmentation completed in {round((end_seg - start_seg)/1.e9, 5)}s."
        )




        # Start publishing phase

        # Set the initial time of this phase
        start_pub = self.get_clock().now().nanoseconds
        start_pub_stamp = self.get_clock().now().to_msg()

    
        # Check number of masks found
        self.get_logger().info(
            f"[LANG-SAM] Masks found: {masks.size(0)}."
        )

        # Declare a new ImageArray object
        mask_images_array = ImageArray()
        mask_images_array.header.frame_id = self.original_image.header.frame_id
        mask_images_array.header.stamp = start_pub_stamp


        # Case when the model did not segment any mask, thus the result is a null image
        if masks.size(0) <= 0:
            empty_image = np.ones((img_shape[0], img_shape[1], 3), dtype=np.uint8) * 255
            empty_image = cv2.cvtColor(empty_image, cv2.COLOR_BGR2RGB)
            empty_image = self.bridge.cv2_to_imgmsg(empty_image, encoding="rgb8")
            empty_image.header.frame_id = self.original_image.header.frame_id
            empty_image.header.stamp = start_pub_stamp
            # Append the white image inside the images array
            mask_images_array.images.append(empty_image)

            # Define image publisher and publish
            self.get_logger().info(f'[Image-pub] Publishing empty image...')
            self.publish_image_segmentation(empty_image)

            # Define image array publisher and publish
            self.get_logger().info(f'[ImageArray-pub] Publishing empty images array...')
            self.publish_image_array_segmentation(mask_images_array)

            # Publish boxes and confidences as empty lists
            self.get_logger().info(f'[Boxes-pub] Publishing empty boxes...')
            self.publish_boxes_segmentation(torch.empty_like(torch.tensor([])), [])
            self.get_logger().info(f'[Confidences-pub] Publishing empty confidences...')
            self.publish_confidences_segmentation(torch.empty_like(torch.tensor([])), [], self.original_image.header.frame_id, start_pub_stamp)
            
            

        # Case when the model segmented some masks
        else:

            masks_names = [f"mask_{i}" for i in range(1, masks.size(0) + 1)]

            # Prepare merged masks images to be published
            # Convert bool masks tensor to cv2 images
            masks_images = convert_masks_to_images(masks)


            # Publish boxes and confidences
            self.get_logger().info(f'[Boxes-pub] Publishing boxes...')
            self.publish_boxes_segmentation(boxes, masks_names)
            self.get_logger().info(f'[Confidences-pub] Publishing confidences...')
            self.publish_confidences_segmentation(confidences, masks_names, self.original_image.header.frame_id, start_pub_stamp)


            # Image array publication
            for i, mask_image in enumerate(masks_images):
                mask_image = rgba_to_rgb_with_white_background(mask_image)
                # mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)
                mask_image = np.uint8(mask_image * 255 * 255) # in order to visualize the color image for RViz and also for the exported image

                # In order to visualize in Rviz, the image need to be processed more
                mask_image = cv2.convertScaleAbs(mask_image)
                mask_image = self.bridge.cv2_to_imgmsg(mask_image, encoding="rgb8")
                mask_image.header.frame_id = self.original_image.header.frame_id
                mask_image.header.stamp = start_pub_stamp

                # Add each image in the ImageArray object
                mask_images_array.images.append(mask_image)
            self.get_logger().info(f'[ImageArray-pub] Publishing images array...')
            self.publish_image_array_segmentation(mask_images_array)


            # Merged masks publication  
            merged_masks_images = merge_masks_images(masks_images)
            merged_masks_images = rgba_to_rgb_with_white_background(merged_masks_images)
            # merged_masks_images = cv2.cvtColor(merged_masks_images, cv2.COLOR_BGR2RGB)
            merged_masks_images = np.uint8(merged_masks_images * 255 * 255) # in order to visualize the color image for RViz and also for the exported image

            # In order to visualize in Rviz, the image need to be processed more
            merged_masks_images = cv2.convertScaleAbs(merged_masks_images)
            merged_masks_images = self.bridge.cv2_to_imgmsg(merged_masks_images, encoding="rgb8")
            merged_masks_images.header.frame_id = self.original_image.header.frame_id
            merged_masks_images.header.stamp = start_pub_stamp

            # Define image publisher and publish
            self.get_logger().info(f'[Image-pub] Publishing merged masks image...')
            self.publish_image_segmentation(merged_masks_images)



        self.get_logger().info(
            f"[Pub] From the received moment, data published in {round((self.get_clock().now().nanoseconds - start_pub)/1.e9, 5)}s."
        )



def main(args=None):

    # Init of the node
    rclpy.init(args=args)
    node = LANGSAMPubSub()

    # Creation of the multi thread executor for the node
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    # Spin the executor
    executor.spin()

    # Terminate
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()