import argparse
from pathlib import Path
from lxml import etree as ET

from falling_obj_rootcause import *
#from rightmost_construction_rootcause import *
from speed_constraint import speed_constraint_action

def arg_parser():
    parser = argparse.ArgumentParser(description="Add disturbance to the scenario.")
    parser.add_argument("input_file", type=str, help="Input File (.xosc)")
    parser.add_argument("--disturbance", type=str,
                        choices=["rain", "snow", "fallOBJ", "construction", "speedConstraint"],
                        help="Disturbance type [rain, snow, fallOBJ, construction, speedConstraint]",
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


    input_path = Path(args.input_file).resolve()
    data_dir = input_path.parent
    output_path = data_dir / f"{input_path.name[:-5]}_{args.disturbance}.xosc"
    # mgeo_dir = data_dir / "MGeo"
    # mgeo_link_set_path = mgeo_dir / "link_set.json"

    # if not input_path.is_file():
    #     raise FileNotFoundError(f"Input file {input_path} does not exist.")
    # if not mgeo_link_set_path.is_file():
    #     raise FileNotFoundError(f"MGeo link set file {mgeo_link_set_path} does not exist.")
    
    tree = ET.parse(input_path)
    root = tree.getroot()

    # speedConstraint용 객체·액션 준비
    if args.disturbance == "speedConstraint":
        obj, init, mg = speed_constraint_action(
            scenario_root=root,
            place_distance=args.distance,
            target_speed=args.target_speed
        )

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
        from weather_rootcause import weather_rain
        act.append(weather_rain())
    if args.disturbance == "snow":
        from weather_rootcause import weather_snow
        act.append(weather_snow())
    if args.disturbance == "fallOBJ":
        entities.append(falled_object())
        actions.append(private_storyboard(root, mgeo_link_set_path, args.distance, args.obj_pos))
    if args.disturbance == "construction":
        from rightmost_construction_rootcause import add_rightmost_construction
        entities.append(falled_object())
        actions.append(add_rightmost_construction(root, mgeo_link_set_path, 2*args.distance))
    if args.disturbance == "speedConstraint":
        entities.append(obj)
        actions.append(init)
        act.append(mg)

    if args.action == "lanechange":
        act.append(add_Ego_lanechange_action(root, args.distance, args.obj_pos))
    if args.action == "stop":
        act.append(add_Ego_stop_action(root, args.distance, args.obj_pos))

    ET.indent(root, space="  ")
    tree.write(output_path, pretty_print=True, encoding="utf-8", xml_declaration=True)
    print(f"Output written to {output_path}")

if __name__ == "__main__":
    main()