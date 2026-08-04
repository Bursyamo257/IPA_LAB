import re
from netmiko import ConnectHandler

# Path สำหรับ SSH Private Key
Private_Key = r"C:\\Users\\KP\\Downloads\\SSH"

# ข้อมูลเฉพาะ Router R1 และ R2
routers = [
    {
        "device_type": "cisco_ios",
        "host": "172.31.3.4",
        "username": "cisco",
        "use_keys": True,
        "key_file": Private_Key,
        "name": "R1",
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
    {
        "device_type": "cisco_ios",
        "host": "172.31.3.5",
        "username": "cisco",
        "use_keys": True,
        "key_file": Private_Key,
        "name": "R2",
        "disabled_algorithms": dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"]),
    },
]

def main():
    for dev in routers:
        dev_name = dev.pop("name")
        print(f"==================================================")
        print(f" Connecting to {dev_name} ({dev['host']})...")
        print(f"==================================================")
        
        try:
            net_connect = ConnectHandler(**dev)
            
            # -------------------------------------------------------------
            # 1. ดึงข้อมูล Uptime จากคำสั่ง 'show version'
            # -------------------------------------------------------------
            version_output = net_connect.send_command("show version")
            
            # Regex Matching สำหรับ Uptime (เช่น "... uptime is 2 hours, 15 minutes")
            uptime_match = re.search(r".* uptime is (.*)", version_output)
            if uptime_match:
                uptime = uptime_match.group(1).strip()
            else:
                uptime = "Unknown"
                
            print(f" Router Uptime : {uptime}\n")

            # -------------------------------------------------------------
            # 2. ดึงข้อมูล Active Interfaces จาก 'show ip interface brief'
            # -------------------------------------------------------------
            intf_output = net_connect.send_command("show ip interface brief")
            
            # Regex Pattern หา Interface ที่มีสถานะ Status = 'up' และ Protocol = 'up'
            # รูปแบบคอลัมน์: <Interface> <IP-Address> <OK?> <Method> <Status> <Protocol>
            active_intf_pattern = r"^(\S+)\s+(\S+)\s+YES\s+\S+\s+up\s+up"
            
            # ค้นหาทุกบรรทัดที่ตรงตาม Pattern
            active_interfaces = re.findall(active_intf_pattern, intf_output, re.MULTILINE)

            print(f" Active Interfaces (Status: up / Protocol: up):")
            print(f" {'Interface':<25} {'IP Address':<15}")
            print(f" -----------------------------------------")
            
            if active_interfaces:
                for intf, ip in active_interfaces:
                    print(f" {intf:<25} {ip:<15}")
            else:
                print("  No active interfaces found.")

            net_connect.disconnect()
            print(f"\n--- Completed {dev_name} successfully ---\n")

        except Exception as e:
            print(f"Failed to check {dev_name}: {e}\n")

if __name__ == "__main__":
    main()