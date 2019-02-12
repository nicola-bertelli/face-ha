import time
import picamera
import yaml

file_configurazione = "/home/pi/riconoscimento/config.yaml"
with open(file_configurazione, 'r') as ymlfile:
    configurazione = yaml.load(ymlfile)

risoluzione_x = configurazione['stato_camera']['risoluzione']['x']
risoluzione_y = configurazione['stato_camera']['risoluzione']['y']
rotazione = configurazione['stato_camera']['rotazione']['gradi']

camera = picamera.PiCamera()
camera.resolution = (risoluzione_x, risoluzione_y)
camera.rotation = (rotazione)
try:
    camera.start_preview()
    time.sleep(3)
    camera.capture('immagine.jpg')
    camera.stop_preview()
finally:
    camera.close()
