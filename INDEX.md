# 📸 照片和视频处理系统 - 完整文档索引

**项目完成日期:** 2024年1月  
**Python版本:** 3.7+  
**主要依赖:** Pillow, piexif, ffmpeg  

---

## 🚀 快速开始（3步）

### 1️⃣ 安装
```bash
pip3 install -r requirements.txt
```

### 2️⃣ 验证
```bash
python3 test_env.py
```

### 3️⃣ 运行
```bash
python3 main.py ./20070922_mcm
```

---

## 📚 文档导航

### 🌟 首先阅读
| 文件 | 说明 |
|------|------|
| **QUICKSTART.md** | ⭐ **从这里开始！** 5分钟快速入门指南 |
| **PROJECT_SUMMARY.md** | 项目全面总结，功能清单和架构概览 |

### 📖 详细文档
| 文件 | 说明 |
|------|------|
| **README.md** | 完整使用说明、功能介绍、常见问题 |
| **GUIDE.md** | 技术深度文档、API参考、开发指南 |
| **INTERPOLATION.md** | ⭐ EXIF插值功能详解（重要特性） |
| **LAST_FILE_INFERENCE.md** | ⭐ 最后一个文件推断功能详解（v2.1新增） |
| **config.ini** | 配置参数说明和调优建议 |

### 💻 代码和工具
| 文件 | 说明 |
|------|------|
| **main.py** | 核心处理脚本（550+行） |
| **examples.py** | 5个实用代码示例 |
| **demo.py** | 功能演示脚本（无需修改文件） |
| **test_env.py** | 环境检查脚本 |
| **setup.sh** | 自动安装脚本（Linux/macOS） |

### 📦 配置文件
| 文件 | 说明 |
|------|------|
| **requirements.txt** | Python依赖列表 |

---

## 🎯 功能概览

### 核心功能
- ✅ **EXIF读取** - 自动读取照片拍摄日期
- ✅ **日期猜测** - 从文件名和目录名推断拍摄时间
- ✅ **视频时间推断** ⭐⭐ - 多层策略推断视频拍摄时间
  - 最后一个文件：前一个媒体文件时间+1分钟
  - 其他视频：相邻照片EXIF时间插值
- ✅ **元数据更新** - 写入照片和视频的时间信息
- ✅ **视频转码** - AVI → MP4转换（高质量）
- ✅ **文件管理** - 自动整理到archive目录

### 智能特性
- 🧠 **多层日期识别** - 最后文件检测 → EXIF插值 → 文件名 → 目录名 → 序列推断
- 🧠 **最后文件推断** ⭐ (v2.1) - 从前一个媒体文件推断，加1分钟
- 🧠 **视频时间插值** ⭐ - 使用线性插值从前后照片的EXIF时间推断视频时间
- 🔄 **自动降级** - 上级方法失败自动尝试备选方案
- 📝 **详细日志** - 清晰的进度输出和错误报告
- 🛡️ **安全操作** - 文件移动而非删除，完整备份

---

## 📊 文件结构

```
camera_/
├── main.py                 # 核心脚本 ⭐
├── examples.py             # 代码示例
├── demo.py                 # 演示脚本
├── test_env.py             # 环境检查
├── setup.sh                # 快速安装
│
├── QUICKSTART.md           # 快速开始 ⭐⭐
├── PROJECT_SUMMARY.md      # 项目总结 ⭐
├── README.md               # 详细说明
├── GUIDE.md                # 技术文档
├── INDEX.md                # 本文件
│
├── requirements.txt        # 依赖列表
├── config.ini              # 配置文件
│
└── 20070922_mcm/           # 示例数据目录
    ├── S7300317.JPG
    ├── ... (其他文件)
    └── S7300333.AVI
```

---

## 🔄 处理流程

```
输入：20070922_mcm/ (包含JPG和AVI)
  ↓
[MediaProcessor] 处理器
  ├─→ 图片处理
  │   ├─ 读EXIF日期
  │   ├─ 猜测缺失日期
  │   └─ 更新EXIF
  │
  └─→ 视频处理
      ├─ 创建archive目录
      ├─ 移动AVI文件
      ├─ ffmpeg转码MP4
      └─ 写入时间戳
  ↓
输出：
  ├─ 20070922_mcm/ (图片已更新，MP4新生成)
  └─ archive/20070922_mcm/ (原始AVI备份)
```

---

## 🎓 学习路线

### 初学者
1. 阅读 **QUICKSTART.md** (5分钟)
2. 运行 `python3 test_env.py` (验证环境)
3. 运行 `python3 demo.py` (查看演示)
4. 运行 `python3 main.py ./20070922_mcm` (实际处理)

### 开发者
1. 了解 `main.py` 中的 `MediaProcessor` 类
2. 查看 **GUIDE.md** 中的 API 参考
3. 运行 `python3 examples.py <number>` (查看代码示例)
4. 编辑 `main.py` 自定义功能

### 高级用户
1. 学习 **GUIDE.md** 中的技术细节
2. 修改 `config.ini` 调整参数
3. 在 `guess_datetime_from_filename()` 中添加新的日期识别模式
4. 扩展支持的媒体格式

---

## 📋 常见任务

### 处理单个目录
```bash
python3 main.py ./20070922_mcm
```

### 处理多个目录
```bash
python3 main.py ./20070922_mcm ./20070923_mcm ./20070924_mcm
```

### 查看演示（不修改文件）
```bash
python3 demo.py
```

### 验证环境
```bash
python3 test_env.py
```

### 调整转码质量
编辑 `config.ini`:
```ini
FFMPEG_CRF = "18"  # 18=高, 23=中, 28=低
```

### 添加新的日期识别模式
编辑 `main.py` 中的 `guess_datetime_from_filename()` 方法

---

## 🔧 配置参数

### 转码设置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| VIDEO_CODEC | libx264 | 视频编码器 |
| FFMPEG_PRESET | medium | 转码速度(fast/medium/slow) |
| FFMPEG_CRF | 18 | 质量(0=高,51=低) |
| AUDIO_CODEC | aac | 音频编码器 |
| AUDIO_QUALITY | 9 | 音频质量(0=高,9=低) |

### 功能开关
| 参数 | 默认值 | 说明 |
|------|--------|------|
| UPDATE_IMAGE_EXIF | True | 是否更新图片EXIF |
| UPDATE_VIDEO_METADATA | True | 是否更新视频元数据 |

---

## ❓ 常见问题

### Q: 需要多长时间处理？
**A:** 照片处理很快（毫秒级），视频转码较慢（可能10-30分钟）。

### Q: 会删除原始文件吗？
**A:** 不会。AVI被移动到archive/，图片保留原位置。

### Q: 支持哪些格式？
**A:** 图片：JPG, PNG, BMP, GIF, TIFF | 视频：AVI, MP4, MOV, MKV

### Q: 如何停止处理？
**A:** 按 Ctrl+C。已处理的文件保持不变。

### Q: 可以处理HEIC/iPhone照片吗？
**A:** 目前不支持。可以手动添加支持，见GUIDE.md。

---

## 🚨 故障排除

### ffmpeg未找到
```bash
# 安装ffmpeg
sudo apt-get install ffmpeg      # Ubuntu/Debian
brew install ffmpeg              # macOS
```

### PIL/piexif导入错误
```bash
pip3 install -r requirements.txt
```

### 权限拒绝
```bash
chmod -R u+rw ./20070922_mcm
```

### 视频转码失败
- 检查ffmpeg是否安装: `ffmpeg -version`
- 检查磁盘空间是否充足
- 查看详细错误日志

更多问题见 **README.md** 的故障排除部分。

---

## 📞 获取帮助

| 问题类型 | 查看文件 |
|---------|---------|
| 快速开始 | QUICKSTART.md |
| 使用说明 | README.md |
| 技术细节 | GUIDE.md |
| 代码示例 | examples.py |
| 功能演示 | demo.py |
| 环境问题 | test_env.py 的输出 |

---

## 🎉 准备好了吗？

1. **立即开始**: 阅读 **QUICKSTART.md**
2. **查看演示**: `python3 demo.py`
3. **开始处理**: `python3 main.py ./20070922_mcm`

---

**祝您使用愉快！** 🚀

这个脚本将为您节省数小时的手动处理时间。
