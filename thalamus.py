
from openRetina import openRetina
ret = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
ret.run()

