from pathlib import Path
from lxml import etree as ET
import pandas as pd

from falling_obj_rootcause import falled_object, private_storyboard

def get_road_network_path(scenario_root):
    road_network = scenario_root.find(".//RoadNetwork")
    road_net_children = {item.tag: item.attrib for item in road_network.getchildren()}
    logic_file_path = road_net_children["LogicFile"]["filepath"]
    # sceneGraphFile = road_net_children["SceeneGraphFile"]["filepath"]
    return logic_file_path

def add_rightmost_construction(scenario_root, mgeo_link_set_path):
    mgeo_link_set = pd.read_json(mgeo_link_set_path, encoding="utf-8")

    init_pos = scenario_root.find(".//Storyboard/Init/Actions/Private[@entityRef='Ego']/PrivateAction/TeleportAction/Position/LinkPosition").attrib
    init_node = init_pos["id"]
    init_index = int(init_pos["index"])

    right_node = init_node
    while mgeo_link_set[mgeo_link_set["idx"] == right_node]["right_lane_change_dst_link_idx"].values[0] != None:
        right_node = mgeo_link_set[mgeo_link_set["idx"] == right_node]["right_lane_change_dst_link_idx"].values[0]

    dst_index = init_index + 100 if init_index + 100 < len(mgeo_link_set[mgeo_link_set["idx"] == right_node]["points"].values[0]) else len(mgeo_link_set[mgeo_link_set["idx"] == right_node]["points"].values[0]) - 1
    
    private = ET.Element("Private", entityRef = "OBJ")
    private_action = ET.SubElement(private, "PrivateAction")
    teleport_action = ET.SubElement(private_action, "TeleportAction")
    position = ET.SubElement(teleport_action, "Position")
    ET.SubElement(position, "LinkPosition", id = init_node, index = str(dst_index))

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