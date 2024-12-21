import paho.mqtt.client as mqtt

# Địa chỉ IP của Máy B (hoặc 'localhost' nếu Máy A và Máy B cùng mạng)
BROKER = "127.0.0.1"  # Thay bằng IP của máy B
PORT = 1883
TOPIC = "test/topic"
# Hàm callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    print(f"Kết nối thành công với mã: {"connect successfull!"}")
    client.subscribe(TOPIC)  # Đăng ký nhận tin nhắn từ topic này
# Hàm callback khi nhận tin nhắn
def on_message(client, userdata, msg):
    print(f"Nhận tin nhắn: {msg.payload.decode()} từ topic: {msg.topic}")
# Tạo MQTT client và cài đặt các callback
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Kết nối tới Broker Mosquitto trên Máy B
client.connect(BROKER, PORT, 60)
# Bắt đầu vòng lặp nhận tin nhắn
client.loop_start()
# Gửi tin nhắn đến topic
client.publish(TOPIC, "hello world")
# Dừng vòng lặp sau một thời gian
import time
time.sleep(2)

client.loop_stop()