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
                
        $ python3 load_face_db.py --path /demo/cv/face/signature -d face-sig-db/tennis-db.json 

For using our demo YAKS do:

        $ python3 load_face_db.py --path /demo/cv/face/signature -d face-sig-db/tennis-db.json  -y demo.yaks.is



# Step IV -- Running the Face Recognition Application 
To start the face recognition do:

        $ python3 recognize.py --cascade haarcascade_frontalface_default.xml --faces /demo/cv/face/signature --recog /demo/cv/face/recognized

For using our demo YAKS do:

        $ python3 recognize.py --cascade haarcascade_frontalface_default.xml --yaks demo.yaks.is --faces /demo/cv/face/signature --recog /demo/cv/face/recognized

The face recognition demo will load the faces signatures stored in Yaks under **/demo/cv/face/signature/\*\*** and compare each detected face to those signatures. The name of recognized faces will be published into Yaks as a list of name with the key **/demo/cv/face/recognized**.

# Step V -- Subscribing to Detection Information

If you want to subscribe to the information of the face being recognized, you can run
a yaks-sub application as follows:

        $ python3 yaks_sub.py -s /demo/cv/face/recognized 

For using our demo YAKS do:      

        $ python3 yaks_sub.py -s /demo/cv/face/recognized --yaks demo.yaks.is
