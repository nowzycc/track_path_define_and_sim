from track_define_interface import *

class track_path_simulater:
    def __init__(self,track:single_track) -> None:
        self.track = track
        self.current_plan = None
        self.time_now = 0
        self.delta = 0
        
        # 机器人世界坐标
        self.robot_world_pos = np.zeros(2)   # [x,y]
        self.robot_world_angle = np.zeros(2) # [pitch,yaw]
        self.robot_world_speed = np.zeros(2) # [x,y]
        # 世界坐标和轨道坐标offset
        self.track2world_pos_offset = np.array(track.pos_offset) # [x,y]
        self.track2world_angle_offset = track.angle_offset[0]    # [yaw]
        # 机器人轨道坐标
        self.robot_track_pos = np.zeros(2)   # [x,y]
        self.robot_track_angle = np.zeros(2) # [pitch,yaw]
        self.robot_track_speed = np.zeros(2) # [x,y]
        # 机器人速度(相对于轨道)
        self.robot_speed = 0
    
    def time_delta(self,delta):
        self.delta = delta
        self.time_now += delta
    
    def use_plan(self,plan_name:str):
        self.current_plan = self.track.track_plan_dict[plan_name]
    
    def __update_world_value(self):
        self.robot_world_pos = self.robot_track_pos - self.track2world_pos_offset
        self.robot_world_angle = self.robot_track_angle - (0,self.track2world_angle_offset)
        self.robot_world_speed[0] = self.robot_track_speed[1]*np.sin(self.track2world_angle_offset)+self.robot_track_speed[0]*np.cos(self.track2world_angle_offset)
        self.robot_world_speed[1] = self.robot_track_speed[1]*np.cos(self.track2world_angle_offset)+self.robot_track_speed[0]*np.sin(self.track2world_angle_offset)
    
    @staticmethod
    def __get_track_speed(dx,dy,speed):
        dy_x = dy / dx
        dx_y = dx / dy
        v_x = speed / np.sqrt(1+dy_x**2)
        v_y = speed / np.sqrt(1+dx_y**2)
        return v_x,v_y
    
    @staticmethod
    def __get_positive_direction(dx,dy,angle):
        slope = np.array((dx,dy))
        gimbal = np.array((np.cos(angle[1]),np.sin(angle[1])))
        if np.dot(slope,gimbal) < 0:
            return -dx,-dy
    
    def setup(self):
        self.robot_track_pos = np.array(self.current_plan.initial_pos)
        self.robot_track_angle = np.array(self.current_plan.initial_angle)
        self.robot_speed = 0
        self.__update_world_value()
        
    def update(self):
        x = self.robot_track_pos[0]
        y = self.robot_track_pos[1]
        pitch = self.robot_track_angle[0]
        yaw = self.robot_track_angle[1]
        self.robot_speed = self.current_plan.func_chassis_speed_define(x,y,pitch,yaw,self.time_now)
        self.robot_track_angle = self.current_plan.func_gimbal_angle_define(x,y,pitch,yaw,self.time_now)
        dx,dy = self.track.get_slope_for_point(x,y)
        dx,dy = self.__get_positive_direction(dx,dy,self.robot_track_angle)
        self.robot_track_speed = self.__get_track_speed(dx,dy,self.robot_speed)
        self.robot_track_pos[0] += self.robot_track_speed[0] * self.delta
        self.robot_track_pos[1] += self.robot_track_speed[1] * self.delta
        self.__update_world_value()

    def get_track_pos(self):
        return self.robot_track_pos
    
    def get_track_angle(self):
        return self.robot_track_angle
