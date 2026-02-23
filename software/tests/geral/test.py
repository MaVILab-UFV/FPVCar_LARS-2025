from fpvcar import fpvcar
import time
import cv2
import numpy as np

def parse(frame, info: fpvcar.Info):
    frame = cv2.putText(frame, f"FPS: {info.average_fps}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
        
    if key == ord('q'):
        cv2.destroyAllWindows()
        return  None
        
    if key == ord('w'):
        return fpvcar.MoveForwardStraight
        
    if key == ord('s'):
        return fpvcar.MoveBackwardStraight
        
    if key == ord('d'):
        return fpvcar.MoveForwardRight
        
    if key == ord('a'):
        return fpvcar.MoveForwardLeft
    
    if key == ord('f'):
        return fpvcar.TurnLeft
        
    return fpvcar.Stop

# delay = 0

# def parseCicles(frame, info: fpvcar.Info):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     gray = cv2.medianBlur(gray, 5)

#     rows = gray.shape[0]
#     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=10, maxRadius=100)

#     if circles is not None:
#         circles = np.uint16(np.around(circles))
#         for i in circles[0, :]:
#             center = (i[0], i[1])
#             cv2.circle(frame, center, 1, (0,100,100), 3)
#             radius = i[2]
#             cv2.circle(frame, center, radius, (255, 0, 255), 3)


#     cv2.imshow('frame', frame)
#     key = cv2.waitKey(1) & 0xFF
    
#     if key == ord('q'):
#         return False, None

#     return True, fpvcar.Stop

# def parseTime(frame, info: fpvcar.Info):
#     global delay
#     print(f'delay: {delay} \tFPS: {info.average_fps}')
#     cv2.imshow('frame', frame)
#     key = cv2.waitKey(1) & 0xFF
    
#     if key == ord('q'):
#         return False, None
    
#     if key == ord('e'):
#         delay += 25
        
#     if key == ord('w'):
#         delay -= 25
    
#     time.sleep(delay/1000)

#     return True, fpvcar.Stop

# def capture(frame, info: fpvcar.Info):
#     code = round(time.time())
#     cv2.imshow('frame', frame)
#     key = cv2.waitKey(1)
#     if key == ord('c'):
#         cv2.imwrite(f'tests/imgs/image{code}.jpg', frame)
#     if key == ord('q'):
#         return False, None
#     return True, fpvcar.Stop

# def drive(frame, info: fpvcar.Info) -> fpvcar.Command:
#     pass


def main():
    car = fpvcar.FPVCar(ip='192.168.4.1')
    car.start()

    def control(frame, info: fpvcar.Info):
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            car.stop()
            return None
        return fpvcar.MoveForward
    
    car.run(parse=parse)

main()
