import json
import csv
from pathlib import Path
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import re
from natsort import ns,natsorted




# filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Guardian_filelist.txt"
# filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Mystic_filelist.txt"
# filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Seeker_filelist.txt"
# filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Rogue_filelist.txt"
# filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Survivor_filelist.txt"
filename_path = r"D:\Projects\Arkham-Horror-LCG-Cards\Neutral_filelist.txt"
with open(filename_path,'r',encoding='utf-8') as f:
    filename_list = f.read().splitlines()

print(len(filename_list),filename_list)



# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Guardian全牌组.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Mystic全牌组.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Seeker全牌组.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Rogue全牌组.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Survivor全牌组.json"
json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Neutral全牌组.json"

with open(json_path,'r',encoding='utf-8') as f:
    content = f.read()
    save_object = json.loads(content)
    object_states = save_object['ObjectStates']    
    for object_state in object_states:        
        # for object in object_state['ContainedObjects']:
            # object['Nickname']='unknown'
        for i,object in enumerate(object_state['ContainedObjects']):
            object['Nickname']=filename_list[i]

    save_object2 = json.dumps(save_object)



# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Guardian全牌组2.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Mystic全牌组2.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Seeker全牌组2.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Rogue全牌组2.json"
# json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Survivor全牌组2.json"
json_path = r"C:\Users\fky\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\诡镇奇谈卡牌\自制全牌组\Neutral全牌组2.json"
with open(json_path,'w',encoding='utf-8') as f:
    f.write(save_object2)
    f.close




# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Mystic" >> Mystic_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Mystic" >> Mystic_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Mystic\69_1" >> Mystic_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Mystic" >> Mystic_filelist.txt


# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Seeker" >> Seeker_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Seeker\69_1" >> Seeker_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Seeker" >> Seeker_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Seeker\69_1" >> Seeker_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Seeker\69_2" >> Seeker_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Seeker" >> Seeker_filelist.txt

# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Rogue" >> Rogue_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Rogue\69_1" >> Rogue_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Rogue" >> Rogue_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Rogue\69_1" >> Rogue_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Rogue" >> Rogue_filelist.txt

# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Survivor" >> Survivor_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Survivor\69_1" >> Survivor_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Survivor" >> Survivor_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Survivor\69_1" >> Survivor_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Survivor" >> Survivor_filelist.txt

# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Skill\Neutral" >> Neutral_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Event\Neutral" >> Neutral_filelist.txt
# ls "E:\Projects\Arkham-Horror-LCG-Cards\Project\New Task Name\export_20250510\Asset\Neutral" >> Neutral_filelist.txt