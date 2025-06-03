import pandas as pd

from utils import config as cf

def get_link_len(link):
    mgeo_link_set = cf.CONFIG.mgeo_link_set
    return len(mgeo_link_set[mgeo_link_set["idx"] == link]["points"].values[0])

def get_ego_link(ego_name="Ego"):
    """
    Get the ego link position from the scenario root.
    It will return linkposion id and index.
    """
    link_position = cf.CONFIG.root.find(f".//Private[@entityRef='{ego_name}']/PrivateAction/TeleportAction/Position/LinkPosition")
    if link_position is None:
        raise ValueError("Ego LinkPosition not found in the input scenario.")
    
    ego_link = link_position.attrib.get("id")
    try:
        ego_index = int(link_position.attrib.get("index", "0"))
    except ValueError:
        raise ValueError("Ego LinkPosition index is not an integer.")
    
    return ego_link, ego_index

def get_rightmost_link():
    mgeo_link_set = cf.CONFIG.mgeo_link_set

    ego_link, ego_index = get_ego_link()

    right_link = ego_link
    while mgeo_link_set[mgeo_link_set["idx"] == right_link]["right_lane_change_dst_link_idx"].values[0] != None:
        right_link = mgeo_link_set[mgeo_link_set["idx"] == right_link]["right_lane_change_dst_link_idx"].values[0]

    return right_link

def get_back_link(link):
    mgeo_link_set = cf.CONFIG.mgeo_link_set

    back_node = mgeo_link_set[mgeo_link_set["idx"] == link]["from_node_idx"].values[0]

    tmp = mgeo_link_set[mgeo_link_set["to_node_idx"] == back_node]
    back_link = tmp[~tmp["idx"].str.contains("-")]["idx"].values[0]

    return back_link