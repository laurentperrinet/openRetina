
from openRetina import openRetina
ret = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
ret.run()
