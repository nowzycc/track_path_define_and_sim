import os
import inspect
from sympy.abc import x, y, z
from sympy import solve
import pickle
import numpy as np
import cv2

class track_plan:
    def __init__(self,name) -> None:
        self.name = name
        self.func_chassis_speed_define = None
        self.func_gimbal_angle_define = None
        self.initial_pos = None
        self.initial_angle = None
    
    def chassis_speed_define(self,func):
        if not callable(func):
            raise 'func can not be called'
        self.func_chassis_speed_define = func
    
    def gimbal_angle_define(self,func):
        if not callable(func):
            raise 'func can not be called'
        self.func_gimbal_angle_define = func
        
    def initial_pos_set(self,pos:tuple,angle:tuple):
        self.initial_pos = pos
        self.initial_angle = angle

class single_track:
    def __init__(self,name:str,
                 track_description_method='grayscalepic',
                 track_width=0.25,
                 threshold=0.1
                 ) -> None:
        self.name = name
        self.track_plan_dict = {}
        # 使用公式描述
        self.formula_list = []
        # 使用灰度图描述
        # 白色为轨道、黑色为空白
        self.img = None
        self.pix_length = None
        self.binary_pic = None
        self.edge_pic = None
        self.nearby_length = None
        # 轨道相对世界坐标系偏移
        self.pos_offset = None
        self.angle_offset = None
        # 轨道相关参数
        self.track_description_method = track_description_method
        self.track_width = track_width
        self.threshold = threshold
    
    def assert_is_formula(self):
        if self.track_description_method != 'formula':
            raise 'track desciption method is not formula'
        
    def assert_is_grayscalepic(self):
        if self.track_description_method != 'grayscalepic':
            raise 'track desciption method is not grayscale pictrue'
    
    def track_plan_append(self,plan:track_plan):
        self.track_plan_dict[plan.name] = plan
    
    def set_grayscale_pic(self,path,gray_thresh=50,pix_length=0.05,nearby_length=0.2):
        self.assert_is_grayscalepic()
        self.pix_length = pix_length
        self.nearby_length = nearby_length
        self.img = cv2.imread(path)
        blurred = cv2.GaussianBlur(self.img, (3, 3), 0)  # 高斯模糊降噪
        edges = cv2.Canny(blurred, 100, 200)
        self.edge_pic = edges
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY) # 转灰值图
        gray = 255 - gray
        ret, dst = cv2.threshold(gray, gray_thresh, 255, cv2.THRESH_BINARY) # 转二值图
        kernel = np.ones((10, 10), np.uint8)
        dst = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, kernel)
        dst = cv2.dilate(dst, kernel, 1)
        self.binary_pic = dst
     
    def track_formula_append(self,formula):
        self.assert_is_formula()
        formula_dict = {
            'formula':formula,      # 方程式
            'intersection_list':[]  # 交点列表
        }
        self.__formula_intersection_cal(formula) # 计算与其他方程交点
        self.formula_list.append(formula_dict)
    
    def __formula_intersection_cal(self,formula_dict):
        # 根据约束来看，在单根轨道上，一个方程最多与其他方程存在两个交点,
        # 所以超过两个交点的算违规方程，应该报错
        for f in self.formula_list:
            solve_res = solve([f['formula'],formula_dict['formula']],[x,y],dict=True)
            if len(solve_res) > 2:
                raise 'too many intersection point for ' + str(formula_dict['formula'])
            for res in solve_res:
                if len(f['intersection_list'] >= 2):
                    raise 'too many intersection point for ' + str(f['formula'])
                f['intersection_list'].append((formula_dict,res[x],res[y]))
                formula_dict['intersection_list'].append((f,res[x],res[y]))

    def track_offset_define(self,poi_offset:tuple,angle_offset:tuple):
        self.pos_offset = poi_offset
        self.angle_offset = angle_offset
        
    def get_subtrack_for_point(self,x,y):
        self.assert_is_formula()
        # 该函数只适用于当轨道描述为解析式时
        # if self
        pass
        
    def __get_slope_on_pic_hough(self,x,y):
        pix_x = int(x / self.pix_length)
        pix_y = int(y / self.pix_length)
        pos_color = self.binary_pic[pix_x][pix_y]
        if pos_color < 200:
            raise 'pos is not on the track'
        nearby_pix = int(self.nearby_length / self.pix_length)
        nearby_area = self.binary_pic[pix_x-nearby_pix:pix_x+nearby_pix][pix_y-nearby_pix:pix_y+nearby_pix]
        lines = cv2.HoughLines(nearby_area,1, np.pi / 180, 200) #TODO:需要调整霍夫直线的参数,阈值可能需要调小一点以满足曲线时的需求
        line = lines[0]
        rho, theta = line[0]
        dx = np.cos(theta)
        dy = np.sin(theta)
        dx = dx / np.sqrt(dx**2+dy**2)
        dy = dy / np.sqrt(dx**2+dy**2)
        return (dx,dy)
    
    def __get_slope_on_pic_mean(self,x,y):
        point = []
        pix_x = int(x / self.pix_length)
        pix_y = int(y / self.pix_length)
        pos_color = self.binary_pic[pix_x][pix_y]
        if pos_color < 200:
            raise 'pos is not on the track'
        nearby_pix = int(self.nearby_length / self.pix_length)
        weights = list(range(1,2*nearby_pix+1))
        nearby_area = self.binary_pic[pix_x-nearby_pix:pix_x+nearby_pix][pix_y-nearby_pix:pix_y+nearby_pix]
        for i,v in np.ndenumerate(nearby_area):
            if v == 255:
                point.append(i)
        x1,y1 = point[0]
        x2,y2 = point[-1]
        
        dx = x2 - x1
        dy = y2 - y1
        return (dx,dy)
    
    def get_slope_for_point(self,x,y):
        if self.track_description_method == 'grayscalepic':
            return self.__get_slope_on_pic_mean(x,y)
        if self.track_description_method == 'formula':
            #TODO: 考虑将方程绘制在灰度图上然后进行计算（不进行单独计算的原因主要考虑到轨道衔接处）
            pass
        
    def save(self,path:os.PathLike):
        temp = (self.name,
                self.angle_offset,
                self.pos_offset,
                self.track_plan_dict,
                self.formula_list
                )
        temp_str = pickle.dumps(temp)
        with open(path,'wb') as f:
            f.write(temp_str)
        
    def load(self,path:os.PathLike):
        temp_str = None
        with open(path,'rb') as f:
            temp_str = f.read()
        temp = pickle.loads(temp_str)
        self.name = temp[0]
        self.angle_offset = temp[1]
        self.pos_offset = temp[2]
        self.track_plan_dict = temp[3]
        self.formula_list = temp[4]


