from scenario.scenario import Scenario
from scenario.baseClass import Vehicle
from typing import Any

"""
TODO: Change the return setences so that LLM understands why it is not safe.
TODO: Look into the logic of safecheck functs
"""


def getInvolvedVehicles(sce:Scenario,laneID:str) -> dict[str,Vehicle]:
    """
        Input: sce, laneID
        Output: A dict containing "leadingCar" and "rearingCar" of class Vehicle
    """
    output = {'leadingCar':None,'rearingCar':None}
    ego = sce.vehicles["ego"]
    # Get involved cars
    laneVehicles = []
    for vk, vv in sce.vehicles.items():
        if vk != 'ego':
            if vv.lane_id == laneID:
                laneVehicles.append((vv, vv.lanePosition))
    # Sort by the position of involved vehicles
    laneVehicles.sort(key=lambda x: x[1])
    # Next we find the adjacent 2 vehicles of "ego", one leading and one rearing(if exists)
    leadingCarIdx = -1
    for i in range(len(laneVehicles)):
        vp = laneVehicles[i]
        if vp[1] >= ego.lanePosition:
            leadingCarIdx = i
            break
    if leadingCarIdx == -1:
        # This means there is no vehicle in front of "ego" on the concerning lane
        try:
            output['rearingCar'] = laneVehicles[-1][0]
            # This rearingCar is now the closest vehicle behind "ego"
        except IndexError:
            # This means the concerning lane is empty
            pass
    elif leadingCarIdx == 0:
        # This means there is no vehicle behind "ego" on the concerning lane
        output['leadingCar'] = laneVehicles[0][0]
    else:
        # This means there are both vehicles in front of and behind "ego" on the concerning lane
        output['leadingCar'] = laneVehicles[leadingCarIdx][0]
        output['rearingCar'] = laneVehicles[leadingCarIdx-1][0]
    return output

# Add the VEHICLE_LENGTH=5.0 to 6.0 so that this simple math will work.
def safeCheckLane(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 3.0
    VEHICLE_LENGTH = 5.0
    ego = sce.vehicles['ego']
    if veh.lanePosition >= ego.lanePosition:
            relativeSpeed = ego.speed - veh.speed
            if veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH > TIME_HEAD_WAY * relativeSpeed:
                return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`.",True
            else:
                return f"change lane to `{veh.lane_id}` may be conflict with `{veh.id}`, which is unacceptable.",False
    else:
        relativeSpeed = veh.speed - ego.speed
        if ego.lanePosition - veh.lanePosition - VEHICLE_LENGTH > TIME_HEAD_WAY * relativeSpeed:
            return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`.",True
        else:
            return f"change lane to `{veh.lane_id}` may be conflict with `{veh.id}`, which is unacceptable.",False

def safeCheckIdle(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 5.0
    VEHICLE_LENGTH = 5.0
    ego = sce.vehicles['ego']
    if veh.lanePosition >= ego.lanePosition:
        relativeSpeed = ego.speed - veh.speed
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH * 2
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Keep lane with current speed is safe with {veh.id}",True
        else:
            return f"Keep lane with current speed may be conflict with {veh.id}, you can consider changing lane or decelerating.",False
    else:
        relativeSpeed = veh.speed - ego.speed 
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Keep lane with current speed is safe with {veh.id}",True
        else:
            return f"Keep lane with current speed may be conflict with {veh.id}, you can consider changing lane or decelerating.",False

def safeCheckAccelerate(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 5.0
    VEHICLE_LENGTH = 5.0
    acceleration = 4.0
    ego = sce.vehicles['ego']
    if veh.lanePosition >= ego.lanePosition:
        relativeSpeed = ego.speed + acceleration - veh.speed
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH * 2
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Acceleration is safe with `{veh.id}`.",True
        else:
            return f"Acceleration may be conflict with `{veh.id}`, which is unacceptable.",False
    else:
        return f"Acceleration is safe with {veh.id}",True

def safeCheckDecelerate(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 3.0
    VEHICLE_LENGTH = 5.0
    deceleration = 3.0
    ego = sce.vehicles['ego']
    if veh.lanePosition <= ego.lanePosition:
        relativeSpeed = ego.speed - veh.speed - deceleration
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Deceleration with current speed is safe with {veh.id}",True
        else:
            return f"Deceleration with current speed may be conflict with {veh.id}",False
    else:
        return f"Deceleration with current speed is safe with {veh.id}, which is unacceptable.",True
    
# The following is not used 
def getSurroundingVehicles(sce:Scenario) -> list[Vehicle]:
    """
        Input: sce
        Output: the 9 surrounding vehicles of "ego"(if exists)
    """
    ego = sce.vehicles["ego"]
    involvedVehicles = []
    laneID = ego.lane_id
    
    match laneID:
        case "lane_0":
            involvedVehicles_0 = getInvolvedVehicles(sce,"lane_0")
            involvedVehicles_1 = getInvolvedVehicles(sce,"lane_1")
            for vv,vk in involvedVehicles_0.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_1.items():
                if vk is not None:
                    involvedVehicles.append(vk)
        case "lane_1":
            involvedVehicles_0 = getInvolvedVehicles(sce,"lane_0")
            involvedVehicles_1 = getInvolvedVehicles(sce,"lane_1")
            involvedVehicles_2 = getInvolvedVehicles(sce,"lane_2")
            for vv,vk in involvedVehicles_0.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_1.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_2.items():
                if vk is not None:
                    involvedVehicles.append(vk)
        case "lane_2":
            involvedVehicles_1 = getInvolvedVehicles(sce,"lane_1")
            involvedVehicles_2 = getInvolvedVehicles(sce,"lane_2")
            involvedVehicles_3 = getInvolvedVehicles(sce,"lane_3")
            for vv,vk in involvedVehicles_1.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_2.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_3.items():
                if vk is not None:
                    involvedVehicles.append(vk)
        case "lane_3":
            involvedVehicles_2 = getInvolvedVehicles(sce,"lane_2")
            involvedVehicles_3 = getInvolvedVehicles(sce,"lane_3")
            for vv,vk in involvedVehicles_2.items():
                if vk is not None:
                    involvedVehicles.append(vk)
            for vv,vk in involvedVehicles_3.items():
                if vk is not None:
                    involvedVehicles.append(vk)
        case _:
            pass
    return involvedVehicles