"""Write a CM1 input_sounding: Weisman-Klemp thermodynamics + a tornado-favourable hodograph.

python mksnd.py OUT [qv0_gkg] [r_low] [z_curve] [u_total]
Prints Bunkers right-mover motion, 0-1 km and 0-3 km SRH, MLCAPE-ish surface CAPE.
(Reconstructed 2026-11-11 from the Colab copy lost when the VM was recycled.)
"""
import math, sys

g, cp, rd, rv, p00 = 9.81, 1004.0, 287.04, 461.5, 1.0e5
out = sys.argv[1]
qv0 = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0      # g/kg mixed-layer cap (WK uses 14)
r_low = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0    # quarter-circle radius (m/s)
z_curve = float(sys.argv[4]) if len(sys.argv) > 4 else 1000.0  # depth of curved part (m)
u_top = float(sys.argv[5]) if len(sys.argv) > 5 else 32.0    # u at 6 km (m/s)

z_tr, th0, th_tr, t_tr = 12000.0, 300.0, 343.0, 213.0
dz = 50.0
zs = [i * dz for i in range(int(20000 / dz) + 1)]


def theta(z):
    if z <= z_tr:
        return th0 + (th_tr - th0) * (z / z_tr) ** 1.25
    return th_tr * math.exp(g / (cp * t_tr) * (z - z_tr))


def rh(z):
    return 1.0 - 0.75 * (z / z_tr) ** 1.25 if z <= z_tr else 0.25


def qsat(p, t):
    es = 611.2 * math.exp(17.67 * (t - 273.15) / (t - 29.65))
    return 0.622 * es / (p - es)


# hydrostatic integration in Exner, iterate qv
pi = [1.0]
qv = []
for k, z in enumerate(zs):
    if k > 0:
        thv_a = theta(zs[k - 1]) * (1 + 0.61 * qv[k - 1])
        thv_b = theta(z) * (1 + 0.61 * qv[k - 1])
        pi.append(pi[-1] - g * dz / (cp * 0.5 * (thv_a + thv_b)))
    p = p00 * pi[k] ** (cp / rd)
    t = theta(z) * pi[k]
    qv.append(min(rh(z) * qsat(p, t), qv0 / 1000.0))


def wind(z):
    """Quarter circle 0..z_curve (u from -r to 0, v from 0 to r), then straight to (u_top, r) at 6 km."""
    if z <= z_curve:
        a = 0.5 * math.pi * z / z_curve
        return -r_low * math.cos(a), r_low * math.sin(a)
    if z <= 6000.0:
        f = (z - z_curve) / (6000.0 - z_curve)
        return f * u_top, r_low
    return u_top, r_low


uv = [wind(z) for z in zs]


def mean_wind(z0, z1):
    sel = [w for z, w in zip(zs, uv) if z0 <= z <= z1]
    return sum(w[0] for w in sel) / len(sel), sum(w[1] for w in sel) / len(sel)


um, vm = mean_wind(0, 6000)
u05, v05 = mean_wind(0, 500)
u6, v6 = mean_wind(5500, 6000)
su, sv = u6 - u05, v6 - v05
mag = math.hypot(su, sv)
cx, cy = um + 7.5 * sv / mag, vm - 7.5 * su / mag   # Bunkers right mover


def srh(ztop):
    h = 0.0
    for k in range(len(zs) - 1):
        if zs[k + 1] > ztop:
            break
        (u1, v1), (u2, v2) = uv[k], uv[k + 1]
        h += (u2 - cx) * (v1 - cy) - (u1 - cx) * (v2 - cy)
    return h


with open(out, "w") as f:
    psfc = p00 * pi[0] ** (cp / rd) / 100.0
    f.write(f"{psfc:10.3f} {theta(0):10.3f} {qv[0] * 1000:10.4f}\n")
    for z, q, (u, v) in zip(zs[1:], qv[1:], uv[1:]):
        f.write(f"{z:10.1f} {theta(z):10.4f} {q * 1000:10.5f} {u:9.3f} {v:9.3f}\n")

p0 = p00 * pi[0] ** (cp / rd)
e0 = qv[0] * p0 / (0.622 + qv[0])
td = 243.5 / (17.67 / math.log(e0 / 611.2) - 1.0) + 273.15
lcl = 125.0 * (theta(0) * pi[0] - td)
print(f"wrote {out}; qv_sfc={qv[0]*1000:.2f} g/kg; storm motion (Bunkers RM) umove={cx:.2f} vmove={cy:.2f}")
print(f"SRH 0-1 km = {srh(1000):.0f} m2/s2, 0-3 km = {srh(3000):.0f} m2/s2; 0-6 km shear = {mag:.1f} m/s; approx LCL = {lcl:.0f} m")
