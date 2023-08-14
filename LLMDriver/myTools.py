from scenario.scenario import Scenario
from scenario.baseClass import Vehicle
from typing import Any

"""
TODO: Change the return setences so that LLM understands why it is not safe.
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
    VEHICLE_LENGTH = 6.0
    ego = sce.vehicles['ego']
    relativeSpeed = ego.speed - veh.speed
    # If two cars are too close, it is dangerous to do anything, regardless of their speed.
    if abs(veh.lanePosition - ego.lanePosition) <= VEHICLE_LENGTH:
        return f"change lane to `{veh.lane_id}` may be conflict with `{veh.id}`, which is unacceptable. You should consider other movements.",False

    if veh.lanePosition >= ego.lanePosition:
        # "ego" is behind veh, we consider if "ego" crushes veh
        
        if relativeSpeed >= 0 :
            if (veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH) > (TIME_HEAD_WAY * relativeSpeed):
                return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`. You can do this safely regardless other things.",True
            else:
                return f"change lane to `{veh.lane_id}` may be conflict with `{veh.id}`, which is unacceptable. You should consider other movements.",False
        else:
            return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`. You can do this safely regardless other things.",True
            

    else:
        # "ego" is ahead of veh, we consider if veh crushed "ego"
        if relativeSpeed <= 0:
            if (ego.lanePosition - veh.lanePosition - VEHICLE_LENGTH) > (TIME_HEAD_WAY * relativeSpeed):
                return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`. You can do this safely regardless other things.",True
            else:
                return f"change lane to `{veh.lane_id}` may be conflict with `{veh.id}`, which is unacceptable. You should consider other movements.",False
        else :
            return f"change lane to `{veh.lane_id}` is safe with `{veh.id}`. You can do this safely regardless other things.",True

def safeCheckIdle(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 5.0
    VEHICLE_LENGTH = 6.0
    ego = sce.vehicles['ego']
    if veh.lanePosition >= ego.lanePosition:
        relativeSpeed = ego.speed - veh.speed
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH * 1.5
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Keep lane with current speed is safe with {veh.id}. You can do this safely regardless other things.",True
        else:
            return f"Keep lane with current speed may be conflict with {veh.id}, you should consider changing lane or decelerating.",False
    else:
        relativeSpeed = veh.speed - ego.speed 
        distance = ego.lanePosition - veh.lanePosition - VEHICLE_LENGTH * 1.5
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Keep lane with current speed is safe with {veh.id}. You can do this safely regardless other things.",True
        else:
            return f"Keep lane with current speed may be conflict with {veh.id}, you should consider changing lane or decelerating.",False

def safeCheckAccelerate(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 5.0
    VEHICLE_LENGTH = 6.0
    acceleration = 4.0
    ego = sce.vehicles['ego']
    if veh.lanePosition >= ego.lanePosition:
        relativeSpeed = ego.speed + acceleration - veh.speed
        distance = veh.lanePosition - ego.lanePosition - VEHICLE_LENGTH * 1.5
        if distance > TIME_HEAD_WAY * relativeSpeed:
            return f"Acceleration is safe with {veh.id}. You can do this safely regardless other things.",True
        else:
            return f"Acceleration is not safe because it conflicts with {veh.id}. Please consider keeping current speed, decelerating, or changing to other lanes",False
    else:
        return f"Acceleration is safe with {veh.id}. You can do this safely regardless other things.",True

def safeCheckDecelerate(sce:Scenario,veh:Vehicle)->tuple[str,bool]:
    """
        Input: sce, veh
        Output: ans  : Reasons why this is not safe
                safe : Boolean Type, false is not safe, true is safe
    """
    TIME_HEAD_WAY = 3.0
    VEHICLE_LENGTH = 6.0
    deceleration = 3.0
    ego = sce.vehicles['ego']
    if veh.lanePosition <= ego.lanePosition:
        relativeSpeed = ego.speed - veh.speed - deceleration
        distance = ego.lanePosition - veh.lanePosition - 1.5*VEHICLE_LENGTH
        if distance + TIME_HEAD_WAY * relativeSpeed > 0:
            return f"Deceleration is safe. You can do this safely regardless other things.",True
        else:
            return f"Deceleration is not safe because it conflicts with {veh.id}. Please consider accelerating, keeping current speed or changing to other lanes",False
    else:
        return f"Deceleration is safe. You can do this safely regardless other things.",True
    
