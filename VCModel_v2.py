import time
import pymemcache
import math

# ---------Run memcached!----------
shared = pymemcache.Client(('localhost', 11211))
lungVolume = 0
flow = 0

dataInterval = .01  # seconds between data transmissions

# sec
T_full = 2.5
T_hold = 0
T_out = 2.5
T_dwell = 0
 # ml
EndVolume = 15  # ml

# -------------------------

R = 1     # Airway resistance
Vt = 400  # Volume
t = 2     # Inhale time
s = 5     # Graph ratio constant
BPM = 14
I_Ratio = 1
E_Ratio = 1

period = 60/BPM
V = Vt
inhaleTime = (period * (I_Ratio/(I_Ratio+E_Ratio)))
exhaleTime = (period * (E_Ratio/(I_Ratio+E_Ratio)))

#volumeMultiplier = 50

# -------------------------

flowMultiplier = 20
volumeMultiplier = 10000

inhaleState = True
holdState = False
exhaleState = False
dwellState = False

measuredInhaleTime = T_full
measuredExhaleTime = T_out
breathCounter = 0
volPerInterval = Vt / (T_full * (1 / dataInterval))  # change in volume between data transmissions
holdFlowPerInterval = volPerInterval / (T_full * (1 / dataInterval))
dwellFlowPerInterval = volPerInterval / (T_full * (1 / dataInterval))


def inhale():
    global lungVolume, Vt, volPerInterval, flow, flowMultiplier, holdFlowPerInterval, T_full, volumeMultiplier, measuredInhaleTime
    global V, s, t, period, inhaleTime
    flow = volPerInterval
    shared.set('flow', (flow * flowMultiplier))
    totalStart = time.time()
    inhaleStartTime = time.time()
    while lungVolume < Vt-3:
        if time.time() > (inhaleStartTime + dataInterval) and lungVolume < Vt:
            inhaleStartTime = time.time()
            x = time.time() - start

            #lungVolume += volPerInterval
            #lungVolume = lungVolume = (-.5 * (x - T_full) ** 2) * (Vt / T_full) + Vt + 1
            lungVolume = V*(1-math.e**(-(x*s)/inhaleTime))
            if lungVolume >= 0:
                shared.set('lungVolume', int(lungVolume))

            flow = (.5 * (x - T_full) ** 2)
            shared.set('flow', (flow * flowMultiplier))


def hold():
    global T_hold, holdState
    shared.set('flow', 0)
    holdStartTime = time.time()
    while time.time() < holdStartTime + T_hold:
        1 == 1


def exhale():
    global lungVolume, Vt, volPerInterval, flow, flowMultiplier, dwellFlowPerInterval, T_out
    global s, exhaleTime
    flow = -volPerInterval
    shared.set('flow', (flow * flowMultiplier))
    totalExhaleTime = time.time() + T_out
    exhaleStartTime = time.time()
    while lungVolume > 1:
        if time.time() > (exhaleStartTime + dataInterval) and lungVolume > 0:
            exhaleStartTime = time.time()
            x = time.time() - start
            # lungVolume -= volPerInterval
            #lungVolume = (.5 * (x - T_out) ** 2) * (Vt / T_out)
            lungVolume = Vt * math.e ** (-(x * s) / exhaleTime)
            shared.set('lungVolume', int(lungVolume))

            flow = (.5 * -(x - T_out) ** 2)
            shared.set('flow', (flow * flowMultiplier))


def dwell():
    global T_dwell, dwellState
    shared.set('flow', 0)
    dwellStartTime = time.time()
    while time.time() < dwellStartTime + T_dwell:
        1 == 1


while True:
    BPM = int(shared.get('Rate'))
    I_Ratio = float(shared.get('I'))
    E_Ratio = float(shared.get('E'))
    Vt = int(shared.get('Vt'))
    V = Vt
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
        measuredInhaleTime = time.time() - start
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
        measuredExhaleTime = time.time() - start
        #print("Exhale time: {} seconds".format(round(time.time() - start, 2)))

    if dwellState:
        start = time.time()
        dwell()
        dwellState = False
        inhaleState = True
        #print("Hold time: {} seconds".format(round(time.time() - start, 2)))
