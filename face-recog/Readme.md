# YAKS Face Recognition Demo
This is a relatively simple demo that shows how YAKS can be used to do face recognition as well as 
notification of recognised faces.

## Step I -- Decide which YAKS instance to use
The simplest way to run the example is to use our online instance of YAKS available at **demo.yaks.is**.
Otherwise you can run a local instance. In the following we'll assume that the local instance is reachable
at the loopback address 127.0.0.1.

## Step II -- Prepare Your Data Set
The directory **dataset** contains some existing data-set for some of the members of the Advanced Technology Office in ADLINK, some famous Tennis Player, Soccer Player and Hollywood starts.

In order to use these data-set they have to be transformed info a face-signature database. This can be done as follows:

        $ python3 encode_faces.py --dataset dataset/tennis --detection-method cnn -o face-sig-db/tennis-db.sig

## Step III -- Load the Data Set on YAKS
Now you should load the  data-set on YAKS, to do so, depeding on the instance you decided to run, 
execute one of the following commands:
                
        $ python3 load_face_db.py --path //demo/cv/face/signature -d face-sig-db/adlink.json 

For using our demo YAKS do:

        $ python3 load_face_db.py --path //demo/cv/face/signature -d face-sig-db/adlink.json  -y demo.yaks.is



# Step IV -- Running the Face Recognition Application 
To start the face recognition do:

        $ python3 recognize.py --cascade haarcascade_frontalface_default.xml --path //demo/cv/face/signature

For using our demo YAKS do:

        $ python3 recognize.py --cascade haarcascade_frontalface_default.xml --yaks demo.yaks.is --path //demo/cv/face/signature


# Step V -- Subscribing to Detection Information

If you want to subscribe to the information of the face being detected, you can run
a yaks-sub application as follows:

        $ python3 yaks_sub.py -s //demo/cv/face/detected/* 

For using our demo YAKS do:      

        $ python3 yaks_sub.py -s //demo/cv/face/detected/* --yaks demo.yaks.is
