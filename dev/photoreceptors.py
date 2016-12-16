
from openRetina import openRetina
phrs = openRetina(model=dict(layer='phrs', input=['picamera'], output=['stream']))
phrs.run()
