from pathlib import Path
from lxml import etree as ET
import pandas as pd

from falling_obj_rootcause import get_ego_linkposition

def get_road_network_path(scenario_root):
    road_network = scenario_root.find(".//RoadNetwork")
    road_net_children = {item.tag: item.attrib for item in road_network.getchildren()}
    logic_file_path = road_net_children["LogicFile"]["filepath"]
    # sceneGraphFile = road_net_children["SceeneGraphFile"]["filepath"]
    return logic_file_path

def add_rightmost_construction(scenario_root, mgeo_link_set_path, distance_input=100):
    mgeo_link_set = pd.read_json(mgeo_link_set_path, encoding="utf-8")

    ego_id, ego_index = get_ego_linkposition(scenario_root)
    ego_index = int(ego_index)

    right_node = ego_id
    while mgeo_link_set[mgeo_link_set["idx"] == right_node]["right_lane_change_dst_link_idx"].values[0] != None:
        right_node = mgeo_link_set[mgeo_link_set["idx"] == right_node]["right_lane_change_dst_link_idx"].values[0]

    dst_index = ego_index + distance_input if ego_index + distance_input < len(mgeo_link_set[mgeo_link_set["idx"] == right_node]["points"].values[0]) else len(mgeo_link_set[mgeo_link_set["idx"] == right_node]["points"].values[0]) - 1
    
    private = ET.Element("Private", entityRef = "OBJ")
    private_action = ET.SubElement(private, "PrivateAction")
    teleport_action = ET.SubElement(private_action, "TeleportAction")
    position = ET.SubElement(teleport_action, "Position")
    ET.SubElement(position, "LinkPosition", id = ego_id, index = str(dst_index))

    return private

if __name__ == "__main__":
    in_file = "D:\\\TUK\\AILAB\\datasets\\[MORAI] T-Car Lv.4  Autonomous Vehicle V&V Scenario\\T_CAR\\R_KR_PG_K-City\\tcar_t1_10.xosc"
    in_file = Path(in_file).resolve()
    mgeo_dir = in_file.parent / "MGeo"
    mgeo_link_set_file = mgeo_dir / "link_set.json"
    mgeo_link_set = pd.read_json(mgeo_link_set_file, encoding="utf-8")

    root = ET.parse(in_file).getroot()

    roadnet = add_rightmost_construction(root)
    print(roadnet)