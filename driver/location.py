async def set_location(loc_sim, lat: float, lng: float):
    await loc_sim.set(lat, lng)

async def clear_location(loc_sim):
    await loc_sim.clear()
