from lxml import etree
import random
import math

def weather_rain():
    maneuverGroup = etree.Element("ManeuverGroup", maximumExecutionCount="1", name="weather_maneuver_group")

    actors = etree.SubElement(maneuverGroup, "Actors", selectTriggeringEntities="false")
    maneuver = etree.SubElement(maneuverGroup, "Maneuver", name="Maneuver_weather_event")
    event = etree.SubElement(maneuver, "Event", maximumExecutionCount="1", name="weather_event", priority="overwrite")
    action = etree.SubElement(event, "Action", name="rainy_action")
    globalAction = etree.SubElement(action, "GlobalAction")
    environmentAction = etree.SubElement(globalAction, "EnvironmentAction")

    environment = etree.SubElement(environmentAction, "Environment", name="rainy_day")
    timeOfDay = etree.SubElement(environment, "TimeOfDay", animation="true", dateTime="2000-08-01T12:00:00")
    weather = etree.SubElement(environment, "Weather", atmosphericPressure=f"{random.randint(80000, 120000)}", fractionalCloudCover="zeroOktas", temperature="293")
    sun = etree.SubElement(weather, "Sun", azimuth=f"{round(random.Random().vonmisesvariate(0, 0), 5)}", elevation=f"{round(random.Random().vonmisesvariate(0, 0) - math.pi, 5)}", illuminance="5.45")
    fog = etree.SubElement(weather, "Fog", visualRange=f"{random.randint(3, 10000)}")
    precipitation = etree.SubElement(weather, "Precipitation", precipitationIntensity=f"{random.randint(0, 1000000)}", precipitationType="rain")
    wind = etree.SubElement(weather, "Wind", direction=f"{round(random.Random().vonmisesvariate(0, 0), 5)}", speed=f"{random.randint(0, 1000)}")
    domeImage = etree.SubElement(weather, "DomeImage", azimuthOffset=f"{round(random.Random().vonmisesvariate(0, 0), 5)}")
    file = etree.SubElement(domeImage, "File", filepath="0")
    roadCondition = etree.SubElement(environment, "RoadCondition", frictionScaleFactor="0", wetness="wetWithPuddles")
    season = etree.SubElement(environment, "Season", season="summer")

    startTrigger = etree.SubElement(event, "StartTrigger")
    conditionGroup = etree.SubElement(startTrigger, "ConditionGroup")
    condition = etree.SubElement(conditionGroup, "Condition", conditionEdge="rising", delay="2", name="condition")
    byValueCondition = etree.SubElement(condition, "ByValueCondition")
    simulationTimeCondition = etree.SubElement(byValueCondition, "SimulationTimeCondition", rule="greaterThan", value="4")

    return maneuverGroup

def weather_snow():
    maneuverGroup = etree.Element("ManeuverGroup", maximumExecutionCount="1", name="weather_maneuver_group")

    actors = etree.SubElement(maneuverGroup, "Actors", selectTriggeringEntities="false")
    maneuver = etree.SubElement(maneuverGroup, "Maneuver", name="Maneuver_weather_event")
    event = etree.SubElement(maneuver, "Event", maximumExecutionCount="1", name="weather_event", priority="overwrite")
    action = etree.SubElement(event, "Action", name="rainy_action")
    globalAction = etree.SubElement(action, "GlobalAction")
    environmentAction = etree.SubElement(globalAction, "EnvironmentAction")

    environment = etree.SubElement(environmentAction, "Environment", name="snow_day")
    timeOfDay = etree.SubElement(environment, "TimeOfDay", animation="true", dateTime="2000-01-01T12:00:00")
    weather = etree.SubElement(environment, "Weather", atmosphericPressure=f"{random.randint(80000, 120000)}", fractionalCloudCover="zeroOktas", temperature="293")
    sun = etree.SubElement(weather, "Sun", azimuth=f"{round(random.Random().vonmisesvariate(0, 0), 5)}", elevation=f"{round(random.Random().vonmisesvariate(0, 0) - math.pi, 5)}", illuminance="5.45")
    fog = etree.SubElement(weather, "Fog", visualRange=f"{random.randint(3, 10000)}")
    precipitation = etree.SubElement(weather, "Precipitation", precipitationIntensity=f"{random.randint(0, 1000000)}", precipitationType="snow")
    wind = etree.SubElement(weather, "Wind", direction=f"{round(random.Random().vonmisesvariate(0, 0), 5)}", speed=f"{random.randint(0, 1000)}")
    domeImage = etree.SubElement(weather, "DomeImage", azimuthOffset=f"{round(random.Random().vonmisesvariate(0, 0), 5)}")
    file = etree.SubElement(domeImage, "File", filepath="0")
    roadCondition = etree.SubElement(environment, "RoadCondition", frictionScaleFactor="0", wetness="wetWithPuddles")
    season = etree.SubElement(environment, "Season", season="winter")

    startTrigger = etree.SubElement(event, "StartTrigger")
    conditionGroup = etree.SubElement(startTrigger, "ConditionGroup")
    condition = etree.SubElement(conditionGroup, "Condition", conditionEdge="rising", delay="2", name="condition")
    byValueCondition = etree.SubElement(condition, "ByValueCondition")
    simulationTimeCondition = etree.SubElement(byValueCondition, "SimulationTimeCondition", rule="greaterThan", value="4")

    return maneuverGroup



if __name__ == "__main__":
    # base_dir = Path(__file__).resolve().parent.parent
    # data_dir = Path("/workspace/carla_docker_collection/carla_storage/junkwon_carla_workspace/Data/T_CAR/R_KR_PG_K-City")
    # input_file = data_dir / "tcar_t1_10.xosc"

    # tree = etree.parse(input_file)
    # root = tree.getroot()

    # maneuverGroup = weather_rain()
    # target_elements = tree.xpath("//Act")
    # if target_elements:
    #     target = target_elements[0]
    #     target.append(maneuverGroup)

    #     etree.indent(root, space="  ")

    #     etree.dump(root)
    #     tree.write(data_dir / "modified_example.xosc", pretty_print=True, encoding="utf-8", xml_declaration=True)
    root = weather_snow()
    etree.dump(root)