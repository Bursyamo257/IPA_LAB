from netmiko import ConnectHandler

USERNAME = "cisco"
PKEY_PATH = "C:\\Users\\KP\\Downloads\\SSH"

DEVICES = {
    "R1": "172.31.3.4",
    "R2": "172.31.3.5",
    "S1": "172.31.3.3",
}

DESCRIPTIONS = {
    "R1": {
        "Gi0/1": "Connect to PC",
        "Gi0/2": "Connect to G0/1 of R2",
    },
    "R2": {
        "Gi0/1": "Connect to G0/2 of R1",
        "Gi0/2": "Connect to G0/1 of S1",
        "Gi0/3": "Connect to WAN",
    },
    "S1": {
        "Gi0/1": "Connect to G0/2 of R2",
        "Gi1/1": "Connect to PC",
    },
}

def apply_descriptions():
    results = []
    for name, host in DEVICES.items():
        print(f"Connecting to {name} ({host}) to apply descriptions...")

        device_params = {
            "device_type": "cisco_ios",
            "host": host,
            "username": USERNAME,
            "use_keys": True,
            "key_file": PKEY_PATH,
            "allow_agent": False,
            "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
        }

        try:
            conn = ConnectHandler(**device_params)
            conn.enable()

            config_cmds = []
            for intf, desc in DESCRIPTIONS[name].items():
                config_cmds.extend([
                    f"interface {intf}",
                    f"description {desc}"
                ])

            output = conn.send_config_set(config_cmds)
            print(f"[{name}] Configuration applied successfully.")

            results.append({
                "device": name,
                "status": "success",
                "interfaces": DESCRIPTIONS[name]
            })
            conn.disconnect()

        except Exception as e:
            print(f"[{name}] Failed to configure: {e}")

            results.append({
                "device": name,
                "status": "failed",
                "error": str(e)
            })

if __name__ == "__main__":
    apply_descriptions()