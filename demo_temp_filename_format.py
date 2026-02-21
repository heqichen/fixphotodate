#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时文件名<YYYY-MM-DD HH.mm.ss>***格式图片处理演示脚本

这个脚本展示如何处理具有临时文件名<YYYY-MM-DD HH.mm.ss>***格式文件名的JPG/JPEG图片。
"""

import tempfile
from pathlib import Path
from datetime import datetime
import re


def create_test_image(path: Path, filename: str):
    """创建一个测试用的PNG图片文件（最小有效PNG）"""
    # 创建最小的有效PNG文件（1x1像素的透明PNG）
    png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG签名
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR块
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT块
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND块
        0x42, 0x60, 0x82
    ])
    
    full_path = path / filename
    with open(full_path, 'wb') as f:
        f.write(png_bytes)
    
    return full_path


def demonstrate_temp_filename_format():
    """演示临时文件名格式的处理"""
    
    print("\n" + "="*80)
    print("临时文件名<YYYY-MM-DD HH.mm.ss>***格式图片处理演示")
    print("="*80 + "\n")
    
    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        demo_dir = Path(tmpdir) / "temp_filename_demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试图片
        test_files = [
            ("临时文件名2012-03-19 02.59.06.jpg", "2012-03-19 02:59:06"),
            ("temp2020-12-15 10.15.30.jpg", "2020-12-15 10:15:30"),
            ("screenshot2000-01-01 00.00.00.png", "2000-01-01 00:00:00"),
            ("photo2023-12-25 23.59.59.jpg", "2023-12-25 23:59:59"),
        ]
        
        print("📁 创建测试目录:", demo_dir)
        print("\n📷 创建测试图片文件:\n")
        
        created_files = []
        for filename, expected_time in test_files:
            filepath = create_test_image(demo_dir, filename)
            created_files.append((filepath, expected_time))
            print(f"   ✓ {filename}")
            print(f"     预期提取的时间: {expected_time}")
            print()
        
        # 演示提取过程
        print("-"*80)
        print("提取过程演示:")
        print("-"*80 + "\n")
        
        for filepath, expected_time in created_files:
            filename = filepath.stem  # 不含扩展名
            
            # 模拟提取过程
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})', filename)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                second = int(match.group(6))
                
                extracted_time = datetime(year, month, day, hour, minute, second)
                
                print(f"文件: {filepath.name}")
                print("  识别模式: YYYY-MM-DD HH.mm.ss")
                print(f"  提取的值: {year}-{month:02d}-{day:02d} {hour:02d}.{minute:02d}.{second:02d}")
                print(f"  解析后的时间: {extracted_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  期望的时间:   {expected_time}")
                
                if extracted_time.strftime('%Y-%m-%d %H:%M:%S') == expected_time:
                    print("  结果: ✅ 匹配")
                else:
                    print("  结果: ❌ 不匹配")
                print()
        
        print("\n" + "="*80)
        print("演示完成！")
        print("="*80)
        
        # 显示用法提示
        print("\n💡 使用提示:\n")
        print("1. 将具有 临时文件名<YYYY-MM-DD HH.mm.ss>*** 格式的图片放在目录中")
        print("2. 运行: python main.py /path/to/image/directory/")
        print("3. 程序会自动:")
        print("   - 识别临时文件名格式")
        print("   - 提取时间戳 (YYYY-MM-DD HH.mm.ss)")
        print("   - 更新图片的EXIF拍摄时间")
        print("   - 输出处理日志")
        print()
        
        # 显示实际的处理流程
        print("📋 处理流程:\n")
        print("   输入: 临时文件名2012-03-19 02.59.06.jpg")
        print("   ↓")
        print("   识别: 文件名中包含 YYYY-MM-DD HH.mm.ss 格式")
        print("   ↓")
        print("   提取: 2012-03-19 02:59:06")
        print("   ↓")
        print("   验证: 检查日期时间有效性")
        print("   ↓")
        print("   写入: 图片EXIF DateTimeOriginal")
        print("   ↓")
        print("   输出: 临时文件名2012-03-19 02.59.06.jpg (已更新时间)")
        print()
        
        # 显示支持的格式变体
        print("📝 支持的文件名变体:\n")
        print("   临时文件名2012-03-19 02.59.06.jpg          标准格式")
        print("   temp2020-12-15 10.15.30.png               简短前缀")
        print("   screenshot2020-12-15 10.15.30.jpeg        任意前缀")
        print("   2012-03-19 02.59.06.jpg                   无前缀")
        print("   file-2020-12-15 10.15.30-extra.jpg        有多个后缀")
        print()


if __name__ == '__main__':
    demonstrate_temp_filename_format()
