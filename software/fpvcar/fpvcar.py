from .command import *
from .info import Info
import cv2
import threading
import time
from websockets.sync.client import connect
import websockets
import json
from collections import deque

WS_PORT     = 81
RTSP_PORT   = 8554

class FPVCar:
    def __init__(self, ip: str = '192.168.4.1', interval: float = 0.1) -> None:
        self.__is_running = False
        # image/capture related values
        self.__cap_thread = threading.Thread(target=self.__capture_thread_run)
        self.__frame_mutex = threading.Lock()
        self.__new_frame = False
        self.__current_frame = None
        self.__cap_is_connected = False
        # fps calculation
        self.__queue_frame_times = deque()
        # system run
        self.__ws_thread = threading.Thread(target=self.__ws_thread_run)
        self.__ws_connection = None
        self.__ws_is_connected = False
        self.__last_time_measure = 0
        # info properties
        self.__info = Info()
        # latency ping/pong thread
        self.__latency_thread = threading.Thread(target=self.__latency_thread_run)
        # debug
        self.verbose = True
        # car info
        self.ip = ip
        self.interval = interval
    
    def start(self):
        self.__is_running = True
        self.__cap_thread.start()
        self.__ws_thread.start()
        self.__latency_thread.start()
    
    def stop(self):
        if self.verbose:
            print('exiting...')
        self.__is_running = False

    def run(self, parse: callable):
        while self.__is_running:
            if not self.__ws_is_connected or not self.__cap_is_connected:
                continue
            
            # get current frame
            self.__frame_mutex.acquire()
            has_new_frame = self.__new_frame
            self.__new_frame = False
            if has_new_frame:
                frame = self.__current_frame.copy()
            self.__frame_mutex.release()
            
            if not has_new_frame:
                continue
            
            # atualiza info
            self.__info.frame_count += 1

            # update fps measure
            self.__queue_frame_times.append(time.time())
            self.__update_fps()

            # call user parse callback
            command = parse(frame, self.__info.copy())
            
            # atualiza info
            self.__info.last_time_call = time.time()
            
            if not self.__is_running:
                break
            
            # send command from user to car
            if command is not None:
                self.__send_command(command)
            
            # sleep the remaining time to match self.interval
            current_time = time.time()
            time.sleep(max(0, self.interval - (current_time - self.__last_time_measure)))
            self.__last_time_measure = current_time
    
    def __update_fps(self):
        # update FPS with average value from the last 5 seconds
        SECONDS = 5
        now = time.time()
        while len(self.__queue_frame_times) > 0 and self.__queue_frame_times[0] < now - SECONDS:
            self.__queue_frame_times.popleft()
        self.__info.average_fps = len(self.__queue_frame_times) / SECONDS
        
    def __latency_thread_run(self):
        while self.__is_running:
            if not self.__ws_is_connected:
                continue
            data = {
                'ping': f'{time.time():.4f}'
            }
            self.__send_message(json.dumps(data))
            if self.verbose:
                print('send ping')
            time.sleep(3)
    
    def __capture_thread_run(self):
        cap : cv2.VideoCapture = None
        # run while system is active
        while self.__is_running:
            # need connection
            if cap is None or not self.__cap_is_connected:
                if self.verbose:
                    print('Conectando ao stream de vídeo...')
                # start reading from stream
                cap = cv2.VideoCapture(f'rtsp://{self.ip}:{RTSP_PORT}/mjpeg/1')
                self.__cap_is_connected = True
                if self.verbose:
                    print('Stream de vídeo conectado!!!')
                continue
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.__frame_mutex.acquire()
                    self.__current_frame = frame
                    self.__new_frame = True
                    self.__frame_mutex.release()
                else:
                    cap = None
                    self.__cap_is_connected = False
            
        # stop system and release cap
        self.__cap_is_connected = False
        cap.release()
    
    def __send_command(self, command: Command):
        self.__send_message(json.dumps(command.values))
    
    def __send_message(self, message: str):
        try:
            self.__ws_connection.send(message)
        except:
            if self.verbose:
                print('OPS: OPS! Websocket Desconectado')
    
    def __parse_message(self, data):
        try:
            obj : dict = json.loads(data)
            
            if 'debug' in obj:
                msg = obj['debug']
                print(f'[ESP32-CAM]: {msg}')
                
            if 'pong' in obj:
                t = float(obj['pong'])
                self.__info.latency = time.time() - t
                
                if self.verbose:
                    print('got pong', self.__info.latency)
            
        except json.decoder.JSONDecodeError:
            print('failed to parse json')
        
    def __ws_thread_run(self):    
        # run while system is active
        while self.__is_running:
            # connecto to WS if not connected
            if not self.__ws_is_connected:
                if self.verbose:
                    print('Conectando ao websocket...')
                try:
                    self.__ws_connection = connect(f'ws://{self.ip}:{WS_PORT}')
                    self.__ws_is_connected = True
                except:
                    if self.verbose:
                        print('Falha ao conectar ao websocket, tentando novamente em 3s')
                    time.sleep(3)
                if self.verbose:
                    print('Websocket conectado!!!')
            
            try:
                message = self.__ws_connection.recv(timeout=0.5)
                self.__parse_message(message)
            except websockets.exceptions.ConnectionClosed:
                self.__ws_is_connected = False
                if self.verbose:
                    print("OPS! Websocket Desconectado")
            except TimeoutError:
                pass
        
        # if stopped, disconnect from WS
        if self.__ws_is_connected:
            self.__ws_is_connected = False
            self.__ws_connection.close()
        