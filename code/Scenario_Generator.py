#! python3

import argparse
from pathlib import Path
from lxml import etree

def agr_parser():
    parser = argparse.ArgumentParser(description="Add disturbance to the scenario.")
    parser.add_argument("input_file", type=str, help="Input File (.xosc)")
    parser.add_argument("--disturbance", type=str, choices=["rain", "snow", "fallOBJ"], help="Disturbance type [rain, snow, fallOBJ]", required=True)
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = agr_parser()
    print(args)
    print(args.input_file)
    print(args.disturbance)

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
        from falling_obj_rootcause import falled_object, private_storyboard
        # 1. Entities 블록에 falling object 추가
        entities = root.find(".//Entities")
        if entities is None:
            raise ValueError("Entities block not found in the input scenario file.")
        entities.append(falled_object())
        # 2. Storyboard/Init/Actions 블록에 Private 요소 추가
        actions = root.find(".//Storyboard/Init/Actions")
        if actions is None:
            raise ValueError("Storyboard/Init/Actions block not found in the input scenario file.")
        actions.append(private_storyboard(root))
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