#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class ParkingModeRouter(Node):

    def __init__(self):
        super().__init__('parking_mode_router')

        self.declare_parameter('mode_topic', '/drive_mode')
        self.declare_parameter('auto_trigger', False)

        self.mode_topic = str(
            self.get_parameter('mode_topic').value
        )
        self.auto_trigger = bool(
            self.get_parameter('auto_trigger').value
        )

        self.service_clients = {
            't_start': self.create_client(
                Trigger, '/t_parking/start'),
            't_cancel': self.create_client(
                Trigger, '/t_parking/cancel'),
            'p_start': self.create_client(
                Trigger, '/parallel_parking/start'),
            'p_cancel': self.create_client(
                Trigger, '/parallel_parking/cancel'),
        }

        self.current_mode = ''
        self.pending = None

        self.create_subscription(
            String,
            self.mode_topic,
            self._mode_cb,
            10
        )

        self.create_timer(0.2, self._retry)

        self.get_logger().info(
            f'parking router ready: mode={self.mode_topic}, '
            f'auto_trigger={self.auto_trigger}'
        )

    def _mode_cb(self, msg):
        new_mode = str(msg.data).strip()

        if new_mode == self.current_mode:
            return

        old_mode = self.current_mode
        self.current_mode = new_mode

        if not self.auto_trigger:
            return

        if old_mode == '7':
            self._request('t_cancel')

        if old_mode == '10':
            self._request('p_cancel')

        if new_mode == '7':
            self._request('t_start')

        elif new_mode == '10':
            self._request('p_start')

    def _request(self, key):
        self.pending = key
        self._retry()

    def _retry(self):
        if self.pending is None:
            return

        key = self.pending
        client = self.service_clients[key]

        if not client.service_is_ready():
            return

        self.pending = None

        future = client.call_async(Trigger.Request())
        future.add_done_callback(
            lambda f, k=key: self._done(k, f)
        )

    def _done(self, key, future):
        try:
            result = future.result()
            self.get_logger().info(
                f'{key}: success={result.success} '
                f'message={result.message}'
            )
        except Exception as exc:
            self.get_logger().error(
                f'{key} service failed: {exc}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = ParkingModeRouter()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
