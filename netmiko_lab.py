from netmiko import ConnectHandler

Private_Key = r"C:\\Users\\KP\\Downloads\\SSH"

devices = [
    {
        "device_type": "cisco_ios",
        "host": "172.31.3.3",
        "username": "cisco",
        "use_keys": True,
        "key_file": Private_Key,
        "name": "S1",
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"])
    },
    {
        "device_type": "cisco_ios",
        "host": "172.31.3.4",
        "username": "cisco",
        "use_keys": True,
        "key_file": Private_Key,
        "name": "R1",
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"])
    },
    {
        "device_type": "cisco_ios",
        "host": "172.31.3.5",
        "username": "cisco",
        "use_keys": True,
        "key_file": Private_Key,
        "name": "R2",
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"])
    },
]

s1_commands = [
    "vlan 101",
    "name Control-Data",
    "exit",
    "interface GigabitEthernet0/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
    "interface GigabitEthernet1/1",
    "switchport mode access",
    "switchport access vlan 101",
    "no shutdown",
    "access-list 10 permit 172.31.3.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 15",
    "access-class 10 in"
]

r1_commands = [
    "router ospf 10 vrf Management",
    "network 172.31.3.0 0.0.0.15 area 15",
    "exit",
    "router ospf 20 vrf Control-Data",
    "network 10.3.1.0 0.0.0.3 area 15",
    "network 10.3.1.8 0.0.0.3 area 15",
    "exit",
    "interface Loopback0",
    "ip ospf 20 area 15",
    "exit",
    "access-list 10 permit 172.31.3.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 15",
    "access-class 10 in"
]

r2_commands = [
    "router ospf 10 vrf Management",
    "network 172.31.3.0 0.0.0.15 area 15",
    "exit",
    "router ospf 20 vrf Control-Data",
    "network 10.7.7.4 0.0.0.3 area 15",
    "network 10.7.7.8 0.0.0.3 area 15",
    "default-information originate always",
    "exit",
    "interface Loopback0",
    "ip ospf 20 area 15",
    "exit",
    "ip route vrf Control-Data 0.0.0.0 0.0.0.0 dhcp",
    "interface GigabitEthernet0/1",
    "ip nat inside",
    "interface GigabitEthernet0/2",
    "ip nat inside",
    "interface GigabitEthernet0/3",
    "ip nat outside",
    "exit",
    "access-list 1 permit 10.7.7.0 0.0.0.255",
    "ip nat inside source list 1 interface GigabitEthernet0/3 vrf Control-Data overload",
    "access-list 10 permit 172.31.3.0 0.0.0.15",
    "access-list 10 permit 10.30.6.0 0.0.0.255",
    "line vty 0 15",
    "access-class 10 in",
    "exit",
    "ip dns server",
    "ip domain-lookup",
    "ip name-server vrf Control-Data 192.168.122.1",
    "ip name-server vrf Control-Data 8.8.8.8",
    "ip name-server vrf Control-Data 1.1.1.1",
]

config_map = {
    "S1": s1_commands,
    "R1": r1_commands,
    "R2": r2_commands,
}

def main():
    for dev in devices:
        dev_name = dev.pop("name")
        print(f"--- Connecting to {dev_name} ({dev['host']}) ---")
        try:
            net_connect = ConnectHandler(**dev)
            net_connect.enable()

            print(f"Applying configurations to {dev_name}...")
            output = net_connect.send_config_set(config_map[dev_name])
            print(output)

            net_connect.save_config()
            net_connect.disconnect()
            print(f"--- Completed {dev_name} successfully ---\n")

        except Exception as e:
            print(f"Failed to configure {dev_name}: {e}\n")

if __name__ == "__main__":
    main()