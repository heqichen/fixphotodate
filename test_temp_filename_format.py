#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试临时文件名<YYYY-MM-DD HH.mm.ss>***格式文件名时间提取功能
"""

import re
from datetime import datetime

def extract_datetime_from_temp_filename(filename: str):
    """
    从临时文件名格式提取时间戳：临时文件名<YYYY-MM-DD HH.mm.ss>***
    例如：临时文件名2012-03-19 02.59.06 → 2012-03-19 02:59:06
    """
    try:
        # 检查是否包含 YYYY-MM-DD HH.mm.ss 格式的时间戳
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})', filename)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            
            dt = datetime(year, month, day, hour, minute, second)
            return dt
        
        return None
    except Exception as e:
        print(f"时间提取失败: {e}")
        return None


# 测试用例
test_cases = [
    ("临时文件名2012-03-19 02.59.06", "2012-03-19 02:59:06"),
    ("临时文件名2012-03-19 02.59.06.jpg", "2012-03-19 02:59:06"),
    ("temp2020-12-15 10.15.30", "2020-12-15 10:15:30"),
    ("file2000-01-01 00.00.00", "2000-01-01 00:00:00"),
    ("video2023-12-25 23.59.59", "2023-12-25 23:59:59"),
    ("screenshot2020-12-15 10.15.30.png", "2020-12-15 10:15:30"),
    ("photo-2020-12-15 10.15.30-extra", "2020-12-15 10:15:30"),
    ("2012-03-19 02.59.06", "2012-03-19 02:59:06"),
    ("无前缀2012-03-19 02.59.06无后缀", "2012-03-19 02:59:06"),
    ("notimestamp2020-12-15", None),  # 缺少时间部分
    ("temp2020-13-15 10.15.30", None),  # 无效月份
    ("temp2020-12-32 10.15.30", None),  # 无效日期
    ("temp2020-12-15 25.15.30", None),  # 无效小时
    ("temp2020-12-15 10.60.30", None),  # 无效分钟
    ("temp2020-12-15 10.15.60", None),  # 无效秒
    ("2020-12-15 10.15", None),  # 秒缺失
    ("2020-12-15", None),  # 只有日期
    ("10.15.30", None),  # 只有时间
]

print("=" * 80)
print("临时文件名<YYYY-MM-DD HH.mm.ss>***格式文件名时间提取测试")
print("=" * 80)

passed = 0
failed = 0

for filename, expected in test_cases:
    # 提取文件名部分（不含扩展名）
    name_without_ext = filename.split('.')[0] if '.' in filename[-4:] else filename
    if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp', '.tiff')):
        name_without_ext = filename.rsplit('.', 1)[0]
    else:
        name_without_ext = filename
    
    result = extract_datetime_from_temp_filename(name_without_ext)
    
    if expected is None:
        expected_dt = None
    else:
        try:
            expected_dt = datetime.strptime(expected, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            expected_dt = None
    
    if result == expected_dt:
        status = "✅ PASS"
        passed += 1
    else:
        status = "❌ FAIL"
        failed += 1
    
    print(f"\n{status}")
    print(f"  输入:     {filename}")
    print(f"  期望:     {expected}")
    print(f"  实际:     {result}")

print("\n" + "=" * 80)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 80)
