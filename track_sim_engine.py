from flask import Flask, request
from flask_restful import RESTful, Resource
from track_simulater import track_path_simulater
from track_define_interface import single_track

app = Flask(__name__)
api = RESTful(app)
track_path = '/home/alstondu/cc_code/track_define/tracks'
simulater = None
tracks_obj_path = {
    'anyang_demo':track_path+'/anyang/demo_track.obj'
}
delta_time = 0

class SimulaterCtl(Resource):
    def post(self):
        cmd = request.json.get('cmd')
        match cmd:
            case 'init':
                track_name = request.json.get('track_name')
                track = None
                try:
                    track = single_track(track_name)
                    track.load(tracks_obj_path[track_name])
                except BaseException as e:
                    return {'result': 'error','cause':e}
                global simulater
                simulater = track_path_simulater(track)
                return {'result': 'success'}
            
            case 'setup':
                global simulater
                if simulater == None:
                    return {'result': 'error','cause':'simulater has not been inited'}
                simulater.setup()
                return {'result': 'success'}
            
            case 'close':
                pass
            case 'change_plan':
                pass
            case 'set_delta_time':
                global simulater
                if simulater == None:
                    return {'result': 'error','cause':'simulater has not been inited'}
                global delta_time
                delta_time = request.json.get('delta')
                

class DataUpdate(Resource):
    def get(self):
        # 内部实现坐标迭代解算
        global simulater
        if simulater == None:
            return {'result': 'error','cause':'simulater has not been inited'}
        
        simulater.time_delta(delta_time) # 时间增量
        simulater.call_plan()            # 调用函数接口
        simulater.update_pose()          # 更新姿态
        position = simulater.get_world_pos()
        angle = simulater.get_world_angle()
        return {'result':'success','position':position,'angle':angle}
    
    def post(self):
        # 采取反馈的方式更新数据（将坐标迭代解算放到外部实现）
        global simulater
        if simulater == None:
            return {'result': 'error','cause':'simulater has not been inited'}
        try:
            position = request.json.get('position')
            angle = request.json.get('angle')
            delta = request.json.get('delta_time')
        except:
            return {'result': 'error','cause':'para error'}
        x,y = position
        pitch,yaw = angle
        simulater.set_world_pose(x,y,pitch,yaw)   # 设置姿态
        simulater.time_delta(delta)               # 时间增量
        simulater.call_plan()                     # 调用函数接口
        speed = simulater.get_robot_speed()
        angle = simulater.get_world_angle()
        return {'result':'success','speed':speed,'angle':angle}

class ExportTrack(Resource):
    def get(self):
        return {'err':'err'}

api.add_resource(SimulaterCtl, '/api/SimulaterCtl')
api.add_resource(DataUpdate, '/api/DataUpdate')
api.add_resource(ExportTrack, '/api/ExportTrack')

if __name__ == '__main__':
    app.run(debug=True)