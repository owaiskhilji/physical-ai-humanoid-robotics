# Chapter 2: The Robotic Nervous System (ROS 2 Fundamentals)

## ROS 2 architecture and core concepts

ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It's designed for modern robotics challenges, including multi-robot systems, real-time control, and embedded systems.

### Core Concepts:

*   **Nodes**: Executable processes that perform computation (e.g., a camera driver node, a motor control node).
*   **Topics**: A publish/subscribe messaging system. Nodes publish data (e.g., sensor readings, motor commands) to topics, and other nodes subscribe to those topics to receive the data.
*   **Services**: A request/reply communication mechanism. A client node sends a request to a service-providing node, which performs an action and sends back a response.
*   **Actions**: Similar to services but for long-running tasks. An action client sends a goal to an action server, which provides feedback as the goal is processed and eventually sends a result.
*   **Parameters**: Dynamic configuration values for nodes. Nodes can expose parameters that can be changed at runtime.
*   **Messages**: Data structures used for communication over topics, services, and actions.
*   **Packages**: The fundamental unit of ROS 2 software organization, containing nodes, libraries, message definitions, and other resources.
*   **Workspaces**: Directories where ROS 2 packages are organized, built, and installed.

## ROS 2 Nodes, Topics, Services, and Actions

These are the fundamental communication mechanisms in ROS 2, enabling different parts of a robot system to interact.

### Nodes

As mentioned, nodes are individual processes that perform computation. For example, a robot might have a node for reading lidar data, another for controlling motors, and another for path planning.

### Topics (Publish/Subscribe)

Topics are a unidirectional streaming communication method. A node *p_ublishes* messages to a topic, and any number of other nodes can *subscribe* to that topic to receive those messages. This is ideal for continuous data streams like sensor readings, joint states, or camera feeds.

```python
# Example: Publisher Node (simplified)
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```python
# Example: Subscriber Node (simplified)
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Services (Request/Reply)

Services are used for one-shot, request-reply interactions. A client sends a request and waits for a response. This is suitable for operations like triggering an action or querying data that doesn't change frequently.

```python
# Example: Service Server (simplified)
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Incoming request: a: {request.a} b: {request.b}')
        return response

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    minimal_service.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```python
# Example: Service Client (simplified)
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(2, 3)
    minimal_client.get_logger().info(f'Result of add_two_ints: {response.sum}')
    minimal_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Actions (Goals with Feedback)

Actions are built on topics and services, providing a more complex communication pattern for long-running, interruptible tasks. An action client sends a goal, receives continuous feedback, and eventually a final result. This is suitable for tasks like moving a robot to a target pose or performing a pick-and-place operation.

```python
# Example: Action Server (simplified)
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class MinimalActionServer(Node):
    def __init__(self):
        super().__init__('minimal_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            feedback_msg.sequence.append(feedback_msg.sequence[i] + feedback_msg.sequence[i-1])
            self.get_logger().info(f'Feedback: {feedback_msg.sequence}')
            goal_handle.publish_feedback(feedback_msg)
            # time.sleep(1) # Simulate long-running task

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        return result

def main(args=None):
    rclpy.init(args=args)
    minimal_action_server = MinimalActionServer()
    rclpy.spin(minimal_action_server)

if __name__ == '__main__':
    main()
```

```python
# Example: Action Client (simplified)
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class MinimalActionClient(Node):
    def __init__(self):
        super().__init__('minimal_action_client')
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f'Received feedback: {feedback_msg.feedback.sequence}')

def main(args=None):
    rclpy.init(args=args)
    action_client = MinimalActionClient()
    action_client.send_goal(10)
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
```

## Bridging Python Agents to ROS controllers using rclpy

`rclpy` is the Python client library for ROS 2, allowing Python developers to write ROS 2 nodes and interact with the ROS 2 ecosystem. It provides a straightforward way to create nodes, publish/subscribe to topics, call/provide services, and interact with actions.

### Key `rclpy` concepts:

*   **`rclpy.init()` and `rclpy.shutdown()`**: Initialize and deinitialize the ROS 2 client library.
*   **`rclpy.create_node()`**: Creates a new ROS 2 node.
*   **`Node.create_publisher()`**: Creates a publisher to send messages to a topic.
*   **`Node.create_subscription()`**: Creates a subscriber to receive messages from a topic.
*   **`Node.create_service()`**: Creates a service server to handle requests.
*   **`Node.create_client()`**: Creates a service client to send requests.
*   **`Node.create_action_server()`**: Creates an action server.
*   **`Node.create_action_client()`**: Creates an action client.
*   **`rclpy.spin()` and `rclpy.spin_once()`**: Process ROS 2 events (callbacks, messages) synchronously. `spin()` blocks until the node is shut down, `spin_once()` processes events once.
*   **`Executor`**: For more advanced multi-threaded or multi-node spinning, executors can be used.

Integrating Python agents with ROS 2 controllers typically involves:

1.  **Agent Logic**: Your Python agent (e.g., an AI planning agent, a high-level behavior controller) determines what actions the robot should take.
2.  **ROS 2 Interface**: Use `rclpy` within your agent to translate these high-level commands into ROS 2 messages (e.g., publishing to a `/cmd_vel` topic for movement, calling a `/set_gripper_position` service).
3.  **ROS 2 Controllers**: The robot's low-level controllers (often written in C++ for performance, but can also be Python) subscribe to these topics or provide these services/actions to execute the commands.

This modular approach allows the Python agent to focus on decision-making, while ROS 2 handles reliable communication and interaction with hardware.

## Building ROS 2 packages with Python

Building ROS 2 packages in Python typically involves using `ament_python` with `colcon` as the build tool.

### Key steps:

1.  **Create a Workspace**: Organize your ROS 2 packages within a `colcon` workspace.
    ```bash
    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws/src
    ```

2.  **Create a Python Package**: Use `ros2 pkg create` to generate a basic package structure.
    ```bash
    ros2 pkg create --build-type ament_python my_python_pkg
    ```

3.  **Define `setup.py`**: This file is crucial for Python packages and tells `colcon` how to build and install your package. It should define entry points for your executables.
    ```python
    # my_python_pkg/setup.py
    from setuptools import setup

    package_name = 'my_python_pkg'

    setup(
        name=package_name,
        version='0.0.0',
        packages=[package_name],
        data_files=[
            ('share/' + package_name, ['package.xml']),
            ('share/' + package_name + '/resource', ['resource/' + package_name]),
        ],
        install_requires=['setuptools'],
        zip_safe=True,
        maintainer='your_name',
        maintainer_email='your_email@example.com',
        description='TODO: Package description',
        license='TODO: License declaration',
        tests_require=['pytest'],
        entry_points={
            'console_scripts': [
                'my_node = my_python_pkg.my_node:main',
            ],
        },
    )
    ```

4.  **Create `package.xml`**: Describes your package, its dependencies, and other metadata.
    ```xml
    <!-- my_python_pkg/package.xml -->
    <?xml version="1.0"?>
    <?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
    <package format="3">
      <name>my_python_pkg</name>
      <version>0.0.0</version>
      <description>TODO: Package description</description>
      <maintainer email="user@todo.todo">user</maintainer>
      <license>TODO: License declaration</license>

      <depend>rclpy</depend>
      <depend>std_msgs</depend>

      <test_depend>pytest</test_depend>

      <export>
        <build_type>ament_python</build_type>
      </export>
    </package>
    ```

5.  **Write your Python Node**: Place your node's Python code (e.g., `my_node.py`) inside the `my_python_pkg` directory.

6.  **Build the Workspace**: Navigate to your workspace root (`~/ros2_ws/`) and run `colcon build`.
    ```bash
    cd ~/ros2_ws/
    colcon build
    ```

7.  **Source the Setup Files**: After building, you need to source the `setup.bash` (or `setup.ps1` for PowerShell) file in your `install` directory to make your package executables available in your environment.
    ```bash
    . install/setup.bash # or source install/setup.bash
    ```

This process creates a functional ROS 2 Python package that `colcon` can build and install.

## Launch files and parameter management

Launch files are a crucial part of ROS 2 for starting and configuring multiple nodes and their parameters simultaneously. They are typically written in Python or XML.

### Python Launch Files

Python launch files provide more flexibility and programmatic control. They use the `launch` and `launch_ros` packages.

```python
# Example: simple_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='sim_talker',
            parameters=[
                {'message': 'Hello from launch!'},
                {'rate': 5}
            ]
        ),
        Node(
            package='demo_nodes_cpp',
            executable='listener',
            name='sim_listener',
        ),
    ])
```

To run this launch file:
```bash
ros2 launch my_package simple_launch.py
```

### Parameter Management

Parameters allow you to configure the behavior of nodes at runtime without recompiling the code. They can be set:

1.  **Directly in Launch Files**: As shown in the example above, using the `parameters` argument for a `Node`.
2.  **From YAML Files**: For more complex configurations, parameters can be loaded from YAML files.
    ```yaml
    # params.yaml
    sim_talker:
      ros__parameters:
        message: "Hello from YAML!"
        rate: 10
    ```
    Then, in your launch file:
    ```python
    # ... inside generate_launch_description()
    Node(
        package='demo_nodes_cpp',
        executable='talker',
        name='sim_talker',
        parameters=['path/to/params.yaml'] # Load parameters from YAML
    ),
    # ...
    ```

3.  **Command Line**: Parameters can be overridden directly from the command line when running a node or a launch file.
    ```bash
    ros2 run demo_nodes_cpp talker --ros-args -p message:="Hello from CLI!"
    ros2 launch my_package simple_launch.py --ros-args -p sim_talker.rate:=2
    ```

4.  **Dynamically at Runtime**: Using `ros2 param` commands.
    ```bash
    ros2 param set /sim_talker message "New message"
    ```

Effective parameter management makes your ROS 2 applications more flexible and easier to configure for different scenarios or robot platforms.

## Understanding URDF (Unified Robot Description Format) for humanoids

URDF (Unified Robot Description Format) is an XML format used in ROS to describe all aspects of a robot. For humanoids and complex robots, URDF is essential for defining their kinematic and dynamic properties, visual appearance, and collision models.

### Key URDF Elements:

*   **`<robot>`**: The root element, defining the robot's name.
*   **`<link>`**: Represents a rigid body of the robot (e.g., torso, upper arm, hand). Links have physical properties (mass, inertia), visual properties (geometry, color, texture), and collision properties.
*   **`<joint>`**: Defines the connection between two links. Joints specify the type of connection (e.g., `revolute`, `prismatic`, `fixed`), axis of rotation/translation, limits, and dynamics.
    *   **`parent` and `child`**: Links connected by the joint.
    *   **`origin`**: The transform from the parent link's origin to the joint's origin.
*   **`<visual>`**: Defines the visual properties of a link (how it looks in RViz or other simulators).
*   **`<collision>`**: Defines the collision properties of a link (how it interacts physically with its environment).
*   **`<inertial>`**: Defines the mass, center of mass, and inertia matrix of a link.

### Example (simplified humanoid limb):

```xml
<?xml version="1.0"?>
<robot name="humanoid_limb">

  <link name="base_link"/>

  <link name="upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

</robot>
```

### Why URDF is important for humanoids:

*   **Simulation**: Accurately represents the robot in simulators like Gazebo.
*   **Visualization**: Allows tools like RViz to display the robot model.
*   **Motion Planning**: Provides kinematic and dynamic information for inverse kinematics, collision checking, and path planning algorithms.
*   **Hardware Interface**: Can be used to define the joints and sensors that ROS controllers will interact with.

For complex humanoid robots, URDF files can become quite extensive, often structured using `xacro` macros to improve readability and reusability.
