import json
import csv
from pathlib import Path
import os
import requests
from concurrent.futures import ThreadPoolExecutor

def safe_get(data, key, default=None):
    """安全获取嵌套字典值的通用方法"""
    return data.get(key, default)

def replace_text_tag(text) -> str:    
    replacements = {
        "[fullname]" : "<fullname>",
        "[guardian]" : "<gua>",
        "[seeker]" : "<see>",
        "[rogue]" : "<rog>",
        "[mystic]" : "<mys>",
        "[survivor]" : "<sur>",
        "[willpower]" : "<wil>",
        "[intellect]" : "<int>",
        "[combat]" : "<com>",
        "[agility]" : "<agi>",
        "[wild]" : "<wild>",
        "[skull]" : "<sku>",
        "[cultist]" : "<cul>",
        "[tablet]" : "<tab>",
        "[elder_thing]" : "<mon>",
        "[bless]" : "<ble>",
        "[curse]" : "<cur>",
        "[elder_sign]" : "<eld>",
        "[auto_fail]" : "<ten>",
        "[action]" : "<act>",
        "[free]" : "<fre>",
        "[fast]" : "<fre>",
        "[reaction]" : "<rea>",
        "[force]" : "<for>",
        "[]" : "<hau>",
        "[object]" : "<obj>",
        "[]" : "<rev>",
        "[]" : "<uni>",
        "[]" : "<per>",
        "[]" : "<bul>",
        "[]" : "<squ>",
        "[[" : "<b><i>",
        "]]" : "</i></b>",
        "- …" : "<bul> ...",
        "\n-" : "\n<bul>",
    }

    for old, new in replacements.items():
        text = text.replace(old,new)
    return text

def fix_X_cost(cost):    
    if '-' in cost:
        cost = 'X'    
    elif cost == 'None':
        return '-'
    return cost

def process_card(card):
    """统一处理卡片数据的函数"""
    # 基本信息（所有卡片共有）
    text = safe_get(card, 'text', '')   
    text = replace_text_tag(text)
    result = {
        'name': safe_get(card, 'name', '未知名称'),
        'code': safe_get(card, 'code', '未知编号'),
        'type': safe_get(card, 'type_code', '未知类型'),
        'subtype': safe_get(card, 'subtype_code', ''),
        'xp': safe_get(card, 'xp', 0), # 默认 XP 为 0
        'faction_code': safe_get(card, 'faction_code', '未知类型'),
        'illustrator': safe_get(card, 'illustrator', '未知作家'),
        'traits': safe_get(card, 'traits', '')+'.',
        'text': text,
        'flavor': '\n'+safe_get(card, 'flavor', ''),
        'pack_code': safe_get(card, 'pack_code', ''),
        'position': safe_get(card, 'position', '0'),
    }

    # 动态处理不同卡片类型的特性字段
    card_type = result['type']    
    
    # 根据不同卡片类型提取特征属性
    if card_type == 'asset':
        result.update({
            'cost': safe_get(card, 'cost', 0),
            'slot': safe_get(card, 'slot', '无装备槽'),
            'sanity': safe_get(card, 'sanity', 'N/A'),
            'skill_combat': safe_get(card, 'skill_combat', '0'),
            'skill_agility': safe_get(card, 'skill_agility', '0'),
            'skill_wild': safe_get(card, 'skill_wild', '0'),
            'skill_willpower': safe_get(card, 'skill_willpower', '0'),
            'skill_intellect': safe_get(card, 'skill_intellect', '0'),            
        })
    elif card_type == 'treachery':
        result.update({
            'hidden': safe_get(card, 'hidden', False),
            'subtype': safe_get(card, 'subtype_code', '无子类型')
        })
    elif card_type == 'skill':
        result.update({
            'skill_combat': safe_get(card, 'skill_combat', '0'),
            'skill_agility': safe_get(card, 'skill_agility', '0'),
            'skill_wild': safe_get(card, 'skill_wild', '0'),
            'skill_willpower': safe_get(card, 'skill_willpower', '0'),
            'skill_intellect': safe_get(card, 'skill_intellect', '0'),
            
            
        })
    elif card_type == 'event':
        # cost = fix_X_cost(safe_get(card, 'cost', 0))
        # print(type(cost),cost)
        # print(card)
        cost = str(safe_get(card, 'cost', 0))
        # if '-' in cost:
        #     cost = 'X'

        cost = fix_X_cost(cost)
        result.update({
            'cost': cost,
            'slot': safe_get(card, 'slot', '无装备槽'),
            'sanity': safe_get(card, 'sanity', 'N/A'),
            'skill_combat': safe_get(card, 'skill_combat', '0'),
            'skill_agility': safe_get(card, 'skill_agility', '0'),
            'skill_wild': safe_get(card, 'skill_wild', '0'),
            'skill_willpower': safe_get(card, 'skill_willpower', '0'),
            'skill_intellect': safe_get(card, 'skill_intellect', '0'),            
        })

    # 处理所有卡片可能存在的公共可选字段
    # optional_fields = ['traits', 'text', 'flavor']
    # for field in optional_fields:
    #     result[field] = safe_get(card, field, '')    
    return result

# 读取并处理文件
def load_cards(file_path_list):
    result_list = []
    for file_path in file_path_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for c in raw_data:
                    result_list.append(process_card(c))
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return []
    return result_list


def json_to_csv(json_data, csv_path, encoding='utf-8'):
    """
    将 JSON 数据转换为 CSV 文件
    
    参数:
        json_data: list/dict - 要转换的 JSON 数据
        csv_path: str - 输出的 CSV 文件路径        
    """
    try:
        # 统一数据格式为列表
        if isinstance(json_data, dict):
            data = [json_data]
        elif isinstance(json_data, list):
            data = json_data
        else:
            raise ValueError("无效的 JSON 数据类型")

        # 获取所有字段（保持顺序）
        # all_fields = set()
        # for item in data:
        #     print('item.keys():',item.keys())
        #     all_fields.update(item.keys())
        # fieldnames = sorted(all_fields)  # 按字母排序，可按需自定义顺序      
        
        # 获取所有字段（保持顺序）
        fieldnames = list(dict.fromkeys(key for item in json_data for key in item))


        # 创建输出目录
        output_path = Path(csv_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入 CSV 文件
        with open(output_path, 'w', newline='', encoding=encoding) as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                # fieldnames=['file', 'name', '$SpecialText', 'portSource', 'portX', 'portY', 'portScale', '$Unique', '$CardClass', '$ResourceCost', '$Level', '$Skill1', '$Skill2', '$Skill3', '$Skill4', '$Skill5', '$Skill6', '$Artist', '$Copyright', '$Traits', '$Keywords', '$Rules', '$Flavor', '$Victory', '$Collection', '$CollectionNumber'],
                quoting=csv.QUOTE_MINIMAL,  # 自动处理特殊字符
                extrasaction='ignore'       # 忽略多余字段
            )
            
            writer.writeheader()
            
            for row in data:
                # 处理嵌套结构（可选）
                processed_row = {
                    k: _convert_value(v) 
                    for k, v in row.items()
                }
                writer.writerow(processed_row)

        print(f"转换成功！文件已保存至：{output_path.resolve()}")

    except Exception as e:
        print(f"转换失败：{str(e)}")

def _convert_value(value):
    """处理特殊数据类型"""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value

# 过滤技能牌
def filter_skill_cards(card_list, type_field='type', target_type='skill'):
    """
    过滤指定类型的卡牌
    
    :param card_list: 原始卡牌列表
    :param type_field: 类型字段名（默认为 type_code）
    :param target_type: 目标类型（默认为 skill）
    :return: 过滤后的新列表
    """
    return [
        card.copy() for card in card_list
        if str(card.get(type_field, '')).lower() == target_type.lower()
    ]

# 过滤事件牌
def filter_event_cards(card_list, type_field='type', target_type='event'):
    """
    过滤指定类型的卡牌
    
    
    :param card_list: 原始卡牌列表
    :param type_field: 类型字段名
    :param target_type: 目标类型
    :return: 过滤后的新列表
    """
    return [
        card.copy() for card in card_list
        if str(card.get(type_field, '')).lower() == target_type.lower() 
            and 'weakness' not in str(card.get('subtype', '')).lower()  #排除弱点卡
    ]

# 过滤支援牌
def filter_asset_cards(card_list, type_field='type', target_type='asset'):
    """
    过滤指定类型的卡牌
    
    :param card_list: 原始卡牌列表
    :param type_field: 类型字段名
    :param target_type: 目标类型
    :return: 过滤后的新列表
    """
    return [
        card.copy() for card in card_list
        if str(card.get(type_field, '')).lower() == target_type.lower()
    ]

# 将卡牌原本的json信息(英文) 与翻译的json 信息(中文) 进行深度合并
def specific_key_merge(json_list_a, json_list_b, key_fields=None):
    """
    精确合并两个JSON列表，仅覆盖指定字段
    
    :param json_list_a: 基础数据列表（保留所有字段）
    :param json_list_b: 更新数据列表（提供覆盖字段）
    :param key_fields: 需要覆盖的字段列表，默认为 ['flavor', 'name', 'text', 'traits']
    :return: 合并后的新列表
    """
    if key_fields is None:
        key_fields = ['flavor', 'name', 'text', 'traits']

    # 创建索引字典（code为键）
    merged_index = {item["code"]: item.copy() for item in json_list_a}

    # 处理覆盖逻辑
    for update_item in json_list_b:
        code = update_item.get("code")
        target_item = merged_index.get(code)
        
        if not target_item:
            continue  # 跳过不存在于A列表的对象
        
        # 精确覆盖指定字段
        for field in key_fields:
            if field in update_item:
                target_item[field] = update_item[field]

    return list(merged_index.values())

# 投入技能排序
def sort_skill(card):
    skill_list = []
    agility = int(safe_get(card,'skill_agility',0))
    combat = int(safe_get(card,'skill_combat',0))
    intellect = int(safe_get(card,'skill_intellect',0))
    willpower = int(safe_get(card,'skill_willpower',0))
    wild = int(safe_get(card,'skill_wild',0))
    if agility > 0:
        for i in range(0,agility):
            skill_list.append('Agility')
    if combat > 0:
        for i in range(0,combat):
            skill_list.append('Combat')
    if intellect > 0:
        for i in range(0,intellect):
            skill_list.append('Intellect')
    if willpower > 0:
        for i in range(0,willpower):
            skill_list.append('Willpower')
    if wild > 0:
        for i in range(0,wild):
            skill_list.append('Wild')
    if len(skill_list) < 6:
        for i in range(0,6-len(skill_list)):
            skill_list.append('None')

    return skill_list

# 根据卡牌给出的pack_core 信息 获取collect , 用于map 卡牌右下角的图标
def map_collection(collection):
    collection_map = {
        'core':'CoreSet' ,
        'dunleg':'TheDunwichLegacy',    
        'ccurrou':'CurseOfTheRougarou' ,
        'ccarhor':'CarnevaleOfHorrors' ,
        'carcosa':'ThePathToCarcosa' ,
        'forage':'TheForgottenAge' ,
        'lablun':'TheLabyrinthsOfLunacy' ,
        'rtnotz':'ReturnToTheNightOfTheZealot' ,
        'guaaby':'GuardiansOfTheAbyss' ,
        'rttdl':'ReturnToTheDunwichLegacy' ,
        'cirund':'TheCircleUndone' ,
        'rttptc':'ReturnToThePathToCarcosa' ,
        'dreeat':'TheDreamEaters' ,
        'mateh':'MurderAtTheExcelsiorHotel' ,
        'parallel':'ParallelInvestigators' ,
        'blob':'TheBlobThatAteEverything' ,
        'rttfa':'ReturnToTheForgottenAge' ,
        'natcho':'NathanielCho' ,
        'harwal':'HarveyWalters' ,
        'winhab':'WinifredHabbamock' ,
        'jacfin':'JacquelineFine' ,
        'stecla':'StellaClark' ,
        'tic':'TheInnsmouthConspiracy' ,
        'cwotog':'WarOfTheOuterGods',        
        'bota':'TheDunwichLegacy',
        'dwl':'TheDunwichLegacy',
        'litas':'TheDunwichLegacy',
        'tece':'TheDunwichLegacy',
        'tmm':'TheDunwichLegacy',
        'uau':'TheDunwichLegacy',
        'wda':'TheDunwichLegacy',
        'eoep':'EdgeOfTheEarthInv',
        'eoec':'EdgeOfTheEarthInv',
        'dsm':'TheDreamEaters',
        'hhg':'TheInnsmouthConspiracy',
        'itm':'TheInnsmouthConspiracy',
        'ste':'StellaClark',
        'win':'WinifredHabbamock',
        'tskp':'TheScarletKeysInv',
        'tbb':'TheForgottenAge',
        'ptc':'ThePathToCarcosa',
        'tpm':'ThePathToCarcosa',
        'jac':'JacquelineFine',
        'eotp':'ThePathToCarcosa',
        'sfk':'TheDreamEaters',
        'fhvp':'fhvp',
        'tcu':'TheCircleUndone',
        'woc':'TheDreamEaters',
        'sha':'TheForgottenAge',
        'bsr':'ThePathToCarcosa',
        'tof':'TheForgottenAge',
        'tfa':'TheForgottenAge',
        'lif':'TheInnsmouthConspiracy',
        'wgd':'TheDreamEaters',
        'pnr':'TheDreamEaters',
        'rtdwl':'TheDunwichLegacy',
        'hote':'TheForgottenAge',
        'dca':'ThePathToCarcosa',                
        'tsh':'TheDreamEaters',
        'itd':'TheInnsmouthConspiracy',
        'har':'CoreSet',
        'nat':'NathanielCho',
        'def':'TheInnsmouthConspiracy',
        'tde':'TheDreamEaters',
        'bbt':'TheCircleUndone',
        'icc':'TheCircleUndone',
        'wos':'TheCircleUndone',
        'tdoy':'TheForgottenAge',
        'uad':'TheCircleUndone',
        '':'',
        '':'',

        # ThePathToCarcosa 卡尔克撒之路
        # TheForgottenAge 失落的时代
        # TheDreamEaters 猫头
        # TheCircleUndone 万象无终 (斜8字)
        }
    return safe_get(collection_map,collection,'')

# copyrigh 的mapping , 用当前的collection 来定位出版年份
def map_copyright(collection):
    year_map = {
        'CoreSet' :'<family "Arial"><cop> 2016 FFG</family>',
        'TheDunwichLegacy'   :'<family "Arial"><cop> 2016 FFG</family>',
        'CurseOfTheRougarou' :'<family "Arial"><cop> 2016 FFG</family>',
        'CarnevaleOfHorrors' :'<family "Arial"><cop> 2016 FFG</family>',
        'TheForgottenAge' :'<family "Arial"><cop> 2018 FFG</family>',
        'TheLabyrinthsOfLunacy' :'<family "Arial"><cop> 2016 FFG</family>',
        'ReturnToTheNightOfTheZealot' :'<family "Arial"><cop> 2016 FFG</family>',
        'GuardiansOfTheAbyss' :'<family "Arial"><cop> 2016 FFG</family>',
        'ReturnToTheDunwichLegacy' :'<family "Arial"><cop> 2016 FFG</family>',
        'ReturnToThePathToCarcosa' :'<family "Arial"><cop> 2016 FFG</family>',
        'TheDreamEaters' :'<family "Arial"><cop> 2016 FFG</family>',
        'MurderAtTheExcelsiorHotel' :'<family "Arial"><cop> 2016 FFG</family>',
        'ParallelInvestigators' :'<family "Arial"><cop> 2016 FFG</family>',
        'TheBlobThatAteEverything' :'<family "Arial"><cop> 2016 FFG</family>',
        'ReturnToTheForgottenAge' :'<family "Arial"><cop> 2016 FFG</family>',
        'HarveyWalters' :'<family "Arial"><cop> 2016 FFG</family>',
        'StellaClark' :'<family "Arial"><cop> 2019 FFG</family>',        
        'WinifredHabbamock' :'<family "Arial"><cop> 2019 FFG</family>',
        'WarOfTheOuterGods':'<family "Arial"><cop> 2016 FFG</family>',

        'EdgeOfTheEarthInv':'<family "Arial"><cop> 2021 FFG</family>',
        'TheDreamEaters':'<family "Arial"><cop> 2019 FFG</family>',
        'TheInnsmouthConspiracy':'<family "Arial"><cop> 2020 FFG</family>',        
        'TheScarletKeysInv':'<family "Arial"><cop> 2022 FFG</family>',        
        'ThePathToCarcosa' :'<family "Arial"><cop> 2017 FFG</family>',
        'JacquelineFine' :'<family "Arial"><cop> 2020 FFG</family>',
        'fhvp' :'<family "Arial"><cop> 2024 FFG</family>',
        'TheCircleUndone' :'<family "Arial"><cop> 2018 FFG</family>',
        'NathanielCho' :'<family "Arial"><cop> 2019 FFG</family>',
}
    return safe_get(year_map,collection,collection)


def download_file(url, save_dir, timeout=10):
    """下载单个文件"""
    try:
        # 获取文件名
        filename = os.path.basename(url)
        save_path = os.path.join(save_dir, filename)
        if Path(save_path).exists():
            return True, url, None
        
        # 发送请求
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            
            # 写入文件
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            return True, url, None
        
    except Exception as e:
        return False, url, str(e)

def download_manager(url_list, save_dir, max_workers=5):
    """批量下载管理器"""
    # 创建目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 进度统计
    success_count = 0
    error_count = 0
    
    # 使用线程池加速下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url in url_list:
            
            futures.append(executor.submit(download_file, url, save_dir))
        
        # 处理结果
        for future in futures:
            status, url, error = future.result()
            if status:
                print(f"[✓] 下载成功: {url}")
                success_count += 1
            else:
                print(f"[×] 下载失败: {url} \n    错误信息: {error}")
                error_count += 1
    
    # 输出统计
    print(f"\n下载完成！成功 {success_count} 个，失败 {error_count} 个")

# 处理图片下载
def init_picture(url_list):
    # 目标目录
    save_directory = "D:\\Projects\\Arkham-Horror-LCG-Cards\\temp"    
    # 执行下载
    download_manager(url_list, save_directory)
    # print(url_list)


def fix_file_name(name) -> str:
    return name.replace('!','').replace('"','').replace("?",'')

#将json 整理成Strange Eons可导入的csv格式 (有些顺序很关键 , 比如portScale 需要在portSource 之后)
def init_skill_csv_json(original_json):
    card_list = []
    url_list = []
    card_map={
        'guardian':'Guardian',
        'seeker':'Seeker',
        'rogue':'Rogue',        
        'mystic':'Mystic',
        'survivor':'Survivor',
        'neutral':'Neutral',
        'unknown':'unknown',
    }

    for card in original_json:
        skill_list = sort_skill(card)
        pack_code = safe_get(card,'pack_code','unknown')        
        collection = map_collection(pack_code)
        copy_right = map_copyright(collection)
        
        filename = fix_file_name(safe_get(card,'name','unknown'))
        xp = safe_get(card,'xp','unknown')
        if xp > 0:
            filename = filename + ' (' + str(xp) + ')'
        print("名称",filename,pack_code)
        result = {
            'file': filename,
            'name': safe_get(card,'name','unknown'),
            '$SpecialText': safe_get(card,'','unknown'),
            'portSource': 'D:\\Projects\\Arkham-Horror-LCG-Cards\\temp\\'+str(safe_get(card,'code','0'))+'.png',
            'portX': safe_get(card,'','0'),
            'portY': '70',
            'portScale': 1.25,
            '$Unique': safe_get(card,'','unknown'),
            '$CardClass': card_map.get(safe_get(card,'faction_code','unknown')),
            '$ResourceCost': safe_get(card,'cost','0'),
            '$Level': safe_get(card,'xp','unknown'),
            '$Skill1': skill_list[0],
            '$Skill2': skill_list[1],
            '$Skill3': skill_list[2],
            '$Skill4': skill_list[3],
            '$Skill5': skill_list[4],
            '$Skill6': skill_list[5],
            '$Artist': safe_get(card,'illustrator','unknown'),            
            '$Copyright': copy_right,
            '$Traits': safe_get(card,'traits','unknown'),
            '$Keywords': '',
            '$Rules': safe_get(card,'text',''),
            '$Flavor': safe_get(card,'flavor',''),
            '$Victory': '',
            '$Collection': collection,
            '$CollectionNumber': safe_get(card,'position','unknown'),
        }


        card_list.append(result)        
        url_list.append("https://zh.arkhamdb.com/bundles/cards/"+safe_get(card,'code','0')+".png")
        init_picture(url_list)

    return card_list

#将json 整理成Strange Eons可导入的csv格式 (有些顺序很关键 , 比如portScale 需要在portSource 之后)
def init_event_csv_json(original_json):
    card_list = []
    url_list = []
    card_map={
        'guardian':'Guardian',
        'seeker':'Seeker',
        'rogue':'Rogue',        
        'mystic':'Mystic',
        'survivor':'Survivor',
        'neutral':'Neutral',
        'unknown':'unknown',
    }

    for card in original_json:
        skill_list = sort_skill(card)
        pack_code = safe_get(card,'pack_code','unknown')        
        collection = map_collection(pack_code)
        copy_right = map_copyright(collection)
        
        filename = fix_file_name(safe_get(card,'name','unknown'))
        xp = safe_get(card,'xp','unknown')
        if xp > 0:
            filename = filename + ' (' + str(xp) + ')'
        print("名称",filename,pack_code,safe_get(card,'subtype_code',''))
        result = {
            'file': filename,
            'name': safe_get(card,'name','unknown'),
            '$SpecialText': safe_get(card,'','unknown'),
            'portSource': 'D:\\Projects\\Arkham-Horror-LCG-Cards\\temp\\'+str(safe_get(card,'code','0'))+'.png',
            'portX': safe_get(card,'','0'),
            'portY': '120',
            'portScale': 1.35,
            '$Unique': safe_get(card,'','unknown'),
            '$CardClass': card_map.get(safe_get(card,'faction_code','unknown')),
            '$ResourceCost': safe_get(card,'cost','0'),
            '$Level': safe_get(card,'xp','unknown'),
            '$Skill1': skill_list[0],
            '$Skill2': skill_list[1],
            '$Skill3': skill_list[2],
            '$Skill4': skill_list[3],
            '$Skill5': skill_list[4],
            '$Skill6': skill_list[5],
            '$Artist': safe_get(card,'illustrator','unknown'),            
            '$Copyright': copy_right,
            '$Traits': safe_get(card,'traits','unknown'),
            '$Keywords': '',
            '$Rules': safe_get(card,'text',''),
            '$Flavor': safe_get(card,'flavor',''),
            '$Victory': '',
            '$Collection': collection,
            '$CollectionNumber': safe_get(card,'position','unknown'),

        }
        if safe_get(card,'code','unknown') == '03238':
            print('result',card)


        card_list.append(result)        
        url_list.append("https://zh.arkhamdb.com/bundles/cards/"+safe_get(card,'code','0')+".png")
        # init_picture(url_list)

    return card_list


#将json 整理成Strange Eons可导入的csv格式 (有些顺序很关键 , 比如portScale 需要在portSource 之后)
def init_asset_csv_json(original_json):
    card_list = []
    url_list = []
    card_map={
        'guardian':'Guardian',
        'seeker':'Seeker',
        'rogue':'Rogue',        
        'mystic':'Mystic',
        'survivor':'Survivor',
        'neutral':'Neutral',
        'unknown':'unknown',
    }

    for card in original_json:
        skill_list = sort_skill(card)
        pack_code = safe_get(card,'pack_code','unknown')        
        collection = map_collection(pack_code)
        copy_right = map_copyright(collection)
        
        filename = fix_file_name(safe_get(card,'name','unknown'))
        xp = safe_get(card,'xp','unknown')
        if xp > 0:
            filename = filename + ' (' + str(xp) + ')'
        print("名称",filename,pack_code)
        result = {
            'file': filename,
            'name': safe_get(card,'name','unknown'),
            '$SpecialText': safe_get(card,'','unknown'),
            'portSource': 'D:\\Projects\\Arkham-Horror-LCG-Cards\\temp\\'+str(safe_get(card,'code','0'))+'.png',
            'portX': safe_get(card,'','0'),
            'portY': '120',
            'portScale': 1.35,
            '$Unique': safe_get(card,'','unknown'),
            '$CardClass': card_map.get(safe_get(card,'faction_code','unknown')),
            '$ResourceCost': safe_get(card,'cost','0'),
            '$Level': safe_get(card,'xp','unknown'),
            '$Skill1': skill_list[0],
            '$Skill2': skill_list[1],
            '$Skill3': skill_list[2],
            '$Skill4': skill_list[3],
            '$Skill5': skill_list[4],
            '$Skill6': skill_list[5],
            '$Artist': safe_get(card,'illustrator','unknown'),            
            '$Copyright': copy_right,
            '$Traits': safe_get(card,'traits','unknown'),
            '$Keywords': '',
            '$Rules': safe_get(card,'text',''),
            '$Flavor': safe_get(card,'flavor',''),
            '$Victory': '',
            '$Collection': collection,
            '$CollectionNumber': safe_get(card,'position','unknown'),

        }
        if safe_get(card,'code','unknown') == '03238':
            print('result',card)


        card_list.append(result)        
        url_list.append("https://zh.arkhamdb.com/bundles/cards/"+safe_get(card,'code','0')+".png")
        init_picture(url_list)

    return card_list

#遍历json 路径
def find_json_files(root_dir):
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                absolute_path = os.path.join(root, file)
                json_files.append(absolute_path)
    return json_files


if __name__ == "__main__":

    processed_cards = load_cards(find_json_files(r"D:\Projects\arkhamdb-json-data\pack"))
    processed_cards_zh = load_cards(find_json_files(r"D:\Projects\arkhamdb-json-data\translations\zh\pack"))        

    processed_cards_merge = specific_key_merge(processed_cards,processed_cards_zh)

    for card in processed_cards_merge:
        if card['code'] == '07308':
            print(card)

    # 打印处理后的结构化数据
    # for card in processed_cards_merge:
    #     print(f"\n【{card['name']}】")
    #     print(f"code: {card['code']}")
        
    #     # 根据不同类型显示特征信息
    #     if card['type'] == 'asset':
    #         print(f"类型: {card['type']}")
    #         print(f"XP: {card['xp']}")
    #         print(f"装备槽: {card['slot']}")
    #         print(f"理智值: {card['sanity']}")
    #         print(f"消耗: {card['cost']}")
    #         print(f"skill_agility: {card['skill_agility']}")
    #         print(f"skill_combat: {card['skill_combat']}")
    #         print(f"skill_intellect: {card['skill_intellect']}")
    #         print(f"skill_willpower: {card['skill_willpower']}")
    #         print(f"skill_wild: {card['skill_wild']}")
            
    #     elif card['type'] == 'treachery':
    #         print(f"隐藏属性: {'是' if card['hidden'] else '否'}")
    #         print(f"子类型: {card['subtype']}")

    #     elif card['type'] == 'skill':
    #         print(f"XP: {card['xp']}")
    #         print(f"faction_code: {card['faction_code']}")
    #         print(f"skill_combat: {card['skill_combat']}")
    #         print(f"skill_agility: {card['skill_agility']}")
    #         print(f"skill_wild: {card['skill_wild']}")
    #         print(f"skill_willpower: {card['skill_willpower']}")
    #         print(f"skill_intellect: {card['skill_intellect']}")
    #         print(f"illustrator: {card['illustrator']}")
    #         print(f"position: {card['position']}")
    #         print(f"pack_code: {card['pack_code']}")
        
    #     # 显示公共字段
    #     if card['traits'] != '':
    #         print(f"特性: {card['traits']}")
    #     if card['text'] != '':
    #         print(f"效果描述: {card['text']}")
    #     if card['flavor'] != '':
    #         print(f"flavor: {card['flavor']}")
            
    #     print("=" * 50)

    # skill_cards = filter_skill_cards(processed_cards_merge)   
    # skill_csv_json_list = init_skill_csv_json(processed_cards_merge)
    
    # json_to_csv(
    #         json_data=skill_csv_json_list,
    #         csv_path="D:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_skill.csv",
    #         encoding='utf-8'
    #     )


    event_cards = filter_event_cards(processed_cards_merge)
    event_csv_json_list = init_event_csv_json(event_cards)

    json_to_csv(
        json_data=event_csv_json_list,
        csv_path="D:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_event.csv",
        encoding='utf-8'
    )

    # asset_cards = filter_asset_cards(processed_cards_merge)
    # asset_csv_json_list = init_asset_csv_json(asset_cards)

    # json_to_csv(
    #     json_data=asset_csv_json_list,
    #     csv_path="D:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_asset.csv",
    #     encoding='utf-8'
    # )


# todo
# - 技能图标 (看看顺序 , 然后计算排序)
# - 截图 (判断如果没有该图片就下载)
# - 收藏 (应该可以用mapping 来获取)
# - 版权准确性 (按照年份批量制作?)
# - 各种标志要换成标签
# - 找不到对应的collection (图片右下角标志)
