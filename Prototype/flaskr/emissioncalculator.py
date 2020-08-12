import requests
import json
import math
import maproutes


  
def setLoadWeight(load):
    fLoad=load

def setDistance(dist):
    distance=dist
 
def getResult():
    result = emissionCalculate()
    return result

def emissionCalculate():
    energyConstant=38.6
 
    emissionFactorCarbon=69.9
    emissionFactorMethane=0.06
    emissionFactorNitro=0.5

    fuelEconomy=2.1

    distance=maproutes.getLengthOfRoute()

    fuelEconomyDecrease=(fLoad*1.1)*fuelEconomy

    finalFuelEconomy=fuelEconomy-fuelEconomyDecrease

    TruckLoaded_EmissionCO=(distance*energyConstant*emissionFactorCarbon*2)/(1000*1000*finalFuelEconomy)
    TruckLoaded_EmissionCH=(distance*energyConstant*emissionFactorMethane*2)/(1000*1000*finalFuelEconomy)
    TruckLoaded_EmissionNO=(distance*energyConstant*emissionFactorNitro*2)/(1000*1000*finalFuelEconomy)
    
    TruckEmpty_EmissionCO =(distance*energyConstant*emissionFactorCarbon*2)/(1000*1000*FuelEconomy)
    TruckEmpty_EmissionCH =(distance*energyConstant*emissionFactorMethane*2)/(1000*1000*FuelEconomy)
    TruckEmpty_EmissionNO =(distance*energyConstant*emissionFactorNitro*2)/(1000*1000*FuelEconomy)

    FinalEmissionCO=TruckLoaded_EmissionCO+TruckEmpty_EmissionCO
    FinalEmissionCH=TruckLoaded_EmissionCH+TruckEmpty_EmissionCH
    FinalEmissionNO=TruckLoaded_EmissionNO+TruckEmpty_EmissionNO

    return {'CO': FinalEmissionCO, 'CH':FinalEmissionCH, 'NO':FinalEmissionNO}
