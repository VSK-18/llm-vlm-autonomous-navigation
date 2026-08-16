#!/usr/bin/env python3
"""
depth_visualizer.py
===================
A standalone ROS 2 node to subscribe to a 32FC1 depth image,
process it, and publish an 8-bit (mono8) grayscale image for easy visualization.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np

class DepthVisualizer(Node):
    def __init__(self):
        super().__init__('depth_visualizer')
        
        # Declare configurable depth range parameters
        self.declare_parameter('min_depth', 0.25)
        self.declare_parameter('max_depth', 6.67)
        
        # Subscribe to the original depth camera topic
        self.subscription = self.create_subscription(
            Image,
            '/depth_camera/depth',
            self.depth_callback,
            10
        )
        
        # Publisher for the 8-bit visualized depth image
        self.publisher = self.create_publisher(
            Image,
            '/depth_camera/depth_visualized',
            10
        )
        
        self.bridge = CvBridge()
        self.get_logger().info('Depth Visualizer Node Started.')
        self.get_logger().info('Subscribed to: /depth_camera/depth')
        self.get_logger().info('Publishing to: /depth_camera/depth_visualized')

    def depth_callback(self, msg):
        try:
            # 1. Retrieve the parameters
            min_depth = self.get_parameter('min_depth').get_parameter_value().double_value
            max_depth = self.get_parameter('max_depth').get_parameter_value().double_value
            
            # 2. Convert ROS Image msg to OpenCV numpy array (encoding: 32FC1)
            depth_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
            
            # 3. Handle NaN and Inf values
            # Map NaNs and positive infinity to max_depth, negative infinity to min_depth
            depth_clean = np.nan_to_num(depth_img, nan=max_depth, posinf=max_depth, neginf=min_depth)
            
            # 4. Clip values to [min_depth, max_depth] range
            depth_clipped = np.clip(depth_clean, min_depth, max_depth)
            
            # 5. Normalize/Scale to 8-bit range [0, 255]
            # (val - min_depth) / (max_depth - min_depth) * 255.0
            depth_normalized = ((depth_clipped - min_depth) / (max_depth - min_depth) * 255.0)
            
            # Convert to uint8
            depth_mono8 = depth_normalized.astype(np.uint8)
            
            # Invert values so closer obstacles are brighter (white) and far away space is darker (black)
            depth_mono8 = 255 - depth_mono8
            
            # 6. Convert OpenCV image back to ROS Image message with mono8 encoding
            output_msg = self.bridge.cv2_to_imgmsg(depth_mono8, encoding='mono8')
            
            # Copy original header to preserve timestamps and frame_id
            output_msg.header = msg.header
            
            # 7. Publish the visualized image
            self.publisher.publish(output_msg)
            
        except Exception as e:
            self.get_logger().error(f'Failed to visualize depth image: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = DepthVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
