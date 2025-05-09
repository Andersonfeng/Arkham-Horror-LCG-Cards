slot='Hand'

slot1 = 'None'
slot2 = 'None'
if slot == '':
    slot = 'None'
else:
    slot_list = slot.split('.')
    slot1 = slot_list[0]        
    if len(slot_list) > 1:
        slot2 = slot_list[1]
    else:
        slot2 = 'None'

    if slot1=='Hand x2':
        slot1 = '2 Hands'
    elif slot1=='Arcane x2':
        slot1 = '2 Arcane'

print(slot1,slot2)