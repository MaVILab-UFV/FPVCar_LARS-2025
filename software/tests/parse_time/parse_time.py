"""
    Aqui serão feitos testes de tempo do parse vs Latência e FPS
"""

from fpvcar import fpvcar
import time
import cv2
import csv

PATH = 'tests/parse_time/data'

file = open(f'{PATH}/test.csv', 'w', newline='')
writer = csv.writer(file, delimiter=',')
writer.writerow(['timestamp', 'sample', 'parse time', 'latencia', 'fps'])

SAMPLES = 150
MAX_SLEEP = 300
STEP = 50

sleep_time = 0
count = 0

def test(frame, info: fpvcar.Info):
    global writer, car, sleep_time, count
    frame = cv2.putText(frame, f"FPS: {info.average_fps}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
    cv2.imshow('Image', frame)
    key = cv2.waitKey(1)
    
    if key == ord('q'):
        car.stop()
        return None

    if count == SAMPLES:
        count = 0
        sleep_time += STEP
    count += 1
        
    if sleep_time > MAX_SLEEP:
        car.stop()
        return None
    
    t = time.time()
    writer.writerow([f'{t:.4f}', count, sleep_time, info.latency, info.average_fps])
    print('saved: ', f'{t:.4f}', count, sleep_time, info.latency, info.average_fps)
        
    time.sleep(sleep_time / 1000)
    return fpvcar.Stop

if __name__ == '__main__':
    global car
    car = fpvcar.FPVCar()
    car.start()
    car.run(parse=test)