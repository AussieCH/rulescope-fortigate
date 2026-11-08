"""Benchmark: synthetic rule base of N policies, mostly sharing one interface pair (worst case).

    python3 tests/bench.py 5000
"""
import random
import sys
import time

sys.path.insert(0, ".")
from rulescope import checks, model  # noqa: E402


def synth(n: int, seed: int = 7) -> str:
    rnd = random.Random(seed)
    out = ["#config-version=FG100F-7.4.3-FW-build2573-240201:opmode=0:vdom=0",
           "config system global", '    set hostname "BENCH"', "end",
           "config system interface"]
    for name, role in (("port1", "wan"), ("port2", "lan"), ("port3", "dmz"), ("port4", "lan")):
        out += [f'    edit "{name}"', f"        set role {role}", "        set allowaccess ping", "    next"]
    out += ["end", "config firewall address"]
    nets = []
    for i in range(1500):
        a, b = rnd.randint(1, 30), rnd.randint(0, 255)
        mask = rnd.choice([24, 24, 28, 32, 32, 32])
        nets.append(f"N{i}")
        bits = (0xFFFFFFFF << (32 - mask)) & 0xFFFFFFFF
        m = ".".join(str((bits >> s) & 255) for s in (24, 16, 8, 0))
        out += [f'    edit "N{i}"', f"        set subnet 10.{a}.{b}.{rnd.randint(0, 255) if mask == 32 else 0} {m}", "    next"]
    out += ["end", "config firewall service custom"]
    svcs = []
    for i in range(300):
        p = rnd.randint(1, 65000)
        svcs.append(f"S{i}")
        out += [f'    edit "S{i}"', f"        set tcp-portrange {p}-{p + rnd.choice([0, 0, 10, 100])}", "    next"]
    out += ['    edit "ALL"', "        set protocol IP", "    next", "end", "config firewall policy"]
    pairs = [("port2", "port1")] * 8 + [("port2", "port3"), ("port3", "port2"), ("port4", "port1"), ("port1", "port3")]
    for pid in range(1, n + 1):
        si, di = rnd.choice(pairs)
        src = " ".join(f'"{x}"' for x in rnd.sample(nets, rnd.randint(1, 3)))
        dst = " ".join(f'"{x}"' for x in rnd.sample(nets, rnd.randint(1, 3)))
        svc = " ".join(f'"{x}"' for x in rnd.sample(svcs, rnd.randint(1, 4)))
        out += [f"    edit {pid}", f'        set name "r{pid}"', f'        set srcintf "{si}"', f'        set dstintf "{di}"',
                "        set action " + ("deny" if rnd.random() < 0.1 else "accept"),
                f"        set srcaddr {src}", f"        set dstaddr {dst}", '        set schedule "always"',
                f"        set service {svc}", "        set logtraffic all", "    next"]
    out.append("end")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    text = synth(n)
    t0 = time.time()
    snap = model.from_config(text)
    t1 = time.time()
    res = checks.analyze(snap)
    t2 = time.time()
    print(f"{n} policies: parse {t1 - t0:.2f}s, analyze {t2 - t1:.2f}s, findings {len(res['findings'])}")
