#! python3

import argparse
import random
from pathlib import Path
from lxml import etree

def agr_parser():
    parser = argparse.ArgumentParser(description="Add disturbance to the scenario.")
    parser.add_argument("input_file", type=str, help="Input File (.xosc)")
    parser.add_argument("--disturbance", type=str, choices=["rain", "snow", "fallOBJ"], 
                        help="Disturbance type [rain, snow, fallOBJ]", required=True)
    parser.add_argument("--obj_pos", type=str, choices=["relative", "link"], default="relative", 
                        help="Object position definition [relative, link]")
    parser.add_argument("--action", type=str, choices=["lanechange", "stop"], default="stop", 
                        help="Action type only required in fallOBJ [lanechange, stop]")
    parser.add_argument("--distance", type=float, default=30, 
                        help="Relative distance in meters for object placement (only used for relative mode)")
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = agr_parser()
    print(args)
    print(args.input_file)
    print("Selected Root Cause : ", args.disturbance)
    print("Object Position method :", args.obj_pos)
    if args.action:
        print("Action type:", args.action)
    print("Distance for object placement:", args.distance)

    input_path = Path(args.input_file).resolve()
    data_dir = input_path.parent
    output_path = data_dir / f"{input_path.name[:-5]}_{args.disturbance}.xosc"

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file {input_path} does not exist.")

    tree = etree.parse(input_path)
    root = tree.getroot()

    maneuverGroup = None # Initialize maneuverGroup to None

    if args.disturbance == "rain":
        from weather_rootcause import weather_rain
        maneuverGroup = weather_rain()
    elif args.disturbance == "snow":
        from weather_rootcause import weather_snow
        maneuverGroup = weather_snow()
    elif args.disturbance == "fallOBJ":
        # 추가: --object 인자에 따라 사용 모듈 결정
        if args.obj_pos == "relative":
            from falling_obj_rootcause_rel import falled_object, private_storyboard_rel, add_Ego_lanechange_action_rel, add_Ego_stop_action_rel
            obj_module = "relative"
        elif args.obj_pos == "link":
            from falling_obj_rootcause import falled_object, private_storyboard, add_Ego_lanechange_action, add_Ego_stop_action
            obj_module = "link"
        else:
            raise ValueError("Invalid object method. Choose 'relative' or 'link'.")
        
        # 1. Entities 블록에 falling object 추가
        entities = root.find(".//Entities")
        if entities is None:
            raise ValueError("Entities block not found in the input scenario file.")
        entities.append(falled_object())
        
        # 2. Storyboard/Init/Actions 블록에 Private 요소 추가
        actions = root.find(".//Storyboard/Init/Actions")
        if actions is None:
            raise ValueError("Storyboard/Init/Actions block not found in the input scenario file.")
        # object 방식에 따라 호출: 여기는 --object 인자로 결정되고, 디폴트는 "relative"일 것임
        if obj_module == "relative":
            actions.append(private_storyboard_rel(root, args.distance))
        else:
            # 기존 방식을 사용하면 private_storyboard(root)를 호출
            actions.append(private_storyboard(root))
        
        # 3. 지정된 위치에 Ego의 액션 추가 (lanechange 또는 stop, --action 인자 사용)
        act = root.find(".//Story[@name='new_story']/Act[@name='new_act']")
        if act is None:
            raise ValueError("Act element with name 'new_act' not found in new_story.")
        if args.action == "lanechange":
            if obj_module == "relative":
                act.append(add_Ego_lanechange_action_rel(root))
            else:
                act.append(add_Ego_lanechange_action(root))
            print("Ego lane change action added.")
        elif args.action == "stop":
            if obj_module == "relative":
                act.append(add_Ego_stop_action_rel(root))
            else:
                act.append(add_Ego_stop_action(root))
            print("Ego stop action added.")
        else:
            raise ValueError("Invalid action type. Choose 'lanechange' or 'stop'.")
    else:
        raise ValueError("Invalid disturbance type. Choose 'rain' or 'snow' or 'fallOBJ'.")
    
    # Weather RootCause인 경우에만 Act 블록에 ManeuverGroup 추가
    if maneuverGroup is not None:
        target_elements = tree.xpath("//Act")
        if target_elements:
            target = target_elements[0]
            target.append(maneuverGroup)

    # 파일 저장은 regardless of maneuverGroup
    etree.indent(root, space="  ")
    tree.write(output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
    print(f"Output written to {output_path}")