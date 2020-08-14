import math

# Global variables to be used throughout the calculation
KILOGRAM_TO_TONNE_CONVERSION = 0.001
PER_100KM = 100
METRE_TO_KILOMETRE_CONVERSION = 0.001



def convert_kilogram_to_tonnes(kg):
  """This function converts kilograms to tones by multiplying the input which
  would be expected to be the kilograms by 0.001 to return tonnes"""

  #the calculation for the function
  convertion = kg * KILOGRAM_TO_TONNE_CONVERSION
  
  return convertion



def litres_per_kilometre_to_liters_per_100km(litres):
  """This function coverts how many letres are being used per kilometre to 
  litres per 100 kilometres by multiplying the litre per kilomtre by 100"""
  
  #the calculation for the function
  convertion = litres * PER_100KM

  return convertion



def kilometres_per_litre_to_litres_per_100km(km):
  """This function coverts how many kilometres per letre to litres per 100 
  kilometres by dividing the letres by the kilometres per letres then 
  multiplying by 100"""

  #the calculation for the function
  convertion = (1 / km) * PER_100KM
  
  return convertion



def metre_to_kilometre(metre):
  """This function converts metres to kilometres by multiplying the input 
  which would be expected to be the metres by 0.001 to return kilometres"""

  #the calculation for the function
  convertion = metre * METRE_TO_KILOMETRE_CONVERSION

  return convertion



#The code under this comment is used for testing
#print('Kilograms to tonnes = ' + str(convert_kilogram_to_tonnes(450)) + '. dummy value was 450')
#print('Litres per kilometre to per 100km = ' + str(litres_per_kilometre_to_liters_per_100km(2)) + '. dummy value was 2')
#print('Metres to kilomtres = ' + str(metre_to_kilometre(1000)) + '. dummy value was 1000')
#print('Kilometres per litre to litres per 100km = ' + str(kilometres_per_litre_to_litres_per_100km(2)) + '. dummy value was 2')


  