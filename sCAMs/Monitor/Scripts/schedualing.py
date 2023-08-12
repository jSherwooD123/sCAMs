from .record import Camera_Record
from Monitor.models import Camera
import threading, time

class Cycle:

    def __init__(self):
        self.cam_threads = []
        threading.Thread(target=self.recordingCycle,daemon=True).start()
        print('t1')

    def recordingCycle(self):
        while True:

            active_primary_keys = Camera.objects.filter(active=True)
            list_apk = list(active_primary_keys.values_list('pk', flat=True))
            print(list_apk)

            not_in = []
            for i,v in enumerate(self.cam_threads):
                if v.pk not in list_apk:
                    not_in.append(i)
                elif v.recording == False:
                     threading.Thread(target=self.cam_threads[i].startRecording(),daemon=True).start()
            print(self.cam_threads)
            count = 0
            for i in not_in:
                del self.cam_threads[i-0]
                count += 1                   

            for cams in active_primary_keys:
                print('t3')
                self.addThread(cams)

            time.sleep(60*10)

    def addThread(self,query_set):
        a = Camera_Record(f"{query_set.ip_address}:{query_set.port_num}",query_set.pk)
        self.cam_threads.append(a)
        threading.Thread(target=self.cam_threads[-1].startRecording(),daemon=True).start()



        
        




    