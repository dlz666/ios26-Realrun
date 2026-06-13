"""
run.py
automatically run the route
"""

"""坐标修正：路线点的坐标系由 config.yaml 的 coordSystem 指定
(wgs84/gcj02/bd09)，统一转换成 iOS 需要的 WGS-84"""
import math
import time
import random
import asyncio

from geopy.distance import geodesic

from driver import location
from util import coord

# set by the SIGINT handler so the running loop can stop gracefully and
# still clear the simulated location before exiting
_stop = False

def request_stop():
    global _stop
    _stop = True

def should_stop():
    return _stop

# get the ditance according to the latitude and longitude
def geodistance(p1, p2):
    return geodesic((p1["lat"],p1["lng"]),(p2["lat"],p2["lng"])).m

def smooth(start, end, i):
    import math
    i = (i-start)/(end-start)*math.pi
    return math.sin(i)**2

def randLoc(loc: list, d=0.000025, n=5):
    import random
    import time
    import math
    # deepcopy loc
    result = []
    for i in loc:
        result.append(i.copy())

    center = {"lat": 0, "lng": 0}
    for i in result:
        center["lat"] += i["lat"]
        center["lng"] += i["lng"]
    center["lat"] /= len(result)
    center["lng"] /= len(result)
    random.seed(time.time())
    for i in range(n):
        start = int(i*len(result)/n)
        end = int((i+1)*len(result)/n)
        offset = (2*random.random()-1) * d
        for j in range(start, end):
            distance = math.sqrt(
                (result[j]["lat"]-center["lat"])**2 + (result[j]["lng"]-center["lng"])**2
            )
            if 0 == distance:
                continue
            result[j]["lat"] +=  (result[j]["lat"]-center["lat"])/distance*offset*smooth(start, end, j)
            result[j]["lng"] +=  (result[j]["lng"]-center["lng"])/distance*offset*smooth(start, end, j)
    start = int(i*len(result)/n)
    end = len(result)
    offset = (2*random.random()-1) * d
    for j in range(start, end):
        distance = math.sqrt(
            (result[j]["lat"]-center["lat"])**2 + (result[j]["lng"]-center["lng"])**2
        )
        if 0 == distance:
            continue
        result[j]["lat"] +=  (result[j]["lat"]-center["lat"])/distance*offset*smooth(start, end, j)
        result[j]["lng"] +=  (result[j]["lng"]-center["lng"])/distance*offset*smooth(start, end, j)
    return result

def fixLockT(loc: list, v, dt):
    fixedLoc = []
    t = 0
    T = []
    T.append(geodistance(loc[1],loc[0])/v)
    a = loc[0].copy()
    b = loc[1].copy()
    j = 0
    while t < T[0]:
        xa = a["lat"] + j*(b["lat"]-a["lat"])/(max(1, int(T[0]/dt)))
        xb = a["lng"] + j*(b["lng"]-a["lng"])/(max(1, int(T[0]/dt)))
        fixedLoc.append({"lat": xa, "lng": xb})
        j += 1
        t += dt
    for i in range(1, len(loc)):
        T.append(geodistance(loc[(i+1)%len(loc)],loc[i])/v + T[-1])
        a = loc[i].copy()
        b = loc[(i+1)%len(loc)].copy()
        j = 0
        while t < T[i]:
            xa = a["lat"] + j*(b["lat"]-a["lat"])/(max(1, int((T[i]-T[i-1])/dt)))
            xb = a["lng"] + j*(b["lng"]-a["lng"])/(max(1, int((T[i]-T[i-1])/dt)))
            fixedLoc.append({"lat": xa, "lng": xb})
            j += 1
            t += dt
    return fixedLoc

async def run1(dvt, loc: list, v, coord_system, dt=0.2):
    fixedLoc = fixLockT(loc, v, dt)
    nList = (5, 6, 7, 8, 9)
    n = nList[random.randint(0, len(nList)-1)]
    fixedLoc = randLoc(fixedLoc, n=n)  # a path will be divided into n parts for random route
    clock = time.monotonic()
    for i in fixedLoc:
        if _stop:
            return
        lng, lat = coord.to_wgs84(i["lng"], i["lat"], coord_system)
        await location.set_location(dvt, lat=lat, lng=lng)
        delay = dt - (time.monotonic() - clock)
        if delay > 0:
            await asyncio.sleep(delay)
        clock = time.monotonic()

async def run(dvt, loc: list, v, laps, coord_system, d=15):
    """Run the route `laps` times (set laps <= 0 to loop forever)."""
    random.seed(time.time())
    lap = 0
    while not _stop and (laps <= 0 or lap < laps):
        vRand = 1000/(1000/v-(2*random.random()-1)*d)
        await run1(dvt, loc, vRand, coord_system)
        lap += 1
        if not _stop:
            if laps > 0:
                print(f"跑完第 {lap}/{laps} 圈")
            else:
                print("跑完一圈了")
    if not _stop and laps > 0:
        print(f"已完成全部 {laps} 圈")