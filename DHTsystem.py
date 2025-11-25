import time
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
from keras.models import load_model  
import cv2  
import numpy as np
# from twilio.rest import Client
import tensorflow

np.set_printoptions(suppress=True)

account_sid = 'AC5d75bceb90d97bb67a368df215e6b363'
auth_token = '10c0e6ffbb6d0b4a3b04d66dfd61f3e6'
# from_number = '+15035059233'
# to_number = '+'
tensorflow.keras.utils.disable_interactive_logging()
client = Client(account_sid, auth_token)

model = load_model("C:/Users/hyunseok/EMSYS/EMSYS/keras_model.h5", compile=False)
class_names = [label.split()[1] for label in open("C:/Users/EMSYS/EMSYS/labels.txt", "r").readlines()]

camera = cv2.VideoCapture(0)

def send_temperature():
    sendData = f"TEMPERATURE=?\n"
    my_serial.write( sendData.encode() )

def send_humidity():
    sendData = f"HUMIDITY=?\n"
    my_serial.write( sendData.encode() )

def send_servo(digree):
    sendData = f"SERVO={digree}\n"
    my_serial.write( sendData.encode() )

def send_bright():
    sendData = f"BRIGHT=?\n"
    my_serial.write( sendData.encode() )

def send_buzzer(freq):
    sendData = f"BUZZER={freq}\n"
    my_serial.write( sendData.encode() )

serial_receive_data = ""

def serial_read_thread():
    global serial_receive_data
    while True:
        read_data = my_serial.readline()
        serial_receive_data = read_data.decode()
        
def send_temp_humi():
    t2 = threading.Timer(1, send_temp_humi)
    t2.daemon = True
    t2.start()
    send_temperature()
    time.sleep(0.2)
    send_humidity()
    time.sleep(0.2)
    send_bright()
    time.sleep(0.2)

def main():
    try:
        alarm_h = 1
        alarm_m = 10
        send_temp_humi()
        global serial_receive_data
        temperature = 0
        humidity = 0    
        gaseopgi = 0 # 0이 꺼진 상태 1이 켜진 상태
        bright_list = []
        bright_avr = 0
        master = 0
        thief_detected = 0
       
        while True:
            ret, image = camera.read()
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

            cv2.imshow("Webcam Image", image)
            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

            image = (image / 127.5) - 1

            prediction = model.predict(image)
            index = np.argmax(prediction)
            class_name = class_names[index]  # 이 부분에서 클래스명을 가져오도록 변경됨

            confidence_score = prediction[0][index]
             # print(" Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
            
            
            if "TEMPERATURE=" in serial_receive_data:
                temperature = float(serial_receive_data[12:])
                serial_receive_data = ""
            elif "HUMIDITY=" in serial_receive_data:
                humidity = float(serial_receive_data[9:])
                serial_receive_data = ""
            elif "BRIGHT=" in serial_receive_data:
                bright = int(serial_receive_data[7:10])
                bright_list.append(bright)
                serial_receive_data = ""

            if len(bright_list) > 3 :
                bright_avr = sum(bright_list[-4:-1]) / 3

   

            if index not in [0,1,3,4] and master == 0:
                if thief_detected == 0:
                    thief_detected = 1
                    print("THIEF Detected ",str(np.round(confidence_score * 100))[:-2], "%")
                    if master == 0:
                        print('THIEF!!!!!!!!!!!!!!!!!!!!!')
                        message = client.messages.create(
                            to=to_number,
                            from_=from_number,
                            body='not master!! call 112'
                        )
                        master = 1
            elif index in [0,1,3,4]:
                # notice = 1
                # prediction = ''

                # keyboard_input = cv2.waitKey(300)
                now = datetime.now()
                #print(now.minute)

                if now.hour >= 20 or now.hour <= 8:
                    
                    if len(bright_list) > 3 and bright_avr < 100:     
                        if temperature !=0 and humidity !=0 :
                            if gaseopgi == 0:
                                if (temperature >= 15.0 and temperature < 18.0) and humidity < 70.0 :  
                                    print("15--18") 
                                    for _ in range(4):
                                        send_servo(0)
                                        time.sleep(1.0)
                                        send_servo(100)
                                        time.sleep(1.0)
                                    gaseopgi = 1    
                                elif (temperature >= 18.0 and temperature < 21.0) and humidity < 60.0 :     
                                    print("18--21")                   
                                    for _ in range(4):
                                        send_servo(0)
                                        time.sleep(1.0)
                                        send_servo(100)
                                        time.sleep(1.0)
                                    gaseopgi = 1
                                elif (temperature >= 21.0 and temperature < 24.0) and humidity < 50.0 :                    
                                    print("21--24") 
                                    for _ in range(4):
                                        send_servo(0)
                                        time.sleep(1.0)
                                        send_servo(100)
                                        time.sleep(1.0)
                                    
                                    gaseopgi = 1
                                elif temperature >= 24.0  and humidity < 40.0 :                    
                                    print("24--") 
                                    for _ in range(4):
                                        send_servo(0)
                                        time.sleep(1.0)
                                        send_servo(100)
                                        time.sleep(1.0)
                                    gaseopgi = 1
                            
                            elif gaseopgi == 1:
                                if (temperature >= 15.0 and temperature < 18.0) and humidity > 80.0 :  
                                    print("high humidity") 
                                    send_servo(0)
                                    time.sleep(1.0)
                                    send_servo(100)
                                    time.sleep(1.0)
                                    gaseopgi = 0    
                                elif (temperature >= 18.0 and temperature < 21.0) and humidity > 70.0 :                        
                                    print("high humidity") 
                                    send_servo(0)
                                    time.sleep(1.0)
                                    send_servo(100)
                                    time.sleep(1.0)
                                    gaseopgi = 0
                                elif (temperature >= 21.0 and temperature < 24.0) and humidity > 60.0 :                    
                                    print("high humidity") 
                                    send_servo(0)
                                    time.sleep(1.0)
                                    send_servo(100)
                                    time.sleep(1.0)
                                    gaseopgi = 0
                                elif temperature >= 24.0  and humidity > 50.0 :                    
                                    print("high humidity") 
                                    send_servo(0)
                                    time.sleep(1.0)
                                    send_servo(100)
                                    time.sleep(1.0)
                                    gaseopgi = 0
                                
                                
                            print("온도:",temperature,"습도:",humidity, "조도:",bright)
                            temperature = 0
                            humidity = 0
                            if now.hour == alarm_h and now.minute == alarm_m :
                                send_buzzer(50)
                                alarm = 1
                                if "BUTTON1=CLICK" in serial_receive_data or "BUTTON2=CLICK" in serial_receive_data:
                                    send_buzzer(0)
                                    if gaseopgi == 1:
                                        send_servo(0)
                                        time.sleep(1.0)
                                        send_servo(100)
                                        time.sleep(1.0)
                                    master = 0
                                    thief_detected = 1
                                    notice = 1
                else:
                    
                    print("It's time to wake up")

                
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'Arduino Mega 2560' in p.description:
            print(f"{p} 포트에 연결하였습니다.")
            my_serial = serial.Serial(p.device, baudrate=9600, timeout=1.0)
            time.sleep(2.0)

    t1 = threading.Thread(target=serial_read_thread)
    t1.daemon = True
    t1.start()
    
    main()
    
    my_serial.close()