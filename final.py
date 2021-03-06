import cv2
import numpy as np
import time
import math
from operator import itemgetter, attrgetter, methodcaller
x_point=[]
y_point=[]
length = 23.5
breadth = 19.0
#load camera
cap = cv2.VideoCapture(2)
def nothing(x):
    pass

def get_pixel(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print x,y
        x_point.append(x)
        y_point.append(y)
            
#create calibration window
cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('Calibration',get_pixel)
cv2.resizeWindow('Calibration', 800, 600)

while(len(x_point)<=3):
    #get first frame
    ret, img = cap.read()
    cv2.putText(img,"Select points to define corners", (50,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0))
    cv2.imshow('Calibration',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if len(x_point)>3:
        cv2.destroyAllWindows()
        print "black",x_point[0],y_point[0]
        pts1 = np.float32([[x_point[0],y_point[0]],[x_point[1],y_point[1]],[x_point[2],y_point[2]],[x_point[3],y_point[3]]])
        pts2 = np.float32([[0,0],[800,0],[0,600],[800,600]])
        break

#create other windows
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 800, 600)

cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
cv2.resizeWindow('mask', 800, 600)

while(len(x_point)>3):
    tic=time.clock()
    # Capture frame-by-frame
    ret, img = cap.read()
    
    #image warp
    M = cv2.getPerspectiveTransform(pts1,pts2)
    imgc=cv2.warpPerspective(img,M,(800,600))

    #rotate image
    (h, w) = imgc.shape[:2]
    center = (w / 2, h / 2)
    obj = cv2.getRotationMatrix2D(center, 180, 1.0)
    imgc = cv2.warpAffine(imgc, obj, (w, h))
    
    #convert to hsv format
    hsv = cv2.cvtColor(imgc, cv2.COLOR_BGR2HSV)
    
    #set the values for green
    lower_green = np.array([40,100,100],dtype=np.uint8)
    upper_green = np.array([60,255,255],dtype=np.uint8) 
    
    #create a mask image 
    mask_img = cv2.inRange(hsv, lower_green, upper_green)
    
    resu = cv2.bitwise_and(imgc,imgc, mask= mask_img)                      
    result_image = cv2.cvtColor(resu, cv2.COLOR_BGR2GRAY)
    
    #image thresholding
    ret,thresh = cv2.threshold(result_image,120,255,0)
    
    #find contours            
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    num=0
    x1=0
    x2=0
    x3=0
    y1=0
    y2=0
    y3=0
    coord=list()
    for cnt in contours:
        if cv2.contourArea(cnt)>150:
            #print cv2.contourArea(cnt)
            M = cv2.moments(cnt)                                                                                                                                                                    
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            #print cX,cY
            #print "x = "+str((length/800)*cX)+"y = "+str((breadth/600)*cY)
            cv2.circle(img, (cX, cY), 50, (255, 0, 0), -1)
            num=num+1
            if num==1:
                x1=cX
                y1=cY
                coord.append([x1,y1])                
            if num==2:                   
                x2=cX
                y2=cY
                coord.append([x2,y2])
            if num==3:
                x3=cX
                y3=cY
                coord.append([x3,y3])
            
    
    if num==3:
        coord=sorted(coord,key=itemgetter(0))
        
        if(coord[1][1]>coord[2][1] and coord[1][0]>400):
            coord[1],coord[2]=coord[2],coord[1]
        if(coord[1][1]>coord[0][1] and coord[1][0]<400):
            coord[1],coord[0]=coord[0],coord[1]
            
        cv2.putText(result_image,"1", (coord[0][0],coord[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        
        cv2.putText(result_image,"2", (coord[2][0],coord[2][1]), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        cv2.putText(result_image,"3", (coord[1][0],coord[1][1]), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        x1=coord[0][0]*length/800
        x2=coord[2][0]*length/800
        x3=coord[1][0]*length/800
        y1=coord[0][1]*breadth/600
        y2=coord[2][1]*breadth/600
        y3=coord[1][1]*breadth/600
        cv2.putText(result_image,str((x1,y1)), (coord[0][0]-25,coord[0][1]+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        cv2.putText(result_image,str((x2,y2)), (coord[2][0]-25,coord[2][1]+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        cv2.putText(result_image,str((x3,y3)), (coord[1][0]-25,coord[1][1]+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        #print coord
        d12=math.sqrt(((x2-x1)**2)+((y2-y1)**2))
        d13=math.sqrt(((x3-x1)**2)+((y3-y1)**2))
        d23=math.sqrt(((x3-x2)**2)+((y3-y2)**2))
        #a312=math.acos(((d13**2)+(d12**2)-(d23**2))/2*d13*d12)
        print d12 , d13 , d23
        
    cv2.imshow('mask',result_image)
    cv2.imshow('image',imgc)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    toc=time.clock()
    #print tic-toc
    
    
    

