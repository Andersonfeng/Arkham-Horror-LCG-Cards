def safe_get(data, key, default=None):
    """安全获取嵌套字典值的通用方法"""
    return data.get(key, default)

replace_mapping={
        '[Guardian]':'',
        '[Seeker]':'',
        '[Rogue]':'',
        '[Mystic]':'',
        '[Survivor]':'',
        '[Neutral]':'',
        '[skill]':'',
    }
for key in replace_mapping:
    print(key)