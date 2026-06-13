from contextlib import asynccontextmanager

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.remote.tunnel_service import CoreDeviceTunnelProxy, start_tunnel
from pymobiledevice3.remote.common import TunnelProtocol
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService


@asynccontextmanager
async def start_rsd():
    """Establish a CoreDevice tunnel over USB and yield a connected RSD.

    iOS 17.4+ / iPadOS 26 use the lockdown-based CoreDeviceProxy tunnel
    (TCP) instead of the old RemoteService QUIC tunnel.
    """
    lockdown = await create_using_usbmux()
    proxy = await CoreDeviceTunnelProxy.create(lockdown)
    async with start_tunnel(proxy, protocol=TunnelProtocol.TCP) as tunnel_result:
        rsd = RemoteServiceDiscoveryService((tunnel_result.address, tunnel_result.port))
        await rsd.connect()
        try:
            yield rsd
        finally:
            await rsd.close()
