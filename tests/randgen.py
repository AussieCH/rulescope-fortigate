"""Random rule base generator used to prove the shadow index equals brute force."""
import random
from typing import Any, Dict

from rulescope import model


def random_snapshot(n: int, seed: int) -> Dict[str, Any]:
    rnd = random.Random(seed)
    snap = model.empty_snapshot("config")
    snap["device"]["hostname"] = "RAND"
    for name, role in (("p1", "wan"), ("p2", "lan"), ("p3", "lan"), ("p4", "dmz")):
        snap["interfaces"][name] = model._interface(name, {"role": role})
    snap["zones"]["Z"] = ["p2", "p3"]
    nets = ["all"]
    snap["addresses"]["all"] = model._address("all", {})
    for i in range(40):
        a, b = rnd.randint(0, 3), rnd.randint(0, 3)
        mask = rnd.choice(["255.255.0.0", "255.255.255.0", "255.255.255.128", "255.255.255.255"])
        snap["addresses"][f"n{i}"] = model._address(f"n{i}", {"subnet": f"10.{a}.{b}.{rnd.choice([0, 128, 7])} {mask}"})
        nets.append(f"n{i}")
    for i in range(6):
        lo = rnd.randint(0, 200)
        snap["addresses"][f"r{i}"] = model._address(f"r{i}", {"type": "iprange", "start-ip": f"10.0.0.{lo}",
                                                              "end-ip": f"10.0.{rnd.randint(0, 3)}.{lo + 50}"})
        nets.append(f"r{i}")
    snap["addresses"]["fq"] = model._address("fq", {"type": "fqdn", "fqdn": "x.example"})
    nets.append("fq")
    for i in range(8):
        members = rnd.sample(nets[1:], rnd.randint(1, 4))
        snap["addrgrps"][f"g{i}"] = model._group(f"g{i}", {"member": members})
        nets.append(f"g{i}")
    snap["vips"]["v1"] = model._vip("v1", {"extip": "198.51.100.1", "mappedip": ["10.0.0.5"], "extintf": "p1"})
    nets.append("v1")
    svcs = ["ALL"]
    snap["services"]["ALL"] = model._service("ALL", {"protocol": "IP"})
    for i in range(25):
        lo = rnd.choice([22, 80, 443, 1000, 3389, 5000])
        snap["services"][f"s{i}"] = model._service(f"s{i}", {"tcp-portrange": f"{lo}-{lo + rnd.choice([0, 5, 100])}"})
        svcs.append(f"s{i}")
    snap["services"]["icmp"] = model._service("icmp", {"protocol": "ICMP"})
    svcs.append("icmp")
    ifs = ["p1", "p2", "p3", "p4", "Z", "any"]
    for pid in range(1, n + 1):
        raw = {
            "srcintf": [rnd.choice(ifs)], "dstintf": [rnd.choice(ifs)],
            "srcaddr": rnd.sample(nets, rnd.randint(1, 2)), "dstaddr": rnd.sample(nets, rnd.randint(1, 2)),
            "service": rnd.sample(svcs, rnd.randint(1, 2)), "schedule": rnd.choice(["always"] * 9 + ["night"]),
            "action": rnd.choice(["accept", "accept", "deny"]), "status": "enable",
        }
        if rnd.random() < 0.05:
            raw.update({"internet-service": "enable", "internet-service-name": ["Svc-A"], "dstaddr": []})
        if rnd.random() < 0.03:
            raw["srcaddr-negate"] = "enable"
        if rnd.random() < 0.05:
            raw["groups"] = ["staff"]
        snap["policies"].append(model._policy(pid, raw))
    return snap
