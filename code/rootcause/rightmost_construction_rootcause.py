from pathlib import Path
from lxml import etree as ET
import pandas as pd

from utils import config as cf
from utils.mgeo import *

def rightmost_construction(distance_input=100):
    ego_id, ego_index = get_ego_link()
    dst_index = 0

    right_link = get_rightmost_link()
    right_link_len = get_link_len(right_link)
    if ego_index + distance_input < right_link_len:
        dst_index = ego_index + distance_input
    else:
        dst_index = right_link_len - 1
    
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