from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

# Path SSH Key
Private_Key = r"C:\\Users\\KP\\Downloads\\SSH"

# ==========================================
# 1. DEVICE DATA (ข้อมูลทั้งหมดอยู่ในนี้)
# ==========================================
devices = [
    # --------------------------------------
    # Switch (S1)
    # --------------------------------------
    {
        "conn": {
            "device_type": "cisco_ios",
            "host": "172.31.3.3",
            "username": "cisco",
            "use_keys": True,
            "key_file": Private_Key,
            "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
        },
        "name": "S1",
        "template_file": "templates/switch.j2",
        "data": {
            "vlans": [{"id": 101, "name": "Control-Data"}],
            "interfaces": [
                {"name": "GigabitEthernet0/1", "mode": "access", "vlan": 101},
                {"name": "GigabitEthernet1/1", "mode": "access", "vlan": 101},
            ],
            "acl_allowed_ips": [
                {"subnet": "172.31.3.0", "wildcard": "0.0.0.15"},
                {"subnet": "10.30.6.0", "wildcard": "0.0.0.255"},
            ],
        },
    },
    # --------------------------------------
    # Router 1 (R1)
    # --------------------------------------
    {
        "conn": {
            "device_type": "cisco_ios",
            "host": "172.31.3.4",
            "username": "cisco",
            "use_keys": True,
            "key_file": Private_Key,
            "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
        },
        "name": "R1",
        "template_file": "templates/router.j2",
        "data": {
            "ospf_configs": [
                {
                    "process_id": 10,
                    "vrf": "Management",
                    "networks": [{"subnet": "172.31.3.0", "wildcard": "0.0.0.15", "area": 15}],
                },
                {
                    "process_id": 20,
                    "vrf": "Control-Data",
                    "networks": [
                        {"subnet": "10.3.1.0", "wildcard": "0.0.0.3", "area": 15},
                        {"subnet": "10.3.1.8", "wildcard": "0.0.0.3", "area": 15},
                    ],
                },
            ],
            "ospf_interfaces": [
                {"name": "Loopback0", "process_id": 20, "area": 15}
            ],
            "acl_allowed_ips": [
                {"subnet": "172.31.3.0", "wildcard": "0.0.0.15"},
                {"subnet": "10.30.6.0", "wildcard": "0.0.0.255"},
            ],
        },
    },
    # --------------------------------------
    # Router 2 (R2)
    # --------------------------------------
    {
        "conn": {
            "device_type": "cisco_ios",
            "host": "172.31.3.5",
            "username": "cisco",
            "use_keys": True,
            "key_file": Private_Key,
            "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
        },
        "name": "R2",
        "template_file": "templates/router.j2",
        "data": {
            "ospf_configs": [
                {
                    "process_id": 10,
                    "vrf": "Management",
                    "networks": [{"subnet": "172.31.3.0", "wildcard": "0.0.0.15", "area": 15}],
                },
                {
                    "process_id": 20,
                    "vrf": "Control-Data",
                    "networks": [
                        {"subnet": "10.7.7.4", "wildcard": "0.0.0.3", "area": 15},
                        {"subnet": "10.7.7.8", "wildcard": "0.0.0.3", "area": 15},
                    ],
                    "default_originate": True,
                },
            ],
            "ospf_interfaces": [
                {"name": "Loopback0", "process_id": 20, "area": 15}
            ],
            "static_routes": [
                {"vrf": "Control-Data", "prefix": "0.0.0.0", "mask": "0.0.0.0", "next_hop": "dhcp"}
            ],
            "nat_config": {
                "inside_interfaces": ["GigabitEthernet0/1", "GigabitEthernet0/2"],
                "outside_interface": "GigabitEthernet0/3",
                "acl_id": 1,
                "acl_subnet": "10.7.7.0",
                "acl_wildcard": "0.0.0.255",
                "vrf": "Control-Data",
            },
            "acl_allowed_ips": [
                {"subnet": "172.31.3.0", "wildcard": "0.0.0.15"},
                {"subnet": "10.30.6.0", "wildcard": "0.0.0.255"},
            ],
            "dns_config": {
                "vrf": "Control-Data",
                "servers": ["192.168.122.1", "8.8.8.8", "1.1.1.1"],
            },
        },
    },
]

# ==========================================
# 2. MAIN EXECUTION LOGIC
# ==========================================
env = Environment(loader=FileSystemLoader("."))

def main():
    for dev in devices:
        dev_name = dev["name"]
        conn_params = dev["conn"]
        
        # โหลด Template จากโฟลเดอร์ templates/ และ Render
        template = env.get_template(dev["template_file"])
        config_text = template.render(dev["data"])
        
        # แยกข้อความให้ออกมาเป็น List ของแต่ละคำสั่ง
        config_commands = [line.strip() for line in config_text.strip().split("\n") if line.strip()]

        print(f"--- Connecting to {dev_name} ({conn_params['host']}) ---")
        try:
            net_connect = ConnectHandler(**conn_params)
            net_connect.enable()

            print(f"Applying configurations to {dev_name}...")
            output = net_connect.send_config_set(
                config_commands, 
                read_timeout=90, 
                cmd_verify=False
            )
            print(output)

            net_connect.save_config()
            net_connect.disconnect()
            print(f"--- Completed {dev_name} successfully ---\n")

        except Exception as e:
            print(f"Failed to configure {dev_name}: {e}\n")

if __name__ == "__main__":
    main()