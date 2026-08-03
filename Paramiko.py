import paramiko
import os

# 1. กำหนดรายชื่ออุปกรณ์ R0-R2 และ S0-S1
devices = [
    {"name": "R0", "host": "172.31.3.1"},
    {"name": "R1", "host": "172.31.3.4"},
    {"name": "R2", "host": "172.31.3.5"},
    {"name": "S0", "host": "172.31.3.2"},
    {"name": "S1", "host": "172.31.3.3"},
]

username = "cisco"
key_filename = os.path.expanduser("C:\\Users\\KP\\Downloads\\SSH")

key = paramiko.RSAKey.from_private_key_file(key_filename)

for dev in devices:
    print(f"Connecting to {dev['name']} ({dev['host']})...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(
            hostname=dev["host"],
            username=username,
            pkey=key,
            look_for_keys=False,
            allow_agent=False,
            disabled_algorithms=dict(pubkeys=["rsa-sha2-256", "rsa-sha2-512"])
        )
        print(f"Successfully SSH to {dev['name']}")
        
        if dev["name"] == "R0":
            stdin, stdout, stderr = client.exec_command("show running-config")
            output = stdout.read().decode('utf-8')

            with open("R0-running.cfg", "w") as f:
                f.write(output)
            print("Saved R0 running-config to R0-running.cfg")
            
        client.close()
    except Exception as e:
        print(f"Failed to connect to {dev['name']}: {e}")