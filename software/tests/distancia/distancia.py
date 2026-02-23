"""
    Aqui serão feitos testes de distância vs latência assim como distância vs FPS
"""

from fpvcar import fpvcar
import time
import cv2
import csv

PATH = 'tests/distancia/data'

file = open(f'{PATH}/tests.csv', 'w', newline='')
writer = csv.writer(file, delimiter=',')
writer.writerow(['timestamp', 'distancia', 'latencia', 'fps', 'sample'])

SAMPLES = 150
count = 0
dist = 1
recording = False

def test(frame, info: fpvcar.Info):
    global writer, count, car, recording, dist
    frame = cv2.putText(frame, f"FPS: {info.average_fps}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
    cv2.imshow('Image', frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        car.stop()
        return None
    if key == ord('p'):
        recording = True
    if count >= SAMPLES:
        recording = False
        count = 0
        dist += 1
        
    print('recording=', recording, 'distance=', dist, 'count=', count)
    if recording:
        t = time.time()
        count += 1
        writer.writerow([f'{t:.4f}', dist, info.latency, info.average_fps, count])
    return fpvcar.Stop

def main():
    global car
    car = fpvcar.FPVCar()
    car.start()
    car.run(parse=test)

if __name__ == '__main__':
    main()