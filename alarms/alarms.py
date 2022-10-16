import time
import requests

class Alarms:
    def __init__(self) -> None:
        self.ip = "192.168.0.9"

    def start_buzzer(self):
        requests.get(f"http://{self.ip}/BuzzerOn")
    
    def stop_buzzer(self):
        requests.get(f"http://{self.ip}/BuzzerOff")

    def flash_alarm_on(self, id=1):
        if id==1:
            nr = ""
        elif id == 2:
            nr = "2"

        requests.get(f"http://{self.ip}/FlashOn{nr}")

    def flash_alarm_off(self, id=1):
        if id==1:
            nr = ""
        elif id == 2:
            nr = "2"

        requests.get(f"http://{self.ip}/FlashOff{nr}")

if __name__ == "__main__":
    alert = Alarms()

    alert.start_buzzer()
    time.sleep(6)
    

    alert.flash_alarm_on(1)
    time.sleep(6)
    

    alert.flash_alarm_on(2)
    time.sleep(6)
    
