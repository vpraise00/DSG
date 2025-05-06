from lxml import etree as ET


def create_speed_sign_object(sign_name: str = "KR_Sign_SL_60") -> ET.Element:
    """
    Creates a ScenarioObject for a speed limit sign.
    """
    obj = ET.Element("ScenarioObject", attrib={"name": "OBJ"})
    misc = ET.SubElement(obj, "MiscObject",
                         attrib={
                             "mass": "0",
                             "miscObjectCategory": "obstacle",
                             "name": sign_name
                         })
    props = ET.SubElement(misc, "Properties")
    for axis in ("x", "y", "z"):
        ET.SubElement(props, "Property", attrib={"name": f"scale_{axis}", "value": "1.0"})
    return obj


def create_speed_sign_init(distance: float,
                           lateral: float = 0.0,
                           height: float = 0.0,
                           dH: float = 0.0,
                           dP: float = 0.0,
                           dR: float = 0.0) -> ET.Element:
    """
    Creates a Private teleport action to place the speed sign relative to Ego.
    Uses RelativeObjectPosition according to OpenSCENARIO 1.2.
    - distance: forward offset (m) along Ego's heading
    - lateral: lateral offset (m) to the right of Ego's heading
    - height: vertical offset (m) above ground
    - dH, dP, dR: angular offsets (rad) for heading, pitch, roll
    """
    private = ET.Element("Private", attrib={"entityRef": "OBJ"})
    pa = ET.SubElement(private, "PrivateAction")
    tp = ET.SubElement(pa, "TeleportAction")
    pos = ET.SubElement(tp, "Position")
    ET.SubElement(pos, "RelativeObjectPosition", attrib={
        "entityRef": "Ego",
        "dx": str(distance),
        "dy": str(lateral),
        "dz": str(height),
        "dH": str(dH),
        "dP": str(dP),
        "dR": str(dR)
    })
    return private

# 이 함수가 있는 모듈 최상단에 추가
def get_ego_absolutetargetspeed(scenario_root):
    ats = scenario_root.find(
        ".//Private[@entityRef='Ego']/PrivateAction"
        "/LongitudinalAction/SpeedAction"
        "/SpeedActionTarget/AbsoluteTargetSpeed"
    )
    if ats is None:
        raise ValueError("Ego AbsoluteTargetSpeed not found.")
    return float(ats.attrib["value"])

def create_speed_sign_maneuver(scenario_root: ET.Element, target_speed: float) -> ET.Element:
    """
    scenario_root에서 Ego 속도를 읽어와 threshold = ego_speed * 0.9로
    RelativeDistanceCondition을 설정하는 ManeuverGroup을 생성합니다.
    """
    # 1) Ego 속도 가져오기
    ego_speed = get_ego_absolutetargetspeed(scenario_root)
    threshold = ego_speed * 0.9

    # 2) ManeuverGroup 생성
    mg = ET.Element("ManeuverGroup", attrib={
        "maximumExecutionCount": "1",
        "name": "ManueverGroup_Ego_event"
    })
    actors = ET.SubElement(mg, "Actors", attrib={"selectTriggeringEntities": "false"})
    ET.SubElement(actors, "EntityRef", attrib={"entityRef": "Ego"})

    m = ET.SubElement(mg, "Maneuver", attrib={"name": "Maneuver_Ego_event"})
    ev = ET.SubElement(m, "Event", attrib={
        "maximumExecutionCount": "1",
        "name": "Ego_event",
        "priority": "overwrite"
    })

    # 속도 제어 액션
    action = ET.SubElement(ev, "Action", attrib={"name": "Ego_sc"})
    pa = ET.SubElement(action, "PrivateAction")
    la = ET.SubElement(pa, "LongitudinalAction")
    sa = ET.SubElement(la, "SpeedAction")

    # SpeedActionTarget 안에 AbsoluteTargetSpeed 중첩
    sat = ET.SubElement(sa, "SpeedActionTarget")
    ET.SubElement(sat, "AbsoluteTargetSpeed", attrib={
        "range": "0",
        "type": "custom",
        "value": str(target_speed)
    })

    ET.SubElement(sa, "SpeedActionDynamics", attrib={
        "dynamicsDimension": "distance",
        "dynamicsShape": "step",
        "value": "1"
    })


    # 트리거: Ego와 OBJ 간 상대거리가 threshold 이하일 때
    st = ET.SubElement(ev, "StartTrigger")
    cg = ET.SubElement(st, "ConditionGroup")
    cond = ET.SubElement(cg, "Condition", attrib={
        "conditionEdge": "rising",
        "delay": "0",
        "name": "Ego_condition"
    })
    byent = ET.SubElement(cond, "ByEntityCondition")
    trigents = ET.SubElement(byent, "TriggeringEntities", attrib={
        "triggeringEntitiesRule": "all"
    })
    ET.SubElement(trigents, "EntityRef", attrib={"entityRef": "Ego"})
    entcond = ET.SubElement(byent, "EntityCondition")
    ET.SubElement(entcond, "RelativeDistanceCondition", attrib={
        "coordinateSystem":     "entity",
        "entityRef":            "OBJ",
        "freespace":            "true",
        "relativeDistanceType": "euclideanDistance",
        "routingAlgorithm":     "assignedRoute",
        "rule":                 "lessThan",
        "value":                str(threshold)
    })

    return mg



def speed_constraint_action(scenario_root: ET.Element,
                            place_distance: float,
                            target_speed: float,
                            lateral: float = 0.0,
                            height: float = 0.0,
                            dH: float = 0.0,
                            dP: float = 0.0,
                            dR: float = 0.0):
    """
    Convenience wrapper:
      1) ScenarioObject 생성
      2) Init 단계 RelativeWorldPosition 생성 (place_distance)
      3) ManeuverGroup 생성 (Ego 속도 * 0.9 기반 트리거, target_speed)
    """
    obj = create_speed_sign_object()
    init = create_speed_sign_init(place_distance, lateral, height, dH, dP, dR)
    mg = create_speed_sign_maneuver(scenario_root, target_speed)
    return obj, init, mg

