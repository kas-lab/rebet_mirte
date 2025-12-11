#include <iostream>
#include <vector>
#include <algorithm>
#include "rebet_msgs/srv/detect_object.hpp"
#include "rebet_msgs/msg/objects_identified.hpp"
#include "rebet_msgs/msg/measure.hpp"
#include "behaviortree_ros2/bt_service_node.hpp"
#include <math.h>
#include "nav_msgs/msg/odometry.hpp"
#include "behaviortree_ros2/plugins.hpp"
#include "behaviortree_cpp/json_export.h"

namespace BT
{

using DetectObject = rebet_msgs::srv::DetectObject;
using ObjectsIdentified = rebet_msgs::msg::ObjectsIdentified;
using Measure = rebet_msgs::msg::Measure;

class DetectObjectService : public RosServiceNode<DetectObject>
{
public:
  static constexpr const char * OBJ_OUT = "objs_identified";
  static constexpr const char * PICS_TAKEN = "pictures_taken";


  DetectObjectService(
    const std::string & instance_name,
    const BT::NodeConfig & conf,
    const BT::RosNodeParams & params)
  : RosServiceNode<DetectObject>(instance_name, conf, params)
  {
    num_executions = 0;
    times_anything_detected = 0;
  }


  static PortsList providedPorts()
  {
    PortsList base_ports = RosServiceNode::providedPorts();

    PortsList child_ports = {
      OutputPort<std::string>("name_of_task"),
      OutputPort<int>(PICS_TAKEN),
      OutputPort<Measure>("measure_taken"),
    };

    child_ports.merge(base_ports);

    return child_ports;
  }

  bool setRequest(typename Request::SharedPtr & request) override
  {
    RCLCPP_INFO(logger(), "ID object request");

    setOutput("name_of_task", registrationName());
    request->id = 1;     //fix

    return true;

  }

  BT::NodeStatus onFailure(ServiceNodeErrorCode error) override
  {
    RCLCPP_ERROR(logger(), "Error: %d", error);
    return NodeStatus::FAILURE;
  }

  BT::NodeStatus onResponseReceived(const typename Response::SharedPtr & response) override
  {
    RCLCPP_INFO(logger(), "response received");

    num_executions++;
    std::vector<ObjectsIdentified> obj_idd = response.get()->objects_id;

    Measure measure_msg;
    measure_msg.monitor_function = "calc_detect_obj";
    nlohmann::json dest;
    JsonExporter::get().toJson(BT::Any(obj_idd), dest);

    std::cout << "Detected objects JSON: " << dest.dump() << std::endl;
    RCLCPP_INFO(logger(), dest.dump().c_str());
    measure_msg.json_value = dest.dump();

    nlohmann::json dest2;
     JsonExporter::get().toJson(BT::Any(measure_msg), dest2);
    std::cout << "Meausre object to JSON: " << dest2.dump() << std::endl;
    setOutput(PICS_TAKEN, num_executions);
    setOutput("measure_taken", measure_msg);

    // RCLCPP_INFO(logger(), ss.str().c_str());
    RCLCPP_INFO(logger(), "SUCCESS IN IDOBJ");
    return NodeStatus::SUCCESS;
  }

private:
  int num_executions;
  std::string goal_object = "fire hydrant";      //Parameterize
  int times_detected;      //privatize
  int times_anything_detected;


};

BT_REGISTER_ROS_NODES(factory, params)
{
  RosNodeParams aug_params;
  aug_params.nh = params.nh;
  aug_params.server_timeout = std::chrono::milliseconds(40000);   //The YOLO can take quite a while.

  factory.registerNodeType<DetectObjectService>("NewIDObj", aug_params);
}


}
