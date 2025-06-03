import argparse
from pathlib import Path
from lxml import etree as ET

from rootcause import *

import utils.config as cf

def arg_parser():
    parser = argparse.ArgumentParser(description="Add disturbance to the scenario.")
    parser.add_argument("input_file", type=str, help="Input File (.xosc)")
    parser.add_argument("--disturbance", type=str,
                        choices=["rain", "snow", "blackice", "fallOBJ", "construction", "speedConstraint"],
                        help="Disturbance type [rain, snow, blackice, fallOBJ, construction, speedConstraint]",
                        required=True)
    parser.add_argument("--obj_pos", type=str, choices=["relative", "link"], default="relative",
                        help="Object position definition [relative, link]")
    parser.add_argument("--action", type=str, choices=["lanechange", "stop"], default="stop",
                        help="Action type only required in fallOBJ [lanechange, stop]")
    parser.add_argument("--distance", type=float, default=30,
                        help="Relative distance in meters for object placement (only used for relative mode)")
    parser.add_argument("--target-speed", type=float, default=17.5,
                        help="Target speed for speedConstraint (m/s)")
    args = parser.parse_args()

    return args

def main():

    args = arg_parser()

    print(args)
    print(args.input_file)
    print("Selected Root Cause : ", args.disturbance)
    print("Object Position method :", args.obj_pos)
    if args.action:
        print("Action type:", args.action)
    print("Distance for object placement:", args.distance)

    input_file = args.input_file
    output_file = f"{input_file[:-5]}_{args.disturbance}.xosc"

    cf.CONFIG = cf.Config(input_file, output_file)
    tree = cf.CONFIG.tree
    root = cf.CONFIG.root

    # 1. Entities 블록에 falling object 추가
    entities = root.find(".//Entities")
    if entities is None:
        raise ValueError("Entities block not found in the input scenario file.")
    
    # 2. Storyboard/Init/Actions 블록에 Private 요소 추가
    actions = root.find(".//Storyboard/Init/Actions")
    if actions is None:
        raise ValueError("Storyboard/Init/Actions block not found in the input scenario file.")
    
    # 3. 지정된 위치에 Ego의 액션 추가 (lanechange 또는 stop, --action 인자 사용)
    act = root.find(".//Storyboard/Story[@name='new_story']/Act[@name='new_act']")
    if act is None:
        raise ValueError("Act element with name 'new_act' not found in new_story.")

    if args.disturbance == "rain":
        act.append(weather_rain())
    if args.disturbance == "snow":
        act.append(weather_snow())
    if args.disturbance == "fallOBJ":
        entities.append(falled_object())
        actions.append(private_storyboard(args.distance, args.obj_pos))
    if args.disturbance == "construction":
        entities.append(falled_object())
        actions.append(rightmost_construction(2*args.distance))
    if args.disturbance == "speedConstraint":
        # speedConstraint용 객체·액션 준비
        obj, init, mg = speed_constraint_action(
            scenario_root=root,
            place_distance=args.distance,
            target_speed=args.target_speed
        )
        entities.append(obj)
        actions.append(init)
        act.append(mg)

    if args.action == "lanechange":
        act.append(add_Ego_lanechange_action(root, args.distance, args.obj_pos))
    if args.action == "stop":
        act.append(add_Ego_stop_action(root, args.distance, args.obj_pos))

    ET.indent(root, space="  ")
    tree.write(cf.CONFIG.output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
    print(f"Output written to {cf.CONFIG.output_path}")

if __name__ == "__main__":
    main()
