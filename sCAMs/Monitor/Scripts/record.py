import requests, threading, cv2, os
import numpy as np
from Monitor.models import Video, Camera
from datetime import datetime
from django.utils import timezone

class Camera_Record:

    def __init__(self,ip,camera_pk,frame_rate = 50, video_lendth = 1):
        self.url = f"http://{ip}/video_feed"
        self.pk = camera_pk
        self.frame_rate = frame_rate
        self.video_length = video_lendth
        self.recording = False
        self.save_loc = self.getSaveLoc()

    def startRecording(self):
        
        try:
            # Open a connection to the URL
            response = requests.get(self.url, stream=True)
     
            if response.status_code == 200:
                self.setActivity(True)
                bytes_data = bytes()  
                image_list = []
                now = datetime.now()
                c_dt = now.strftime("%d-%m-%Y_%H-%M-%S")

                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')  # Find the start of the JPEG image
                    b = bytes_data.find(b'\xff\xd9')  # Find the end of the JPEG image

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]  # Extract the JPEG image
                        bytes_data = bytes_data[b + 2:]  # Remove processed data

                        # Turn into jpeg and add to lisr
                        image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        image_list.append(image)

                    # Check if there is enough frames to create a minute video
                    if len(image_list) == self.frame_rate*60*self.video_length:
                    
                        #Create video saving thread
                        threading.Thread(target=self.saveVideo, daemon=True, args=(image_list, c_dt,)).start()

                        #Reset image list and datetime
                        image_list = []
                        now = datetime.now()
                        c_dt = now.strftime("%d-%m-%Y_%H-%M-%S")
        except:
            self.setActivity(False)

    def saveVideo(self,image_list,c_dt):

        height, width, _ = image_list[0].shape
 
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_loc = os.path.join(self.save_loc,f'output_video_{self.pk}_{c_dt}.mp4')
        output_video = cv2.VideoWriter(output_loc, fourcc, self.frame_rate, (width, height))
      
        # Write the images to the video
        for image in image_list:
                output_video.write(image)

        # Save images for human detection
        sample_rate = len(image_list) // self.frame_rate
        image_samples = image_list[::sample_rate]

        for i,v in enumerate(image_samples):
            output_loc = os.path.join(self.save_loc,f'Sample{i}_{self.pk}_{c_dt}.jpg')
            cv2.imwrite(output_loc,v)

        # Add video to database
        self.updateDB(f'{self.pk}_{c_dt}')

        # Release the video writer and destroy any remaining OpenCV windows
        output_video.release()
        cv2.destroyAllWindows()

    def updateDB(self, v_name):
        
        video = Video()
        video.v_name = v_name
        video.camera = Camera.objects.get(pk = self.pk)
        video.save()

    def setActivity(self, boolean):
        print(boolean)
        self.recording = True if boolean == True else False

        camera = Camera.objects.get(pk = self.pk)
        camera.active = boolean
        camera.last_active = timezone.now() 
        camera.save()

    def getSaveLoc(self):

        # Gets files directory
        curr_dir = os.getcwd()

        # Sets the location for where all the files from this camera are stored
        save_loc = os.path.join(curr_dir,'Storage',f'{self.pk}')

        # If makes directory if it dosnt already exist
        if not os.path.exists(save_loc):
            os.makedirs(save_loc)

        return save_loc
        



        


