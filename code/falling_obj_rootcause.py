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

def private_storyboard(scenario_root):
    """
    Create a private storyboard for the object.
    """

    # Extract the ego link position from the scenario root
    ego_id, ego_index = get_ego_linkposition(scenario_root)

    new_index = random.randint(ego_index + 1, ego_index + 50)

    private = etree.Element("Private", entityRef = "OBJ")
    private_action = etree.SubElement(private, "PrivateAction")
    teleport_action = etree.SubElement(private_action, "TeleportAction")
    position = etree.SubElement(teleport_action, "Position")
    etree.SubElement(position, "LinkPosition", id = ego_id, index = str(new_index))
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
    storyboard_actions.append(private_storyboard(root))

    # 들여 쓰기 적용 후 파일 저장
    etree.indent(root, space="  ")
    output_path = input_path.parent / f"{input_path.stem}_fallingOBJ.xosc"
    tree.write(str(output_path), pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"변경된 시나리오 파일이 저장되었습니다: {output_path}")