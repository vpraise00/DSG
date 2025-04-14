from lxml import etree
import argparse
import random
from pathlib import Path

def falled_object():
    """
    Create a random object falling from the sky.
    """

    scenario__object = etree.Element("ScenarioObject", name = "OBJ")
    misc_object = etree.SubElement(scenario__object, "MiscObject", mass = "0", miscObjectCategory = "obstacle", name = "PE_Firewall_Orange")
    properties = etree.SubElement(misc_object, "Properties")
    etree.SubElement(properties, "Property", name = "scale_x", value = "1.0")
    etree.SubElement(properties, "Property", name = "scale_y", value = "1.0")
    etree.SubElement(properties, "Property", name = "scale_z", value = "1.0")
    return scenario__object

def get_obj_position_from_private_rel(scenario_root):
    """
    Retrieve the RelativeObjectPosition attributes of the falling object (OBJ)
    from the Private element.
    Returns dx, dy, dz values as strings.
    """
    rop = scenario_root.find(".//Private[@entityRef='OBJ']/PrivateAction/TeleportAction/Position/RelativeObjectPosition")
    if rop is None:
        raise ValueError("RelativeObjectPosition not found in the Private element.")
    dx = rop.attrib.get("dx")
    dy = rop.attrib.get("dy")
    dz = rop.attrib.get("dz", "0")
    return dx, dy, dz

def get_ego_absolutetargetspeed(scenario_root):
    """
    Retrieve the AbsoluteTargetSpeed value for Ego from the scenario.
    This function looks in Ego's PrivateAction/LongitudinalAction/SpeedAction section.
    """
    ats = scenario_root.find(".//Private[@entityRef='Ego']/PrivateAction/LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed")
    if ats is None:
        raise ValueError("Ego AbsoluteTargetSpeed not found in the scenario.")
    try:
        return float(ats.attrib.get("value"))
    except (ValueError, TypeError):
        raise ValueError("Ego AbsoluteTargetSpeed value is not numeric.")

def add_Ego_lanechange_action_rel(scenario_root):
    """
    Create and return a ManeuverGroup for Ego lane change action.
    
    이 함수는 lane change 이벤트를 구성하는 XML 구조를 생성합니다.
    (여기서는 LinkPosition id와 index 값은 하드코딩되어 있지만, 필요에 따라 scenario_root를
    이용해 동적으로 추출할 수도 있습니다.)
    """
    # ManeuverGroup 생성
    mg = etree.Element("ManeuverGroup", maximumExecutionCount="1", name="ManueverGroup_Ego_event")
    
    # Actors 블록 생성 및 Ego EntityRef 추가
    actors = etree.SubElement(mg, "Actors", selectTriggeringEntities="false")
    etree.SubElement(actors, "EntityRef", entityRef="Ego")
    
    # Maneuver 생성
    maneuver = etree.SubElement(mg, "Maneuver", name="Maneuver_Ego_event")
    
    # Event 생성
    event = etree.SubElement(maneuver, "Event", maximumExecutionCount="1", name="Ego_event", priority="overwrite")
    
    # Action 생성: Ego_lc
    action = etree.SubElement(event, "Action", name="Ego_lc")
    private_action = etree.SubElement(action, "PrivateAction")
    lateral_action = etree.SubElement(private_action, "LateralAction")
    
    # LaneChangeAction 구성 (targetLaneOffset="1")
    lane_change = etree.SubElement(lateral_action, "LaneChangeAction", targetLaneOffset="1")
    etree.SubElement(lane_change, "LaneChangeActionDynamics", dynamicsDimension="distance", dynamicsShape="step", value="5")
    lane_change_target = etree.SubElement(lane_change, "LaneChangeTarget")
    etree.SubElement(lane_change_target, "RelativeTargetLane", entityRef="Ego", value="1")
    
    # StartTrigger 생성 및 조건 구성
    start_trigger = etree.SubElement(event, "StartTrigger")
    condition_group = etree.SubElement(start_trigger, "ConditionGroup")
    condition = etree.SubElement(condition_group, "Condition", conditionEdge="rising", delay="0", name="Ego_condition")
    by_entity_condition = etree.SubElement(condition, "ByEntityCondition")
    triggering_entities = etree.SubElement(by_entity_condition, "TriggeringEntities", triggeringEntitiesRule="all")
    etree.SubElement(triggering_entities, "EntityRef", entityRef="Ego")
    entity_condition = etree.SubElement(by_entity_condition, "EntityCondition")
    # Retrieve Ego's AbsoluteTargetSpeed and compute threshold (3/2 * speed)
    ego_speed = get_ego_absolutetargetspeed(scenario_root)
    threshold = ego_speed * 1.5
    
    distance_condition = etree.SubElement(entity_condition, "DistanceCondition",
                                          coordinateSystem="entity", freespace="false",
                                          relativeDistanceType="euclideanDistance",
                                          routingAlgorithm="assignedRoute", rule="lessThan", value=str(threshold))
    pos = etree.SubElement(distance_condition, "Position")
    dx, dy, dz = get_obj_position_from_private_rel(scenario_root)
    etree.SubElement(pos, "RelativeObjectPosition", entityRef="Ego", dx=dx, dy=dy, dz=dz)
    
    return mg

def add_Ego_stop_action_rel(scenario_root):
    """
    Create and return a ManeuverGroup for Ego stop action.
    
    This function creates a stop event for Ego where Ego's speed is set to zero.
    The stop action is triggered when the Euclidean distance (from Ego to the falling object)
    is less than 10. The DistanceCondition's Position element uses the falling object's 
    LinkPosition information (from the Private element) to establish the reference.
    """
    mg = etree.Element("ManeuverGroup", maximumExecutionCount="1", name="ManueverGroup_Ego_event")
    
    # Actors 블록 생성 및 Ego EntityRef 추가
    actors = etree.SubElement(mg, "Actors", selectTriggeringEntities="false")
    etree.SubElement(actors, "EntityRef", entityRef="Ego")
    
    # Maneuver 생성
    maneuver = etree.SubElement(mg, "Maneuver", name="Maneuver_Ego_event")
    
    # Event 생성
    event = etree.SubElement(maneuver, "Event", maximumExecutionCount="1", name="Ego_event", priority="overwrite")
    
    # Action 생성: Ego_stop
    action = etree.SubElement(event, "Action", name="Ego_stop")
    private_action = etree.SubElement(action, "PrivateAction")
    long_action = etree.SubElement(private_action, "LongitudinalAction")
    speed_action = etree.SubElement(long_action, "SpeedAction")
    
    # SpeedActionTarget 설정: 속도를 0으로 (정지)
    speed_target = etree.SubElement(speed_action, "SpeedActionTarget")
    etree.SubElement(speed_target, "RelativeTargetSpeed", continuous="true", entityRef="Ego",
                     range="0", speedTargetValueType="delta", type="custom", value="0")
    
    # SpeedActionDynamics 구성
    etree.SubElement(speed_action, "SpeedActionDynamics", dynamicsDimension="distance",
                     dynamicsShape="step", value="5")
    
    # StartTrigger 구성
    start_trigger = etree.SubElement(event, "StartTrigger")
    condition_group = etree.SubElement(start_trigger, "ConditionGroup")
    condition = etree.SubElement(condition_group, "Condition", conditionEdge="rising", delay="0", name="Ego_condition")
    by_entity_condition = etree.SubElement(condition, "ByEntityCondition")
    triggering_entities = etree.SubElement(by_entity_condition, "TriggeringEntities", triggeringEntitiesRule="all")
    etree.SubElement(triggering_entities, "EntityRef", entityRef="Ego")
    entity_condition = etree.SubElement(by_entity_condition, "EntityCondition")
    # Retrieve Ego's AbsoluteTargetSpeed and compute threshold (3/2 * speed)
    ego_speed = get_ego_absolutetargetspeed(scenario_root)
    threshold = ego_speed * 1.5
    
    distance_condition = etree.SubElement(entity_condition, "DistanceCondition",
                                          coordinateSystem="entity", freespace="false",
                                          relativeDistanceType="euclideanDistance",
                                          routingAlgorithm="assignedRoute", rule="lessThan", value=str(threshold))
    pos = etree.SubElement(distance_condition, "Position")
    dx, dy, dz = get_obj_position_from_private_rel(scenario_root)
    etree.SubElement(pos, "RelativeObjectPosition", entityRef="Ego", dx=dx, dy=dy, dz=dz)
    
    return mg


def private_storyboard_rel(scenario_root):
    """
    Create a private storyboard for the object.
    """

    # Extract the ego link position from the scenario root
    ego_id, ego_index = get_ego_linkposition(scenario_root)

    new_index = random.randint(ego_index + 50, ego_index + 150)

    private = etree.Element("Private", entityRef = "OBJ")
    private_action = etree.SubElement(private, "PrivateAction")
    teleport_action = etree.SubElement(private_action, "TeleportAction")
    position = etree.SubElement(teleport_action, "Position")
    # 생성하는 RelativeObjectPosition: ego의 좌표계 기준, 전방 50m, lateral=0, dz=0 (기본값)
    etree.SubElement(position, "RelativeObjectPosition",
                     entityRef="Ego", dx="50", dy="0", dz="0")
    return private

def get_ego_linkposition(scenario_root):
    """
    Get the ego link position from the scenario root.
    It will return linkposion id and index.
    """
    lp = scenario_root.find(".//Private[@entityRef='Ego']/PrivateAction/TeleportAction/Position/LinkPosition")
    if lp is None:
        raise ValueError("Ego LinkPosition not found in the input scenario.")
    
    ego_id = lp.attrib.get("id")
    try:
        ego_index = int(lp.attrib.get("index", "0"))
    except ValueError:
        raise ValueError("Ego LinkPosition index is not an integer.")
    
    return ego_id, ego_index
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="명령어 입력하면 시나리오 내부에 Entity와 Private Action을 생성")
    parser.add_argument("scenario_file", type=str, help="입력 시나리오 파일 (.xosc)")
    args = parser.parse_args()

    input_path = Path(args.scenario_file).resolve()
    tree = etree.parse(str(input_path))
    root = tree.getroot()

    # 1. Entities 블록에 Object 객체 추가
    entities = root.find(".//Entities")
    if entities is None:
        raise ValueError("시나리오 내에 Entities 블록을 찾을 수 없습니다.")
    entities.append(falled_object())

    # 2. StoryBoard/Init/Actions 블록에 Private 요소 추가
    storyboard_actions = root.find(".//StoryBoard/Init/Actions")
    if storyboard_actions is None:
        raise ValueError("시나리오 내에 StoryBoard/Init/Actions 블록을 찾을 수 없습니다.")
    storyboard_actions.append(private_storyboard_rel(root))

    # 3. 지정된 위치에 Ego의 stop 액션 추가
    act = root.find(".//Story[@name='new_story']/Act[@name='new_act']")
    if act is None:
        raise ValueError("Act element with name 'new_act' not found in new_story.")
    act.append(add_Ego_stop_action_rel(root))
    print("Ego stop action added.")

    # # 'lanechange'와 'stop' 중 랜덤으로 선택
    # action_choice = random.choice(['lanechange', 'stop'])
    # if action_choice == 'lanechange':
    #     act.append(add_Ego_lanechange_action(root))
    #     print("Ego lane change action added.")
    # else:
    #     act.append(add_Ego_stop_action(root))
    #     print("Ego stop action added.")


    # 들여 쓰기 적용 후 파일 저장
    etree.indent(root, space="  ")
    output_path = input_path.parent / f"{input_path.stem}_fallingOBJ.xosc"
    tree.write(str(output_path), pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"변경된 시나리오 파일이 저장되었습니다: {output_path}")