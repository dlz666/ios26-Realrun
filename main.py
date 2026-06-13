import signal
import asyncio
import logging
import coloredlogs
import os
from contextlib import suppress

from driver import location

from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

from init import init
from init import tunnel
from init import route

import run

import config


debug = os.environ.get("DEBUG", False)

# set logging level
coloredlogs.install(level=logging.INFO)
logging.getLogger('wintun').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('quic').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('zeroconf').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.cache').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.cache.pickle').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.python.diff').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('humanfriendly.prompts').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('blib2to3.pgen2.driver').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG if debug else logging.WARNING)


logger = logging.getLogger(__name__)


async def amain():
    # set level
    coloredlogs.install(level=logging.INFO)
    logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG)

    await init.init()
    logger.info("init done")

    # get route
    loc = route.get_route()
    logger.info(f"got route from {config.config.routeConfig}")

    # start the tunnel and connect to the device's RemoteServiceDiscovery
    logger.info("starting tunnel")
    async with tunnel.start_rsd() as rsd:
        logger.info("tunnel started")
        async with DvtProvider(rsd) as dvt:
            loc_sim = LocationSimulation(dvt)
            await loc_sim.connect()
            laps = getattr(config.config, "laps", 0)
            coord_system = getattr(config.config, "coordSystem", "wgs84")
            try:
                print(f"已开始模拟跑步，速度大约为 {config.config.v} m/s，坐标系 {coord_system}")
                if laps > 0:
                    print(f"将跑 {laps} 圈后自动停止，中途可按 Ctrl+C 退出")
                else:
                    print("会无限循环，按 Ctrl+C 退出")
                print("请勿直接关闭窗口，否则无法还原正常定位")
                await run.run(loc_sim, loc, config.config.v, laps, coord_system)
            finally:
                logger.debug("Start to clear location")
                with suppress(Exception):
                    await location.clear_location(loc_sim)
                logger.info("Location cleared")
    print("Bye")


def main():
    # turn Ctrl+C into a graceful stop so the location can be restored
    signal.signal(signal.SIGINT, lambda signum, frame: run.request_stop())
    asyncio.run(amain())


if __name__ == "__main__":
    main()
