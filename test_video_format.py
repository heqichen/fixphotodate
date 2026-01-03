#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试video-<YYYY-MM-DD-HH-mm-ss>***格式文件名时间提取功能
"""

import re
from datetime import datetime

def extract_datetime_from_video_format(filename: str):
    """
    从特殊格式的视频文件名提取时间戳：video-<YYYY-MM-DD-HH-mm-ss>***
    例如：video-2012-03-17-23-48-09 → 2012-03-17 23:48:09
    """
    try:
        # 检查是否以video-开头，并且后面跟YYYY-MM-DD-HH-mm-ss格式
        match = re.match(r'^video-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})', filename)
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
    ("video-2012-03-17-23-48-09", "2012-03-17 23:48:09"),
    ("video-2012-03-17-23-48-09.mp4", "2012-03-17 23:48:09"),
    ("video-2020-12-15-10-15-30", "2020-12-15 10:15:30"),
    ("video-2000-01-01-00-00-00", "2000-01-01 00:00:00"),
    ("video-2023-12-25-23-59-59", "2023-12-25 23:59:59"),
    ("video-2020-12-15-10-15-30-123456", "2020-12-15 10:15:30"),
    ("video-2020-12-15-10-15-30-extra", "2020-12-15 10:15:30"),
    ("Notvideo-2020-12-15-10-15-30", None),  # 不以video-开头
    ("video-2020-13-15-10-15-30", None),  # 无效的月份
    ("video-2020-12-32-10-15-30", None),  # 无效的日期
    ("video-2020-12-15-25-15-30", None),  # 无效的小时
    ("video-2020-12-15-10-60-30", None),  # 无效的分钟
    ("video-2020-12-15-10-15-60", None),  # 无效的秒
    ("video-202-12-15-10-15-30", None),  # 年份只有3位
    ("video-2020-2-15-10-15-30", None),  # 月份只有1位
]

print("=" * 75)
print("video-<YYYY-MM-DD-HH-mm-ss>***格式文件名时间提取测试")
print("=" * 75)

passed = 0
failed = 0

for filename, expected in test_cases:
    # 提取文件名部分（不含扩展名）
    name_without_ext = filename.split('.')[0]
    result = extract_datetime_from_video_format(name_without_ext)
    
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

print("\n" + "=" * 75)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 75)
