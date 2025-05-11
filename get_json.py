import json
import csv
from pathlib import Path
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import re

# TODO:
# - 技能图标 (看看顺序 , 然后计算排序) [DONE]
# - 截图 (判断如果没有该图片就下载) [DONE]
# - 收藏 (应该可以用mapping 来获取) [DONE 50%]
# - 版权准确性 (按照年份批量制作?) [DONE 50%]
# - 各种标志要换成标签 [DONE]
# - 多class 的问题要考虑一下 [DONE]
# - filename 分类 [DONE]
# - 两张独特事件卡重做 [Done]
# - 做卡时先忽略限定卡组 restrictions [Done]
# - 忽略没有汉化的卡牌 [Done]
# - 同名同等级卡要考虑一下 [Done: 加上subname 了] 
'''
https://steamusercontent-a.akamaihd.net/ugc/10905241397881077175/CFFA53F8A3B0DE707B3C709F95E8C314D38A1898/

# SKILL
Guardian
16
https://steamusercontent-a.akamaihd.net/ugc/17732419635487435338/DE6A7931E001775024C25E65ED9C3A0B263914E5/
Seeker
16
https://steamusercontent-a.akamaihd.net/ugc/11402909173224140102/8E7C0B7703A3D0863F15FEED3B56614178688CB7/
Rogue
21
https://steamusercontent-a.akamaihd.net/ugc/14972634393972709854/4B088203321F079052526B6BFE37F2B077E934AE/
Mystic
15
https://steamusercontent-a.akamaihd.net/ugc/10943431180037000495/A13039E1524EA6F66E025A3323133C73DFFFC6BE/
Survivor
26
https://steamusercontent-a.akamaihd.net/ugc/17104993361052881179/39C7EED498EE8FD17C540C0D6C93B64ECF658C48/

Neutral
10
https://steamusercontent-a.akamaihd.net/ugc/18139753114041224948/1ECE756CE4434254422FE3E52113F3F10143F660/

# ASSET
Guardian
https://steamusercontent-a.akamaihd.net/ugc/10543334433840929116/93BE6F7D78F50557C04B6ACA039E5F761D29122D/
43
https://steamusercontent-a.akamaihd.net/ugc/10446415808110787879/1FF8E1D443DCE5D9C1143253D1DB66D178351AD0/

Seeker
https://steamusercontent-a.akamaihd.net/ugc/12779563778923896602/354D82F08C957C6165DA62926A536BE8E68525D3/
https://steamusercontent-a.akamaihd.net/ugc/10433539388238535803/436337BF51117B4C922850BC46AA4972FFCFA90B/
1
https://steamusercontent-a.akamaihd.net/ugc/10592950541985823431/6969E888A2D446FA46EB4D480B910C03539B8B3F/

Rogue
https://steamusercontent-a.akamaihd.net/ugc/15619834257663482819/B4E3F63B0EA4B3AFD47B29845150D7C984427E87/
54
https://steamusercontent-a.akamaihd.net/ugc/14139153343575391185/C00C51CFAD01E1EC73B3D6DAE837E759CA2AC5E4/

Mystic
https://steamusercontent-a.akamaihd.net/ugc/11126285996779418087/96032BB31874F532A3C2680D4B6C827203FDB9B3/
69
https://steamusercontent-a.akamaihd.net/ugc/10230792398903030630/E7F808F83593F158A8809602F739B3282711E5B0/

Survivor
https://steamusercontent-a.akamaihd.net/ugc/9300682814529985562/0DBCEFFB7A865944CD8FA86853D6370C489D0B1B/
41
https://steamusercontent-a.akamaihd.net/ugc/17224183804070964427/DF0A49EE5E8D99AD8499C7AB3340830B4BF4FB58/
Neutral
42
https://steamusercontent-a.akamaihd.net/ugc/14957673940978101251/D92568A1D5382A58313DE114587D77354AE8707F/


# Event
## Guardian
### 69
https://steamusercontent-a.akamaihd.net/ugc/17779736787007749983/1F536F611D75EA57973C941109EDA30C51EF3CE1/
### 20
https://steamusercontent-a.akamaihd.net/ugc/13626475346278529819/F9457F5DD8608E008E9F39C497B735F5D4EE7FCD/

Seeker
### 69
https://steamusercontent-a.akamaihd.net/ugc/17517563552056739163/A8CC42F77CD59F0987FC87AE08B0277252E56E7D/

### 1
https://steamusercontent-a.akamaihd.net/ugc/12923576918906896184/DFE8A439961F72ED66AA4EAEEF99BDF8368D3617/

Rogue
### 69
https://steamusercontent-a.akamaihd.net/ugc/13536926113318784458/04184789B2771F9A5854528177D1F34B3B596588/
### 5
https://steamusercontent-a.akamaihd.net/ugc/16081623492054780745/08414924D9B81527E9179D4A1EC19185FB913997/

Mystic
### 68
https://steamusercontent-a.akamaihd.net/ugc/9717304444944155577/122AAC859E14F47FEC48D1D83F8CC754E2AEF748/

Survivor
### 69
https://steamusercontent-a.akamaihd.net/ugc/16173992829996080790/906338EC3D32E1F4911341796F6861B211C5B567/
### 8
https://steamusercontent-a.akamaihd.net/ugc/15196312272121941373/7D433837A3610C414D1E97850DCDBBC0454D78E8/

Neutral
### 12
https://steamusercontent-a.akamaihd.net/ugc/9892996788443780851/8B477A6715DCEB5E928342CA087795850E1102D8/
'''



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
        "[per_investigator]" : "<per>",
        "[]" : "<rev>",
        "[]" : "<uni>",
        "[]" : "<per>",
        "[]" : "<bul>",
        "[]" : "<squ>",
        "[[" : "<b><i>",
        "]]" : "</i></b>",
        "- …" : "<bul> ...",
        "\n-" : "\n<bul>",
        "\n -" : "\n <bul>",
    }

    for old, new in replacements.items():
        text = text.replace(old,new)
    return text

def fix_X_cost(cost):    
    if '-' in cost:
        cost = 'X'    
    elif cost == 'None':
        return '-'
    elif cost == 'null':
        return "-"
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
        'faction_code': safe_get(card, 'faction_code', 'None'),
        'faction2_code': safe_get(card, 'faction2_code', 'None'),
        'faction3_code': safe_get(card, 'faction3_code', 'None'),
        'illustrator': safe_get(card, 'illustrator', '未知作家'),
        'traits': safe_get(card, 'traits', '')+'.',
        'text': text,
        'flavor': '\n'+safe_get(card, 'flavor', ''),
        'pack_code': safe_get(card, 'pack_code', ''),
        'position': safe_get(card, 'position', '0'),
        'subname': safe_get(card, 'subname', ''),
        'encounter_code': safe_get(card, 'encounter_code', ''),
        'health': safe_get(card, 'health', ''),
        'sanity': safe_get(card, 'sanity', ''),
        'slot': safe_get(card, 'slot', ''),
        'unique': safe_get(card, 'is_unique', ''),
        'skill_combat': safe_get(card, 'skill_combat', '0'),
        'skill_agility': safe_get(card, 'skill_agility', '0'),
        'skill_wild': safe_get(card, 'skill_wild', '0'),
        'skill_willpower': safe_get(card, 'skill_willpower', '0'),
        'skill_intellect': safe_get(card, 'skill_intellect', '0'),
        'victory': safe_get(card, 'victory', ''),
        'restrictions': safe_get(card, 'restrictions', ''),
    }

    # 动态处理不同卡片类型的特性字段
    card_type = result['type']    
    
    cost = str(safe_get(card, 'cost', 0))
    cost = fix_X_cost(cost)
    result.update({
        'cost': cost,
    })   
    return result

# 读取并处理文件
def load_cards(file_path_list):
    result_list = []
    for file_path in file_path_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for c in raw_data:
                    result = process_card(c)
                    if result['encounter_code'] == '':
                        result_list.append(result)
                    # result_list.append(process_card(c))
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
        fieldnames = list(dict.fromkeys(key for item in json_data for key in item))


        # 创建输出目录
        output_path = Path(csv_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入 CSV 文件
        with open(output_path, 'w', newline='', encoding=encoding) as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,                
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
        print(f"本次转换数目:{len(json_data)}")

    except Exception as e:
        print(f"转换失败：{str(e)}")

def _convert_value(value):
    """处理特殊数据类型"""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value

# 过滤技能牌
def filter_cards(card_list, type_field='type', target_type='skill'):
    """
    过滤指定类型的卡牌
    
    :param card_list: 原始卡牌列表
    :param type_field: 类型字段名（默认为 type_code）
    :param target_type: 目标类型（默认为 skill）
    :return: 过滤后的新列表
    """
    return [
        card.copy() for card in card_list
        # restrictions = safe_get(card, 'restrictions', '')
        if str(card.get(type_field, '')).lower() == target_type.lower()
            and 'weakness' not in str(card.get('subtype', '')).lower()  #排除弱点卡
            and safe_get(card, 'restrictions', '') == '' #排除专属卡

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
        key_fields = ['flavor', 'name', 'text', 'traits','subname']

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

# 获取有共同文本的json
def filter_common_json(english_json_list, chinese_json_list):
    """
    只获取有翻译的json
    """
    chinese_codes = {item["code"] for item in chinese_json_list if "code" in item}
    
    # 过滤英文列表中存在于中文列表的条目
    filtered_english = [
        item for item in english_json_list
        if item.get("code") in chinese_codes
    ]
    
    return filtered_english

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
        'rttcu':'ReturnToTheCircleUndone',
        'tcoa':'TheForgottenAge',
        'lod':'TheInnsmouthConspiracy',
        'tsn':'TheCircleUndone',
        'rtptc':'ReturnToThePathToCarcosa',
        'fgg':'TheCircleUndone',
        'tuo':'ThePathToCarcosa',
        'fgg':'TheCircleUndone',
        'apot':'ThePathToCarcosa',
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
        'ReturnToTheCircleUndone' :'<family "Arial"><cop> 2021 FFG</family>',
        'ReturnToThePathToCarcosa' :'<family "Arial"><cop> 2019 FFG</family>',
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
    save_directory = "e:\\Projects\\Arkham-Horror-LCG-Cards\\temp"    
    # 执行下载
    download_manager(url_list, save_directory)
    # print(url_list)


def fix_file_name(name) -> str:
    if name.startswith('.'):
        name = '點' + name[1:]
    return name.replace('!','').replace('"','').replace("?",'')

# 处理职阶名称
def solve_class_name(card_class, card_class2, card_class3):
    card_class_name = str(card_class)
    card_class2_name = str(card_class2)
    card_class3_name = str(card_class3)

        
        
    if card_class2_name != '' and card_class2_name != 'None':
        card_class_name = card_class_name + '_'+ card_class2_name
        
    if card_class3_name != '' and card_class3_name != 'None':
        card_class_name = card_class_name + '_'+ card_class3_name

    if card_class2 == '' or card_class2 is None:
        card_class2='None'

    if card_class3 == '' or card_class3 is None:
        card_class3='None'
    return card_class_name,card_class2,card_class3


#将json 整理成Strange Eons可导入的csv格式 (有些顺序很关键 , 比如portScale 需要在portSource 之后)
def init_csv_json(original_json,portX,portY,portScale):
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
        card_class = card_map.get(safe_get(card,'faction_code','unknown'))
        card_class2 = card_map.get(safe_get(card,'faction2_code','None'))
        card_class3 = card_map.get(safe_get(card,'faction3_code','None'))
        code = safe_get(card,'code','unknown')    
        # if(code!='07189' and code!='54011'):
            # continue
        
        filename = fix_file_name(safe_get(card,'name','unknown'))

        card_class_name,card_class2, card_class3  = solve_class_name(card_class, card_class2, card_class3)

        xp = safe_get(card,'xp','unknown')
        if xp > 0:
            filename = filename + ' (' + str(xp) + ')' + ' '+ '['+card_class_name+']'
        else:
            filename = filename + ' ' + '['+card_class_name+']'

        type = card['type']
        filename = filename + '['+ type +']'
        subname = safe_get(card,'subname','')

        for tmp_card in card_list.copy():
            if tmp_card['file'] == filename:
                print('old_filename',filename)
                filename = filename + '[' + subname + ']'
                print('new_filename',filename)

        code = re.sub(r'\D','',str(safe_get(card,'code','0')))

        
        # print("名称",filename,pack_code,safe_get(card,'subtype_code',''),code ,card_class,card_class2,card_class3)

        # subtitle = safe_get(card,'subname','')
        # if subtitle:
        #     print('filename',filename,'subtitle',subtitle)

        slot1, slot2 = get_slot(card)


        
        health, sanity = get_health_sanity(card)        
        
        unique = safe_get(card,'unique','')
        if unique == True:
            unique = '1'
        else:
            unique = ''
        result = {
            'file': filename,
            '$Unique': unique,            
            'name': safe_get(card,'name','unknown'),
            '$Subtitle': subname,
            '$CardClass': card_class,
            '$CardClass2': card_class2,
            '$CardClass3': card_class3,
            '$ResourceCost': safe_get(card,'cost','0'),
            '$Level': safe_get(card,'xp','unknown'),
            '$Slot': slot1,
            '$Slot2': slot2,
            '$Stamina': health,
            '$Sanity': sanity,
            '$Skill1': skill_list[0],
            '$Skill2': skill_list[1],
            '$Skill3': skill_list[2],
            '$Skill4': skill_list[3],
            '$Skill5': skill_list[4],
            '$Skill6': skill_list[5],
            '$Copyright': copy_right,
            '$Traits': safe_get(card,'traits','unknown'),
            '$Rules': safe_get(card,'text',''),
            '$Flavor': safe_get(card,'flavor',''),
            '$Victory': safe_get(card,'victory',''),
            'portSource': 'E:\\Projects\\Arkham-Horror-LCG-Cards\\temp\\'+ code +'.png',
            'portScale': portScale,            
            'portX': portX,
            'portY': portY,
            '$Artist': safe_get(card,'illustrator','unknown'),
            '$Collection': collection,
            '$CollectionNumber': safe_get(card,'position','unknown'),

        }
        # if safe_get(card,'code','unknown') == '03238':
        #     print('result',card)

        
        card_list.append(result)        
        url_list.append("https://zh.arkhamdb.com/bundles/cards/"+safe_get(card,'code','0')+".png")
        # init_picture(url_list)

    return card_list

# 判断卡牌是否有血 恐
def get_health_sanity(card):
    health = safe_get(card,'health','')
    sanity = safe_get(card,'sanity','')    

    if isinstance(health,(int,float)) and health < 0:
        health = '*'
    if isinstance(sanity,(int,float)) and sanity < 0:
        sanity = '*'

    if health != '' and sanity == '':
        sanity = '-'
    elif health == '' and sanity != '':
        health = '-'
    elif health == '' and sanity == '':
        health = 'None'
        sanity = 'None'
    
    return health,sanity

# 获取手部槽位
def get_slot(card):
    slot_map = {
        'Ally':'Ally',
        'Accessory':'Accessory',
        'Body':'Body',
        'Hand':'1 Hand',
        'Hand x2':'2 Hands',
        'Arcane':'1 Arcane',
        'Arcane x2':'2 Arcane',
        'Tarot':'Tarot',
    }
    # Accessory
    # Ally
    slot = safe_get(card,'slot','')
    slot1 = 'None'
    slot2 = 'None'
    if slot == '':
        slot = 'None'
    else:
        slot_list = slot.split('.')
        slot1 = slot_list[0]
        slot1 = safe_get(slot_map,slot1.strip(),'None')
        if len(slot_list) > 1:
            slot2 = slot_list[1]
        
        slot2 = safe_get(slot_map,slot2.strip(),'None')    
    return slot1,slot2


#遍历json 路径
def find_json_files(root_dir):
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json') and 'encounter' not in file:
                absolute_path = os.path.join(root, file)
                json_files.append(absolute_path)    
    return json_files


if __name__ == "__main__":

    processed_cards = load_cards(find_json_files(r"D:\Projects\arkhamdb-json-data\pack"))
    processed_cards_zh = load_cards(find_json_files(r"D:\Projects\arkhamdb-json-data\translations\zh\pack"))        

    processed_cards = filter_common_json(processed_cards,processed_cards_zh)
    
    processed_cards_merge = specific_key_merge(processed_cards,processed_cards_zh)


    skill_cards = filter_cards(processed_cards_merge,target_type='skill')
    skill_csv_json_list = init_csv_json(skill_cards,'0','75',1.25)    
    json_to_csv(
        json_data=skill_csv_json_list,
        csv_path="E:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_skill.csv",
        encoding='utf-8'
    )

    event_cards = filter_cards(processed_cards_merge,target_type='event')
    event_csv_json_list = init_csv_json(event_cards,'0','118',1.25)    
    json_to_csv(
        json_data=event_csv_json_list,
        csv_path="E:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_event.csv",
        encoding='utf-8'
    )

    asset_cards = filter_cards(processed_cards_merge,target_type='asset')
    asset_csv_json_list = init_csv_json(asset_cards,'0','90',1.25)
    json_to_csv(
        json_data=asset_csv_json_list,
        csv_path="E:\\Projects\\Arkham-Horror-LCG-Cards\\Project\\New Task Name\\data_asset.csv",
        encoding='utf-8'
    )