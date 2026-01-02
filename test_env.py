#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证环境和依赖
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低 (需要3.7+，当前{version.major}.{version.minor})")
        return False

def check_ffmpeg():
    """检查ffmpeg"""
    print("检查ffmpeg...", end=" ")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              check=True,
                              timeout=5)
        version_line = result.stdout.decode('utf-8').split('\n')[0]
        print(f"✓ {version_line}")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("✗ ffmpeg未安装或无法访问")
        print("  安装ffmpeg:")
        print("    Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("    macOS: brew install ffmpeg")
        return False

def check_python_packages():
    """检查Python包"""
    packages = ['PIL', 'piexif']
    all_ok = True
    
    for package in packages:
        print(f"检查{package}...", end=" ")
        try:
            __import__(package)
            print("✓")
        except ImportError:
            print("✗ 未安装")
            all_ok = False
    
    return all_ok

def check_main_script():
    """检查主脚本"""
    print("检查main.py...", end=" ")
    main_path = Path(__file__).parent / 'main.py'
    if main_path.exists():
        print("✓")
        return True
    else:
        print("✗ 文件不存在")
        return False

def check_sample_directory():
    """检查示例目录"""
    print("检查示例目录...", end=" ")
    sample_dir = Path(__file__).parent / '20070922_mcm'
    if sample_dir.exists() and sample_dir.is_dir():
        files = list(sample_dir.iterdir())
        print(f"✓ ({len(files)}个文件)")
        return True
    else:
        print("✗ 不存在或不是目录")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*50)
    print("照片和视频处理脚本 - 环境检查")
    print("="*50 + "\n")
    
    results = []
    
    # 运行检查
    results.append(("Python版本", check_python_version()))
    results.append(("ffmpeg", check_ffmpeg()))
    results.append(("Python包", check_python_packages()))
    results.append(("主脚本", check_main_script()))
    results.append(("示例目录", check_sample_directory()))
    
    # 总结
    print("\n" + "="*50)
    print("检查结果总结:")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20} {status}")
    
    print("\n" + "="*50)
    
    if passed == total:
        print(f"✓ 所有检查通过 ({passed}/{total})")
        print("\n可以开始使用脚本了！")
        print("运行: python3 main.py ./20070922_mcm")
        return 0
    else:
        print(f"✗ 有 {total - passed} 项检查失败")
        print("\n请解决上述问题后再运行脚本")
        print("\n安装缺失的包:")
        print("  pip3 install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
