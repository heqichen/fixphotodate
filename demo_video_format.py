#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-<YYYY-MM-DD-HH-mm-ss>***格式视频处理演示脚本

这个脚本展示如何处理具有video-<YYYY-MM-DD-HH-mm-ss>***格式文件名的MP4视频。
"""

import tempfile
from pathlib import Path
from datetime import datetime
import re


def create_test_video(path: Path, filename: str):
    """创建一个测试用的MP4视频文件（最小有效MP4）"""
    # 创建最小的有效MP4文件（空的MP4盒结构）
    # ftyp盒 (file type box)
    ftyp = bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,  # box size and type
        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x00, 0x00,  # major brand and version
        0x69, 0x73, 0x6F, 0x6D, 0x61, 0x76, 0x63, 0x31,  # compatible brands
        0x6D, 0x70, 0x34, 0x31, 0x64, 0x61, 0x73, 0x68
    ])
    
    full_path = path / filename
    with open(full_path, 'wb') as f:
        f.write(ftyp)
    
    return full_path


def demonstrate_video_format():
    """演示video格式的处理"""
    
    print("\n" + "="*75)
    print("video-<YYYY-MM-DD-HH-mm-ss>***格式视频处理演示")
    print("="*75 + "\n")
    
    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        demo_dir = Path(tmpdir) / "video_format_demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试视频
        test_files = [
            ("video-2012-03-17-23-48-09.mp4", "2012-03-17 23:48:09"),
            ("video-2020-12-15-10-15-30.mp4", "2020-12-15 10:15:30"),
            ("video-2000-01-01-00-00-00.mp4", "2000-01-01 00:00:00"),
            ("video-2023-12-25-23-59-59.mp4", "2023-12-25 23:59:59"),
        ]
        
        print("📁 创建测试目录:", demo_dir)
        print("\n🎬 创建测试视频文件:\n")
        
        created_files = []
        for filename, expected_time in test_files:
            filepath = create_test_video(demo_dir, filename)
            created_files.append((filepath, expected_time))
            print(f"   ✓ {filename}")
            print(f"     预期提取的时间: {expected_time}")
            print()
        
        # 演示提取过程
        print("-"*75)
        print("提取过程演示:")
        print("-"*75 + "\n")
        
        for filepath, expected_time in created_files:
            filename = filepath.stem  # 不含扩展名
            
            # 模拟提取过程
            match = re.match(r'^video-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})', filename)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                second = int(match.group(6))
                
                extracted_time = datetime(year, month, day, hour, minute, second)
                
                print(f"文件: {filepath.name}")
                print("  识别模式: video-YYYY-MM-DD-HH-mm-ss")
                print(f"  提取的值: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
                print(f"  解析后的时间: {extracted_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  期望的时间:   {expected_time}")
                
                if extracted_time.strftime('%Y-%m-%d %H:%M:%S') == expected_time:
                    print("  结果: ✅ 匹配")
                else:
                    print("  结果: ❌ 不匹配")
                print()
        
        print("\n" + "="*75)
        print("演示完成！")
        print("="*75)
        
        # 显示用法提示
        print("\n💡 使用提示:\n")
        print("1. 将具有 video-<YYYY-MM-DD-HH-mm-ss>*** 格式的MP4文件放在目录中")
        print("2. 运行: python main.py /path/to/video/directory/")
        print("3. 程序会自动:")
        print("   - 识别video格式文件名")
        print("   - 提取时间戳 (YYYY-MM-DD-HH-mm-ss)")
        print("   - 更新视频的MP4元数据创建时间")
        print("   - 输出处理日志")
        print()
        
        # 显示实际的处理流程
        print("📋 处理流程:\n")
        print("   输入: video-2012-03-17-23-48-09.mp4")
        print("   ↓")
        print("   识别: video-开头 + YYYY-MM-DD-HH-mm-ss格式")
        print("   ↓")
        print("   提取: 2012-03-17 23:48:09")
        print("   ↓")
        print("   验证: 检查日期有效性")
        print("   ↓")
        print("   写入: 视频MP4元数据 creation_time")
        print("   ↓")
        print("   输出: video-2012-03-17-23-48-09.mp4 (已更新时间)")
        print()
        
        # 显示支持的格式变体
        print("📝 支持的文件名变体:\n")
        print("   video-2012-03-17-23-48-09.mp4          标准格式")
        print("   video-2012-03-17-23-48-09-123456.mp4   有额外后缀")
        print("   video-2012-03-17-23-48-09-extra.mp4    任意后缀")
        print()


if __name__ == '__main__':
    demonstrate_video_format()
