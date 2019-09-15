# YAKS Face Recognition Demo
This is a relatively simple demo that shows how YAKS can be used to do face recognition as well as 
notification of recognised faces.

## Pre-requisite
Python 3,  pip3 and the yaks-python api.
Install the required python modules:

        $ pip3 install jsonschema jsonpickle argcomplete imutils opencv-python opencv-contrib-python face_recognition


## Step I -- Decide which YAKS instance to use
The simplest way to run the example is to use our online instance of YAKS available at **demo.yaks.is**.
Otherwise you can run a local instance. In the following we'll assume that the local instance is reachable
at the loopback address 127.0.0.1.

## Step II -- Prepare Your Data Set (optional)
The directory **dataset** contains some existing data-set for some of the members of the Advanced Technology Office in ADLINK, some famous Tennis Player, Soccer Player and Hollywood starts. The data-set are actually collections of faces pictures organized in subdirectories: **dataset/*category*/*name*/\*.jpg**
These data-set have already been transformed into face-signature databases (JSON format) in face-sig-db. 

If you want to generate those databases again (for instance because you added more pictures or a new data-set of pictures), it can be done as follows:

        $ python3 encode_faces.py --dataset dataset/tennis --detection-method cnn -o face-sig-db/tennis-db.json

## Step III -- Load the Data Set on YAKS
Now you should load each database (JSON file) on YAKS, to do so, depeding on the instance you decided to run, 
execute one of the following commands for each database:
                
        $ python3 load_face_db.py -d face-sig-db/tennis-db.json 

For using our demo YAKS do:

        $ python3 load_face_db.py -d face-sig-db/tennis-db.json -z demo.yaks.is

## Step IV -- Run the face detection component
This component reads frames from the camera, detects faces and publishes the faces images to YAKS.

        $ python3 detect_faces.py

For using our demo YAKS do:

        $ python3 detect_faces.py -z demo.yaks.is

## Step V -- Run the face recognition component
This component subscribes to faces images from the detecton component, and to face signatures 
from the dataset on YAKS, identifies received faces and publishes identifications to YAKS.

        $ python3 recognize_faces.py

For using our demo YAKS do:

        $ python3 recognize_faces.py -z demo.yaks.is

## Step VI -- Run the display component
This component subscribes to faces images from the detecton component, and to identifications 
from the face recognition component on YAKS and displays them.

        $ python3 display_faces.py

For using our demo YAKS do:

        $ python3 display_faces.py -z demo.yaks.is
