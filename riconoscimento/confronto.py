
import yaml
import face_recognition
import picamera
import numpy as np
import time
import socket
import paho.mqtt.publish as mqtt


file_configurazione = "/home/pi/riconoscimento/config.yaml"
with open(file_configurazione, 'r') as ymlfile:
    configurazione = yaml.load(ymlfile)

risoluzione_x = configurazione['stato_camera']['risoluzione']['x']
risoluzione_y = configurazione['stato_camera']['risoluzione']['y']
rotazione = configurazione['stato_camera']['rotazione']['gradi']
ip_mqtt = configurazione['mqtt']['ip_server']

print("DATI DI CONFIGURAZIONE MQTT:")
print("risolizione x: " + str(risoluzione_x))
print("risoluzione y: " + str(risoluzione_y))
print("rotazione camera: " + str(rotazione))
print("indirizzo ip server mqtt: " + ip_mqtt)


# NOTIFICA AVVIO SISTEMA
try:
    mqtt.single("notify/notifica_nicola", "riconoscimento facciale avviato", hostname=ip_mqtt)
except:
    print ("errore mqtt")

try:
    # notifica indirizzo IP  tramite HA
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.connect(("apple.com",80))
    personalip = sk.getsockname()[0]
except:
    print ("indirizzo ip non individuato")

try:
    mqtt.single("notify/notifica_nicola", ("indirizzo ip riconoscimento facciale " + str(personalip)), hostname=ip_mqtt)
except:
    print ("errore mqtt")



camera = picamera.PiCamera()
camera.resolution = (risoluzione_x, risoluzione_y)
camera.rotation = (rotazione)
camera.framerate = 32
output = np.empty((240, 320, 3), dtype=np.uint8)


nomi = []
riferimenti = []
mqtt_persona = []


for leggi in (configurazione['persone_conosciute']):
    nome_persona = (list(leggi)[0])
    file_persona = (leggi[nome_persona]['file'])
    mqtt_nome = (leggi[nome_persona]['topic_sensore'])
    nomi = nomi + [nome_persona]
    riferimenti = riferimenti + [file_persona]
    mqtt_persona = mqtt_persona + [mqtt_nome]


immagini_campione = []
a = 0

for immagini in riferimenti:
    immagine_campione = face_recognition.load_image_file(immagini)
    immagini_campione = immagini_campione + [face_recognition.face_encodings(immagine_campione)[0]]
    print("ho codificato " + nomi[a] + " file di riferimento " + riferimenti[a])
    print(" topic sensore " + mqtt_persona[a])
    a = a + 1
print("ho completato la codifica delle immagini campione ")

try:
    mqtt.single("notify/notifica_nicola", "ho completato la codifica delle immagini campione", hostname=ip_mqtt)
except:
    print("errore mqtt")



while True:
    print("catturo l'immagine dalla PIcamera")
    camera.capture(output, format="rgb")

    # individuo i faccie presenti nell'immagine
    visi_individuati = face_recognition.face_locations(output)
    print("Ho trovato {} visi nell'immagine".format(len(visi_individuati)))
    face_encodings = face_recognition.face_encodings(output, visi_individuati)

    # ciclo for per analizzare le faccie trovate
    for face_encoding in face_encodings:
        a = 0
        riconoscimento = 0
        for faccie in immagini_campione:
            confronto = face_recognition.compare_faces([faccie], face_encoding)
            if confronto[0] == True and riconoscimento==0:
                print(" ")
                saluto = ("vedo "+nomi[a] + " con file " + riferimenti[a] + " topic " + mqtt_persona[a])
                print(saluto)
                print(" ")
                try:
                    mqtt.single(mqtt_persona[a], "presente", hostname=ip_mqtt)
                except:
                    print("errore mqtt")
                riconoscimento = 1
                camera.capture('immagine.jpg')

            a = a + 1
        if riconoscimento == 0:
            print("viso non riconosciuto ")
