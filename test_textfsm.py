import pytest
from netmiko import ConnectHandler

USERNAME = "cisco"
PKEY_PATH = "C:\\Users\\KP\\Downloads\\SSH"


DEVICES = {
    "S1": "172.31.3.3",
    "R1": "172.31.3.4",
    "R2": "172.31.3.5",
}

def get_descriptions(ip):
    device_params = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": USERNAME,
        "use_keys": True,
        "key_file": PKEY_PATH,
        "allow_agent": False,
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    }
    
    conn = ConnectHandler(**device_params)
    conn.enable()
    
    rows = conn.send_command("show interfaces description", use_textfsm=True)
    conn.disconnect()
    
    assert isinstance(rows, list), f"TextFSM parsing failed, raw string received: {rows!r}"
    
    return {row["port"]: row["description"] for row in rows}

@pytest.fixture(scope="module")
def s1_descs():
    return get_descriptions(DEVICES["S1"])

@pytest.fixture(scope="module")
def r1_descs():
    return get_descriptions(DEVICES["R1"])

@pytest.fixture(scope="module")
def r2_descs():
    return get_descriptions(DEVICES["R2"])

def test_s1_interfaces(s1_descs):
    assert s1_descs["Gi0/1"] == "Connect to G0/2 of R2"
    assert s1_descs["Gi1/1"] == "Connect to PC"

def test_r1_interfaces(r1_descs):
    assert r1_descs["Gi0/1"] == "Connect to PC"
    assert r1_descs["Gi0/2"] == "Connect to G0/1 of R2"

def test_r2_interfaces(r2_descs):
    assert r2_descs["Gi0/1"] == "Connect to G0/2 of R1"
    assert r2_descs["Gi0/2"] == "Connect to G0/1 of S1"
    assert r2_descs["Gi0/3"] == "Connect to WAN"