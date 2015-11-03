
import subprocess
p = subprocess.Popen(['/usr/local/bin/ipython', 'photoreceptors.py'])
from openRetina import openRetina
thalamus = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
thalamus.run()
# 
# import sys
# sys.exit()
# 
# 
# from concurrent.futures import ThreadPoolExecutor
# from openRetina import openRetina
# thalamus = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
# phrs = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
# with ThreadPoolExecutor() as e:
#     e.submit(thalamus.run)
#     e.submit(phrs.run)
# 
# 
# import sys
# sys.exit()
# 
# 
# from openRetina import openRetina
# thalamus = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
# thalamus.run()
# 
# 
# 
# from multiprocessing.pool import ThreadPool
# pool = ThreadPool()
# 
# phrs = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
# 
# import multiprocessing
# p2 = multiprocessing.Process(target=thalamus.run, args=())
# print(p2, p2.is_alive())
# p2.start()
# print(p2, p2.is_alive())
# p1 = multiprocessing.Process(target=phrs.run, args=())
# print(p1, p1.is_alive())
# p1.start()
# print(p1, p1.is_alive())
# 
# import sys
# sys.exit()
# import threading
# p2 = threading.Thread(target=thalamus.run, args=())
# print(p2, p2.is_alive())
# p2.start()
# print(p2, p2.is_alive())
# p1 = threading.Thread(target=phrs.run, args=())
# print(p1, p1.is_alive())
# p1.start()
# print(p1, p1.is_alive())
# 
# threads = [p1, p2]
# for thread in threads:
#     thread.join()
# 
# import sys
# sys.exit()
# 
# from multiprocessing.popen_fork import Pool
# from openRetina import openRetina
# # thalamus = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
# # thalamus.run()
# class RetinaStreamer(threading.Thread):
#     def __init__(self):
#         super(RetinaStreamer, self).__init__()
#         self.phrs = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
#         self.event = threading.Event()
#         self.start()
# 
#     def run(self):
#         # This method runs in a background thread
#         self.phrs.run()
# 
# class ThalamusStreamer(threading.Thread):
#     def __init__(self):
#         super(ThalamusStreamer, self).__init__()
#         self.thalamus = openRetina(model=dict(layer='thalamus', input=['stream'], output=['display', 'capture']))
#         self.event = threading.Event()
#         self.start()
# 
#     def run(self):
#         # This method runs in a background thread
#         self.thalamus.run()
# 
# pool_lock = threading.Lock()
# pool =[RetinaStreamer(), ThalamusStreamer()]
