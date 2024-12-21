import paho.mqtt.client as mqtt


# Cấu hình MQTT broker
BROKER = "127.0.0.1"  # Địa chỉ IP của máy chạy MQTT broker
PORT = 1883
TOPIC = "test/topic"
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối thành công đến broker!")
        client.subscribe(TOPIC)
        print(f"Đã đăng ký topic: {TOPIC}")
    else:
        print(f"Kết nối thất bại, mã lỗi: {rc}")
def on_message(client, userdata, msg):
    print(f"Nhận tin nhắn từ topic {msg.topic}: {msg.payload.decode()}")
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Đang kết nối tới broker...")
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
