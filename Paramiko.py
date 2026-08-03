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

# 2. วนลูปเชื่อมต่อแต่ละอุปกรณ์
for device in devices:
    print(f"==========================================")
    print(f"Connecting to {device['name']} ({device['host']})...")
    
    # สร้าง Paramiko SSHClient Object
    client = paramiko.SSHClient()
    
    # ยอมรับ Host Key อัตโนมัติ (สำหรับระบบแล็บ)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 3. เรียกใช้งาน client.connect() โดยใช้ key_filename สำหรับ Public Key Auth
        client.connect(
            hostname=device["host"],
            username=username,
            key_filename=key_filename,  # ระบุ SSH Private Key File
            port=22,
            timeout=10,
            look_for_keys=True,
            allow_agent=True
        )
        print(f"Successfully connected to {device['name']}!")
        
        # ทดสอบส่งคำสั่งตรวจสอบสถานะ
        stdin, stdout, stderr = client.exec_command("show ip interface brief")
        output = stdout.read().decode('utf-8')
        print(f"--- Output from {device['name']} ---")
        print(output)
        
    except Exception as e:
        print(f"Failed to connect to {device['name']}: {e}\n")
    finally:
        client.close()