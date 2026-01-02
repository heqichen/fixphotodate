#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例 - 如何使用照片和视频处理脚本
"""

from main import MediaProcessor
from pathlib import Path

def example_1_process_single_directory():
    """示例1: 处理单个目录"""
    print("示例1: 处理单个目录")
    print("=" * 50)
    
    # 处理单个目录
    processor = MediaProcessor('./20070922_mcm')
    processor.process_all()
    
    print("\n处理完成！")
    print(f"生成的MP4文件位置: {processor.source_dir}")
    print(f"移动的AVI文件位置: {processor.archive_dir}")


def example_2_process_multiple_directories():
    """示例2: 处理多个目录"""
    print("示例2: 处理多个目录")
    print("=" * 50)
    
    directories = [
        './20070922_mcm',
        './20070923_mcm',
        './20070924_mcm',
    ]
    
    for dir_path in directories:
        try:
            print(f"\n处理目录: {dir_path}")
            processor = MediaProcessor(dir_path)
            processor.process_all()
            print(f"✓ {dir_path} 处理完成")
        except Exception as e:
            print(f"✗ {dir_path} 处理失败: {e}")


def example_3_manual_image_processing():
    """示例3: 手动处理单个图片"""
    print("示例3: 手动处理单个图片")
    print("=" * 50)
    
    processor = MediaProcessor('./20070922_mcm')
    
    # 处理特定的图片文件
    image_path = Path('./20070922_mcm/S7300317.JPG')
    
    print(f"\n处理图片: {image_path.name}")
    
    # 读取EXIF日期
    exif_date = processor.get_exif_datetime(image_path)
    if exif_date:
        print(f"EXIF日期: {exif_date}")
    else:
        print("未找到EXIF日期")
        
        # 猜测日期
        guessed_date = processor.guess_datetime_from_filename(image_path)
        if guessed_date:
            print(f"猜测日期: {guessed_date}")
            
            # 更新EXIF
            processor.set_exif_datetime(image_path, guessed_date)
            print("已更新EXIF日期")


def example_4_manual_video_processing():
    """示例4: 手动处理单个视频"""
    print("示例4: 手动处理单个视频")
    print("=" * 50)
    
    from pathlib import Path
    
    processor = MediaProcessor('./20070922_mcm')
    
    # 处理特定的AVI文件
    avi_path = Path('./20070922_mcm/S7300333.AVI')
    
    if avi_path.exists():
        print(f"\n处理视频: {avi_path.name}")
        processor.process_avi(avi_path)
    else:
        print(f"文件不存在: {avi_path}")


def example_5_check_directory_date():
    """示例5: 查看目录解析的日期"""
    print("示例5: 查看目录解析的日期")
    print("=" * 50)
    
    processor = MediaProcessor('./20070922_mcm')
    
    dir_date = processor.get_directory_date()
    print(f"\n目录名: {processor.source_dir.name}")
    print(f"解析的日期: {dir_date}")


if __name__ == '__main__':
    import sys
    
    print("\n照片和视频处理脚本 - 使用示例")
    print("=" * 50)
    print("\n可用的示例:")
    print("  1. 处理单个目录")
    print("  2. 处理多个目录")
    print("  3. 手动处理单个图片")
    print("  4. 手动处理单个视频")
    print("  5. 查看目录解析的日期")
    print("\n使用方法:")
    print("  python3 examples.py <示例号>")
    print("\n或者直接导入使用:")
    print("  from examples import example_1_process_single_directory")
    print("  example_1_process_single_directory()")
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == '1':
            example_1_process_single_directory()
        elif example_num == '2':
            example_2_process_multiple_directories()
        elif example_num == '3':
            example_3_manual_image_processing()
        elif example_num == '4':
            example_4_manual_video_processing()
        elif example_num == '5':
            example_5_check_directory_date()
        else:
            print(f"未知的示例: {example_num}")
