import requests
import json
import logging

logging.basicConfig(filename='std.out')

class TrackSimConnector:
    def __init__(self) -> None:
        self.version = 'v0.1'
        self.session = requests.Session()
        self.base_url = ''
        
    def connect(self,url:str):
        self.base_url = url
        self.SimluaterCtl_url = url + '/api/SimulaterCtl'
        self.DataUpdate_url = url + '/api/DataUpdate'
        self.ExportTrack_url = url + '/api/ExportTrack'
        
        content = self.session.get(url+'/VersionCheck').content
        version = json.loads(content)['version']
        if version == self.version:
            print('Connect success!!!')
        else:
            print('Connect Failed!!!')
            print('Client version is ',self.version)
        print('Server version is',version)
        
    def init(self,track_name:str):
        data = {'cmd':'init','track_name':track_name}
        content = self.session.post(self.SimluaterCtl_url,json=data).content
        print(content)
    
        

connector = TrackSimConnector()
connector.connect('http://127.0.0.1:5000')
connector.init('anyang_demo')