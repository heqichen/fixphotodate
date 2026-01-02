#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本 - 展示脚本的核心功能
不实际修改文件，只显示将会执行的操作
"""

import sys
from pathlib import Path
from main import MediaProcessor
import logging

# 设置日志为仅显示INFO和以上
logging.basicConfig(level=logging.INFO)

def demo_analyze():
    """演示分析功能 - 不修改文件"""
    print("\n" + "="*60)
    print("演示：分析目录结构和文件")
    print("="*60 + "\n")
    
    source_dir = Path('./20070922_mcm')
    
    if not source_dir.exists():
        print(f"❌ 目录不存在: {source_dir}")
        return False
    
    print(f"📁 分析目录: {source_dir}")
    print(f"   完整路径: {source_dir.absolute()}\n")
    
    # 统计文件
    files = list(source_dir.iterdir())
    images = [f for f in files if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
    videos = [f for f in files if f.suffix.lower() == '.avi']
    
    print("📊 文件统计:")
    print(f"   总文件数: {len(files)}")
    print(f"   图片文件: {len(images)}")
    print(f"   AVI视频: {len(videos)}")
    
    print("\n📷 图片文件:")
    for img in images[:5]:
        print(f"   - {img.name}")
    if len(images) > 5:
        print(f"   ... 还有 {len(images)-5} 个")
    
    print("\n🎬 AVI文件:")
    for avi in videos:
        file_size = avi.stat().st_size / (1024*1024)  # MB
        print(f"   - {avi.name} ({file_size:.1f} MB)")
    
    return True

def demo_date_detection():
    """演示日期识别功能"""
    print("\n" + "="*60)
    print("演示：日期识别")
    print("="*60 + "\n")
    
    processor = MediaProcessor('./20070922_mcm')
    
    # 显示目录名识别的日期
    dir_date = processor.get_directory_date()
    print("📅 从目录名识别:")
    print(f"   目录: {processor.source_dir.name}")
    print(f"   识别日期: {dir_date}")
    
    # 显示几个样本文件的日期识别
    source_dir = Path('./20070922_mcm')
    image_files = [f for f in source_dir.iterdir() 
                   if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
    
    print("\n📸 样本图片的日期识别:")
    for img_file in image_files[:3]:
        exif_date = processor.get_exif_datetime(img_file)
        guess_date = processor.guess_datetime_from_filename(img_file)
        
        print(f"\n   文件: {img_file.name}")
        if exif_date:
            print(f"   EXIF日期: ✓ {exif_date}")
        else:
            print("   EXIF日期: ✗ 未找到")
        
        if guess_date:
            print(f"   猜测日期: {guess_date}")
    
    print("\n🎬 AVI文件的日期识别:")
    avi_files = [f for f in source_dir.iterdir() if f.suffix.lower() == '.avi']
    for avi_file in avi_files[:2]:
        guess_date = processor.guess_datetime_from_filename(avi_file)
        print(f"\n   文件: {avi_file.name}")
        if guess_date:
            print(f"   猜测日期: {guess_date}")

def demo_output_structure():
    """演示输出目录结构"""
    print("\n" + "="*60)
    print("演示：处理后的目录结构")
    print("="*60 + "\n")
    
    processor = MediaProcessor('./20070922_mcm')
    
    print("处理前:")
    print(f"""
{processor.source_dir.name}/
├── S7300317.JPG
├── S7300318.JPG
├── ... (其他JPG文件)
├── S7300333.AVI ← 将被转码
├── S7300359.AVI ← 将被转码
└── S7300362.AVI ← 将被转码
""")
    
    print("处理后:")
    print(f"""
{processor.source_dir.name}/
├── S7300317.JPG (EXIF已更新为 2007-09-22 10:30:00)
├── S7300318.JPG (EXIF已更新为 2007-09-22 10:30:01)
├── ... (其他JPG文件，EXIF已更新)
├── S7300333.MP4 (新生成的高质量MP4) ← 转码完成
├── S7300359.MP4 (新生成的高质量MP4) ← 转码完成
└── S7300362.MP4 (新生成的高质量MP4) ← 转码完成

archive/
└── {processor.source_dir.name}/
    ├── S7300333.AVI (原始备份)
    ├── S7300359.AVI (原始备份)
    └── S7300362.AVI (原始备份)
""")
    
    print("说明:")
    print("  ✓ JPG文件保留在原位置，EXIF日期已更新")
    print("  ✓ AVI文件已移动到 archive/ 目录")
    print("  ✓ MP4文件在原目录中，替代AVI")
    print("  ✓ MP4包含日期元数据，可被媒体应用正确识别")

def main():
    """主演示函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  照片和视频处理脚本 - 功能演示".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # 演示1: 分析
    if not demo_analyze():
        print("\n❌ 无法访问演示目录")
        return 1
    
    # 演示2: 日期识别
    try:
        demo_date_detection()
    except Exception as e:
        print(f"\n⚠️  日期识别演示出错（通常是缺少依赖）: {e}")
    
    # 演示3: 输出结构
    demo_output_structure()
    
    # 总结
    print("\n" + "="*60)
    print("演示总结")
    print("="*60 + "\n")
    print("脚本将执行以下操作:")
    print("  1. 📸 读取所有JPG文件的EXIF信息")
    print("  2. 📅 对缺失EXIF的文件，从文件名猜测日期")
    print("  3. 🔄 更新JPG的EXIF日期")
    print("  4. 🎬 对每个AVI文件:")
    print("      - 创建 archive/20070922_mcm/ 目录")
    print("      - 移动AVI到该目录")
    print("      - 用ffmpeg转码为高质量MP4")
    print("      - 写入MP4创建时间元数据")
    print("\n")
    print("✅ 要实际执行处理，运行:")
    print("   python3 main.py ./20070922_mcm")
    print("\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
