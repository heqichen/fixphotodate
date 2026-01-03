#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MA格式文件名时间提取功能
"""

import re
from datetime import datetime

def extract_datetime_from_ma_format(filename: str):
    """
    从特殊格式的文件名提取时间戳：MA<YYYYMMDDHHMMSS>***
    例如：MA201203141423570096-12-000000 → 2012-03-14 14:23:57
    """
    try:
        # 检查是否以MA开头，并且后面跟14位数字（YYYYMMDDHHMMSS）
        match = re.match(r'^MA(\d{14})', filename)
        if match:
            datetime_str = match.group(1)  # 提取14位数字
            # 格式：YYYYMMDDHHMMSS
            dt = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            return dt
        
        return None
    except Exception as e:
        print(f"时间提取失败: {e}")
        return None


# 测试用例
test_cases = [
    ("MA201203141423570096-12-000000", "2012-03-14 14:23:57"),
    ("MA201203141423570096-12-000000.jpg", "2012-03-14 14:23:57"),
    ("MA20201215101530", "2020-12-15 10:15:30"),
    ("MA20000101000000", "2000-01-01 00:00:00"),
    ("MA20231225235959", "2023-12-25 23:59:59"),
    ("MA1999123123595900", "1999-12-31 23:59:59"),  # 边界值
    ("NotMA20201215101530", None),  # 不以MA开头
    ("MA2020121", None),  # 数字不足14位
    ("MA202012151015309999-extra", "2020-12-15 10:15:30"),  # 有额外后缀
]

print("=" * 70)
print("MA格式文件名时间提取测试")
print("=" * 70)

passed = 0
failed = 0

for filename, expected in test_cases:
    # 提取文件名部分（不含扩展名）
    name_without_ext = filename.split('.')[0]
    result = extract_datetime_from_ma_format(name_without_ext)
    
    if expected is None:
        expected_dt = None
    else:
        expected_dt = datetime.strptime(expected, '%Y-%m-%d %H:%M:%S')
    
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

print("\n" + "=" * 70)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 70)
