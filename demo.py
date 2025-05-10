def safe_get(data, key, default=None):
    """安全获取嵌套字典值的通用方法"""
    return data.get(key, default)

slot='Hand'

slot_map = {
    'Hand':'1 Hand',
    'Hand x2':'2 Hands',
    'Arcane':'1 Arcane',
    'Arcane x2':'2 Arcane',
    'Ally':'Ally',
    'Accessory':'Accessory',
    'Body':'Body',
}
# Accessory
# Ally
slot = "Body. Arcane"
slot1 = 'None'
slot2 = 'None'
if slot == '':
    slot = 'None'
else:
    slot_list = slot.split('.')
    print("slot_list:",slot_list)
    slot1 = slot_list[0]
    slot1 = safe_get(slot_map,slot1.strip(),'None')
    if len(slot_list) > 1:
        slot2 = slot_list[1]
    
    slot2 = safe_get(slot_map,slot2.strip(),'None')
print(f"slot:{slot} slot1:{slot1} slot2:{slot2}")