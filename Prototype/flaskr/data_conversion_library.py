def convert_kilogram_to_tonnes(kg):
  """This function converts kilograms to tones by multiplying the input which
  would be expected to be the kilograms by 0.001 to return tonnes

  Parameters:
  kg {float} -- the ammount of kilograms

  Returns:
  [float] -- the conversion of kilograms to tonnes
  """

  #the calculation for the function
  conversion = kg * 0.001
  
  return conversion



def litres_per_kilometre_to_litres_per_100km(litres):
  """This function coverts how many letres are being used per kilometre to 
  litres per 100 kilometres by multiplying the litre per kilomtre by 100
  
  Parameters:
  lires {float} -- the ammount of litres per kilometre

  Returns:
  [float] -- the conversion of litres per kilometres into litres per 100 kilometres
  """

  conversion = litres * 100

  return conversion



def kilometres_per_litre_to_litres_per_100km(km):
  """This function coverts how many kilometres per letre to litres per 100 
  kilometres by dividing the letres by the kilometres per letres then 
  multiplying by 100
  
  Parameters:
  km {float} -- the ammount of kilometres per litre

  Returns:
  [float] -- the conversion of kilometres per litre into litres per 100 kilometres
  """

  conversion = (1 / km) * 100
  
  return conversion



def metre_to_kilometre(metre):
  """This function converts metres to kilometres by multiplying the input 
  which would be expected to be the metres by 0.001 to return kilometres

  Parameters:
  metre {float} -- the ammount of metres

  Returns:
  [float] -- the conversion of metres to kilometres
  """

  conversion = metre * 0.001

  return conversion



#The code under this comment is used for testing
#print('Kilograms to tonnes = ' + str(convert_kilogram_to_tonnes(450)) + '. dummy value was 450')
#print('Litres per kilometre to per 100km = ' + str(litres_per_kilometre_to_litres_per_100km(2)) + '. dummy value was 2')
#print('Metres to kilomtres = ' + str(metre_to_kilometre(1000)) + '. dummy value was 1000')
#print('Kilometres per litre to litres per 100km = ' + str(kilometres_per_litre_to_litres_per_100km(2)) + '. dummy value was 2')


  