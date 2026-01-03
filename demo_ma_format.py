#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MA格式图片处理演示脚本

这个脚本展示如何处理具有MA<YYYYMMDDHHMMSS>***格式文件名的图片。
"""

import tempfile
import logging
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_image(path: Path, filename: str):
    """创建一个测试用的PNG图片文件"""
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


def demonstrate_ma_format():
    """演示MA格式的处理"""
    
    print("\n" + "="*70)
    print("MA格式图片处理演示")
    print("="*70 + "\n")
    
    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        demo_dir = Path(tmpdir) / "ma_format_demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试图片
        test_files = [
            ("MA201203141423570096-12-000000.png", "2012-03-14 14:23:57"),
            ("MA20201215101530.png", "2020-12-15 10:15:30"),
            ("MA20000101000000.png", "2000-01-01 00:00:00"),
            ("MA20231225235959photo.png", "2023-12-25 23:59:59"),
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
        print("-"*70)
        print("提取过程演示:")
        print("-"*70 + "\n")
        
        import re
        
        for filepath, expected_time in created_files:
            filename = filepath.stem  # 不含扩展名
            
            # 模拟提取过程
            match = re.match(r'^MA(\d{14})', filename)
            if match:
                datetime_str = match.group(1)
                extracted_time = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
                
                print(f"文件: {filepath.name}")
                print(f"  提取的时间戳: {datetime_str}")
                print(f"  解析后的时间: {extracted_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  期望的时间:   {expected_time}")
                
                if str(extracted_time) == expected_time:
                    print("  结果: ✅ 匹配")
                else:
                    print("  结果: ❌ 不匹配")
                print()
        
        print("\n" + "="*70)
        print("演示完成！")
        print("="*70)
        
        # 显示用法提示
        print("\n💡 使用提示:\n")
        print("1. 将具有 MA<YYYYMMDDHHMMSS>*** 格式的图片放在目录中")
        print("2. 运行: python main.py /path/to/image/directory/")
        print("3. 程序会自动:")
        print("   - 识别MA格式文件名")
        print("   - 提取时间戳 (YYYYMMDDHHMMSS)")
        print("   - 更新图片的EXIF拍摄时间")
        print("   - 输出处理日志")
        print()
        
        # 显示实际的处理流程
        print("📋 处理流程:\n")
        print("   输入: MA201203141423570096-12-000000.jpg")
        print("   ↓")
        print("   识别: MA开头 + 14位数字")
        print("   ↓")
        print("   提取: 20120314 14 23 57")
        print("   ↓")
        print("   解析: 2012年03月14日 14:23:57")
        print("   ↓")
        print("   写入: 图片EXIF DateTimeOriginal")
        print("   ↓")
        print("   输出: MA201203141423570096-12-000000.jpg (已更新时间)")
        print()


if __name__ == '__main__':
    demonstrate_ma_format()
