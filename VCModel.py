import time
import pymemcache

# ---------Run memcached!----------
shared = pymemcache.Client(('localhost', 11211))
lungVolume = 0


dataInterval = .01  # seconds between data transmissions

#sec
T_full = 2.5
T_hold = 1.5
T_out = 2.5
T_dwell = 1.5
Vt = 500  # ml
EndVolume = 15  # ml

inhaleState = True
holdState = False
exhaleState = False
dwellState = False

breathCounter = 0
volPerInterval = Vt / (T_full * (1/dataInterval))  # change in volume between data transmissions


def inhale():
    global lungVolume,Vt
    inhaleStartTime = time.time()
    while lungVolume < Vt:
        if time.time() > (inhaleStartTime + dataInterval) and lungVolume < Vt:
            lungVolume += volPerInterval
            shared.set('lungVolume', int(lungVolume))
            inhaleStartTime = time.time()


def hold():
    global T_hold, holdState
    holdStartTime = time.time()
    while time.time() < holdStartTime + T_hold:
        holdState = True


def exhale():
    global lungVolume, Vt
    exhaleStartTime = time.time()
    while lungVolume > 0:
        if time.time() > (exhaleStartTime + dataInterval) and lungVolume > 0:
            lungVolume -= volPerInterval
            shared.set('lungVolume', int(lungVolume))
            exhaleStartTime = time.time()


def dwell():
    global T_dwell, dwellState
    dwellStartTime = time.time()
    while time.time() < dwellStartTime + T_dwell:
        dwellState = True


while True:
    shared.set('breathCounter', breathCounter)
    if breathCounter < 3:
        breathCounter += 1
    else:
        breathCounter = 0

    if inhaleState:
        start = time.time()
        inhale()
        inhaleState = False
        holdState = True
        #print("Inhale time: {} seconds".format(round(time.time() - start, 2)))

    if holdState:
        start = time.time()
        hold()
        holdState = False
        exhaleState = True
        #print("Hold time: {} seconds".format(round(time.time() - start, 2)))

    if exhaleState:
        start = time.time()
        exhale()
        exhaleState = False
        dwellState = True
        #print("Exhale time: {} seconds".format(round(time.time() - start, 2)))

    if dwellState:
        start = time.time()
        dwell()
        dwellState = False
        inhaleState = True
        #print("Hold time: {} seconds".format(round(time.time() - start, 2)))







