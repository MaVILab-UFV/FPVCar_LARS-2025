from fpvcar import fpvcar
import time
import cv2
import os
import numpy as np

PATH = 'tests/calibration'
PATH_TO_IMGS = PATH + '/imgs'
PATH_TO_DATA = PATH + '/data'
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.03
MARKER_LENGTH = 0.015
LENGTH_PX = 640   # total length of the page in pixels
MARGIN_PX = 20    # size of the margin in pixels
SAVE_NAME = 'ChArUco_Marker.png'

def create_and_save_new_board():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    size_ratio = SQUARES_HORIZONTALLY / SQUARES_VERTICALLY
    img = cv2.aruco.CharucoBoard.generateImage(board, (LENGTH_PX, int(LENGTH_PX*size_ratio)), marginSize=MARGIN_PX)
    cv2.imshow("ChArUco_Marker", img)
    cv2.waitKey(2000)
    cv2.imwrite(PATH + '/' + SAVE_NAME, img)

def capture(frame, info: fpvcar.Info):
    code = round(time.time())
    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key == ord('c'):
        cv2.imwrite(f'{PATH_TO_IMGS}/image{code}.png', frame)
    if key == ord('q'):
        return False, None
    return True, fpvcar.Stop    

def calibrate_and_save_parameters():
    # Define the aruco dictionary and charuco board
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.CharucoParameters()

    # Load PNG images from folder
    image_files = [os.path.join(PATH_TO_IMGS, f) for f in os.listdir(PATH_TO_IMGS) if f.endswith(".png")]
    image_files.sort()  # Ensure files are in order

    all_charuco_corners = []
    all_charuco_ids = []

    detector = cv2.aruco.CharucoDetector(board,  params)
     
    for image_file in image_files:
        image = cv2.imread(image_file)
        image_copy = image.copy()
        
        charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(image)
        cv2.aruco.drawDetectedMarkers(image_copy, marker_corners, marker_ids)
        all_charuco_corners.append(charuco_corners)
        all_charuco_ids.append(charuco_ids)
        
        # cv2.imshow('image', image)
        # cv2.imshow('image_copy', image_copy)
        # cv2.waitKey()

    # # Calibrate camera
    retval, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, board, image.shape[:2], None, None)

    # # Save calibration data
    np.save(f'{PATH_TO_DATA}/camera_matrix.npy', camera_matrix)
    np.save(f'{PATH_TO_DATA}/dist_coeffs.npy', dist_coeffs)
    
    cv2.destroyAllWindows()

def show_camera_data():
    camera_matrix = np.load(f'{PATH_TO_DATA}/camera_matrix.npy')
    dist_coeffs = np.load(f'{PATH_TO_DATA}/dist_coeffs.npy')
    print(camera_matrix)
    print(dist_coeffs)
    # Load PNG images from folder
    image_files = [os.path.join(PATH_TO_IMGS, f) for f in os.listdir(PATH_TO_IMGS) if f.endswith(".png")]
    image_files.sort()  # Ensure files are in order
    for image_file in image_files:
        image = cv2.imread(image_file)
        undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)
        cv2.imshow('Undistorted Image', undistorted_image)
        cv2.imshow('Image', image)
        cv2.waitKey(0)

if __name__ == '__main__':
    b = input('create board? (y/n): ')
    if b == 'y':
        create_and_save_new_board()
    
    cap = input('capture? (y/n): ')
    if cap == 'y':
        car = fpvcar.FPVCar(ip='192.168.4.1', interval=0.1)
        car.start()
        car.run(parse=capture)
    
    cal = input('calibrate? (y/n): ')
    if cal == 'y':
        calibrate_and_save_parameters()
        
    data = input('show camera data? (y/n): ')
    if data == 'y':
        show_camera_data()
        