def energy_charges(units):
    slabs = [(100, 10), (100, 15), (100, 20), (None, 30)]
    remaining = units
    total = 0
    for size, rate in slabs:
        if size is None or remaining <= size:
            total += remaining * rate
            break
        total += size * rate
        remaining -= size
    return total

units = 1450 - 1200
energy = energy_charges(units)
gst = energy * 0.17
total = energy + gst + 35

print("Units :", units)
print("Energy: Rs", energy)
print("GST   : Rs", gst)
print("Total : Rs", total)