
from openRetina import openRetina
phrs = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
phrs.run()
