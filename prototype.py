from bluepy.btle import Peripheral,Scanner
import sys
from threading import Thread,Lock,Condition
import RPi.GPIO as GPIO
from time import sleep,time
import queue
import pygame
from gpiozero import Button

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(24,GPIO.IN)
GPIO.setup(14,GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setwarnings(False)
mac_1 = "ce:27:8e:27:17:22"
mac_2 = "d0:05:77:86:d5:bb"
mac_3 = "d7:d1:87:c8:f4:5b"
RSSI_beacon_1 = queue.Queue(3)
RSSI_beacon_2 = queue.Queue(3)
RSSI_beacon_3 = queue.Queue(3)
b1_arr = []
b2_arr = []
b3_arr = []
states = enumerate(['start','ramp','hallway','room2'])
current_state = 0

pygame.mixer.init()


    
def scan():
    while(True):
        scanner = Scanner()
        #devices = scanner.scan(1.0)
        devices = scanner.scan(1.0, passive=True)

        for i in devices:
            if (mac_1 in i.addr) :
                #print("enqueing rssi for " + mac_1 + " : " + str(i.rssi))
                RSSI_beacon_1.put(i.rssi,True,None)
            if (mac_2 in i.addr) :
                #print("enqueing rssi for " + mac_2 + " : " + str(i.rssi))
                RSSI_beacon_2.put(i.rssi,True,None)
            if (mac_3 in i.addr) :
                #print("enqueing rssi for " + mac_3 + " : " + str(i.rssi))
                RSSI_beacon_3.put(i.rssi,True,None)
        

def read(arr,queue,beacon_num,threshold):
    #sound = pygame.mixer.Sound(audio)
    proximity = False
    global current_state
    while True:
        #print(proximity)
        current_ave = 0
        arr.append(queue.get())
        for i in arr:
            current_ave +=  i
        print("RSSI average val. " + str(beacon_num) + " : " + str(current_ave/(len(arr))))
        if (current_state == 2 and beacon_num == 3 and current_ave/len(arr) > -82):
            audio('Exiting Room 121 1.wav')
            current_state = 1
        elif (current_ave/len(arr)) > threshold and not(proximity):
            if beacon_num == 2 and current_state != 2:
                if current_state == 1:
                    audio('121 side room to 2.wav')
                elif current_state == 3:
                    audio('121 side room to 1.wav')
                current_state = 2
            if beacon_num == 3 and current_state != 1:
                if current_state == 0:
                    audio('Approaching Room 1.wav')
                #elif current_state == 2:
                    #audio('Exiting Room 121 1.wav')
                current_state = 1
            if beacon_num == 1 and current_state != 3:
                current_state = 3
                print("say: about to exit room 121")
                audio('room3.wav')
            #else:
               # print("In proximity of "+beacon_num)
               # playing = sound.play()
               # proximity = True
               # while playing.get_busy():
                #    pygame.time.delay(100)
        elif (current_ave/len(arr)) <= threshold and proximity:
            print("Leaving "+beacon_num)
            proximity = False
        if (len(arr) >= 3): arr.pop(0)
        
            
            

        
def ultra_s(pin):
    GPIO.setup(14,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.output(18,True)
    sleep(0.00001)
    GPIO.output(18,False)

    StartTime = time()
    StopTime = time()
    
    while GPIO.input(24) == 0:
        StartTime = time()
        
    while GPIO.input(24) == 1:
        StopTime = time()
        
    TimeElapsed = StopTime - StartTime

    distance = (TimeElapsed * 34300) / 2

    print(str(int(distance)))
        
    if (distance < 400):
        prod_num(str(int(distance)))
    else :
        audio('No obstacles det 2.wav')

    GPIO.setup(14,GPIO.IN,pull_up_down = GPIO.PUD_UP)

def prod_num(digits):
    for i in digits:
        if i == "0":
            audio('0 2.wav')
        if i == "1":
            audio('1 1.wav')
        if i == "2":
            audio('2 1.wav')
        if i == "3":
            audio('3 1.wav')
        if i == "4":
            audio('4 2.wav')
        if i == "5":
            audio('5 1.wav')
        if i == "6":
            audio('six 2.wav')
        if i == "7":
            audio('7 1.wav')
        if i == "8":
            audio('eight-3_vf77gV7p.wav')
        if i == "9":
            audio('nine 1.wav')
    audio('centimeters away 1.wav')
            
            
def audio(file):
    sound = pygame.mixer.Sound(file)
    print("playing file: " + file)
    playing = sound.play()
    while playing.get_busy():
        pygame.time.delay(100)

GPIO.add_event_detect(14,GPIO.FALLING)
GPIO.add_event_callback(14,ultra_s)
    
def main():
    audio('Guide Pie Starti 1.wav')
    #audio('room3.wav')
    current_state = 0
    t1 = Thread(target=scan)
    t2 = Thread(target=read,args=(b1_arr,RSSI_beacon_1,1,-60))
    t3 = Thread(target=read,args=(b2_arr,RSSI_beacon_2,2,-60))
    t4 = Thread(target=read,args=(b3_arr,RSSI_beacon_3,3,-50))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()

    

if __name__ == '__main__':
    main()
