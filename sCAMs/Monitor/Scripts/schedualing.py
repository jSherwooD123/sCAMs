from .record import Camera_Record
from Monitor.models import Camera
import threading, time

class Cycle:

    def __init__(self):
        self.cam_threads = []
        threading.Thread(target=self.recordingCycle,daemon=True).start()

    def recordingCycle(self):
        while True:

            # Get a queryset containing all camera objects with recording set as true
            active_primary_keys = Camera.objects.filter(active=True)
            # Get a list of all the objects primary keys
            list_apk = list(active_primary_keys.values_list('pk', flat=True))

            """This loop checks all the objects currently not recording video,
            if they are not recording but the related camera is active, then it restarts
            the recording.If it is active and recording it's taken out of the queryset as it 
            dosn't need to be added later If its not active then its added to the not_in array."""

            not_in = []
            for i,v in enumerate(self.cam_threads):
                # If pk is not in the list og active pks then its added to the remove list
                if v.pk not in list_apk:
                    not_in.append(i)
                # If it is active then the recording is restarted
                elif v.recording == False:
                     threading.Thread(target=self.cam_threads[i].startRecording,daemon=True).start()
                # if the object is recording its removed from the queryset 
                elif v.recording == True:
                    active_primary_keys.exclude(pk=v.pk)

            """This loop remove the object, at the index in provideded by the not_in list,
            from the list of recording objects"""

            for i,v in enumerate(not_in):
                del self.cam_threads[v-i]
                                  

            for cams in active_primary_keys:
                self.addThread(cams)

            time.sleep(60*10)

    def addThread(self,query_set):
        a = Camera_Record(f"{query_set.ip_address}:{query_set.port_num}",query_set.pk)
        self.cam_threads.append(a)
        threading.Thread(target=self.cam_threads[-1].startRecording,daemon=True).start()



        
        




    