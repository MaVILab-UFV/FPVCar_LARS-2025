class Info:
    current_speed: int = 0
    current_turn: int = 0
    last_time_call: float = 0
    frame_count: int = 0
    battery_level: float = 0
    average_fps: float = 0
    latency: float = 0
    
    def copy(self):
        new = Info()
        new.current_speed = self.current_speed
        new.current_turn = self.current_turn
        new.last_time_call = self.last_time_call
        new.battery_level = self.battery_level
        new.average_fps = self.average_fps
        new.frame_count = self.frame_count
        new.latency = self.latency
        return new
        