import time
import pymemcache
import math

# ---------Run memcached!----------
shared = pymemcache.Client(('localhost', 11211))
lungVolume = 0
flow = 0


dataInterval = .01  # seconds between data transmissions

#sec
T_full = 2.5
T_hold = 1.5
T_out = 2.5
T_dwell = 1.5
Vt = 500  # ml
EndVolume = 15  # ml
flowMultiplier = 20

inhaleState = True
holdState = False
exhaleState = False
dwellState = False

breathCounter = 0
volPerInterval = Vt / (T_full * (1/dataInterval))  # change in volume between data transmissions
holdFlowPerInterval = volPerInterval / (T_full * (1 / dataInterval))
dwellFlowPerInterval = volPerInterval / (T_full * (1 / dataInterval))


def inhale():
    global lungVolume, Vt, volPerInterval, flow, flowMultiplier, holdFlowPerInterval, T_full
    flow = volPerInterval
    shared.set('flow', (flow * flowMultiplier))
    start = time.time()
    inhaleStartTime = time.time()
    while lungVolume < Vt:
        if time.time() > (inhaleStartTime + dataInterval) and lungVolume < Vt:
            inhaleStartTime = time.time()
            lungVolume += volPerInterval
            shared.set('lungVolume', int(lungVolume))
            #flow += holdFlowPerInterval  # log function here
            #print(time.time() - start)
            #flow = math.log(time.time() - start) * -2
            flow = (.5 * ((time.time() - start) - T_full) ** 2)
            shared.set('flow', (flow * flowMultiplier))


def hold():
    global T_hold, holdState
    shared.set('flow', 0)
    holdStartTime = time.time()
    while time.time() < holdStartTime + T_hold:
        1==1


def exhale():
    global lungVolume, Vt, volPerInterval, flow, flowMultiplier, dwellFlowPerInterval, T_out
    flow = -volPerInterval
    shared.set('flow', (flow * flowMultiplier))
    totalExhaleTime = time.time() + T_out
    exhaleStartTime = time.time()
    while lungVolume > 0:
        if time.time() > (exhaleStartTime + dataInterval) and lungVolume > 0:
            exhaleStartTime = time.time()
            lungVolume -= volPerInterval
            shared.set('lungVolume', int(lungVolume))
            #flow -= dwellFlowPerInterval
            #flow = math.log(time.time()-totalExhaleTime)
            flow = (.5 * -((time.time() - start) - T_out) ** 2)
            shared.set('flow', (flow * flowMultiplier))


def dwell():
    global T_dwell, dwellState
    shared.set('flow', 0)
    dwellStartTime = time.time()
    while time.time() < dwellStartTime + T_dwell:
        1==1


while True:
    shared.set('breathCounter', breathCounter)
    if breathCounter < 6:
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







