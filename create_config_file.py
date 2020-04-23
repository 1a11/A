import json

scheme = {'APIKey':'',\
          'ComputerID':'',\
          'ComputerName':''}

with open('config.json', 'w') as outfile:
    json.dump(scheme, outfile, indent=4)
