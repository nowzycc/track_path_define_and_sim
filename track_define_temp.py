from track_define_interface import track_plan_base,single_track,x,y

def chassis_speed(x,y,pitch,yaw,t):
    # x和y是传入的是当前机器人在轨道坐标系下坐标
    # pitch和yaw是云台的当前角度
    # t为此时时刻
    
    # 这里应该写上速度定义公式
    # 定义开始
    
    # 定义结束
    
    # 应该返回机器人相对轨道的速度
    return 0

def gimbal_angle(x,y,pitch,yaw,t):
    # x和y是传入的是当前机器人在轨道坐标系下坐标
    # pitch和yaw是云台的当前角度
    # t为此时时刻
    
    # 这里应该写上云台的角度定义公式
    # 定义开始
    
    # 定义结束
    
    # 应该返回机器人云台的角度
    return 0,0

plan_name = 'demo_plan'
plan = track_plan_base(plan_name) # 在这里设定巡检策略的名字
plan.chassis_speed_define(chassis_speed)
plan.gimbal_angle_define(gimbal_angle)
plan.initial_pos_set((0, 0), (0, 0)) # 第一个参数是初始化坐标、第二个参数是初始化云台角度

track_name = 'demo_track'
track = single_track(track_name) # 在这里设定轨道的名字
track.track_plan_append(plan)
track.track_formula_append(x-y) # 轨道方程添加，支持添加多个方程，约束为f(x,y)=0
track.track_offset_define((0, 0), (0)) # 第一个参数是轨道相对世界坐标偏移量、第二个参数是轨道相对世界角度偏移量

track.save('./'+track_name)
