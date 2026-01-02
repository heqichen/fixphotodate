# 照片和视频处理脚本

这个脚本用于处理数码相机拍摄的照片和视频文件。

## 功能

1. **读取照片EXIF数据** - 从照片中提取拍摄日期
2. **猜测缺失日期** - 如果照片没有EXIF数据，从文件名和目录名猜测拍摄时间
3. **更新照片元数据** - 将猜测的日期写入照片的EXIF信息
4. **处理AVI视频** - 将AVI文件移动到 `archive/` 目录
5. **视频转码** - 使用ffmpeg将AVI转换为MP4（保持高质量）
6. **智能视频时间推断** ⭐ - 多层策略推断视频拍摄时间：
   - 对于最后一个视频：从前一个媒体文件时间+1分钟
   - 其他视频：通过相邻照片的EXIF时间插值
7. **设置视频元数据** - 将推断的时间写入MP4文件的创建时间

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
从 https://ffmpeg.org/download.html 下载或使用包管理器

## 使用

### 基本用法

```bash
python main.py <目录路径>
```

### 示例

```bash
# 处理单个目录
python main.py ./20070922_mcm

# 处理多个目录
python main.py ./20070922_mcm ./20070923_mcm ./20070924_mcm
```

## 目录结构

处理前：
```
20070922_mcm/
  ├── S7300317.JPG
  ├── S7300318.JPG
  └── S7300333.AVI
```

处理后：
```
20070922_mcm/
  ├── S7300317.JPG (已更新EXIF日期)
  ├── S7300318.JPG (已更新EXIF日期)
  └── S7300333.MP4 (新生成的高质量视频)

archive/
  └── 20070922_mcm/
      └── S7300333.AVI (原始AVI文件)
```

## 文件名解析规则

脚本使用以下优先级解析文件时间：

### 对于视频文件（AVI）
1. **最后一个文件检测** ⭐ - 从前一个媒体文件时间+1分钟（最精确）
2. **EXIF插值优先** ⭐ - 通过相邻照片的EXIF时间线性插值（精度秒级）
   - 示例：S7300332.JPG (14:30) → S7300333.AVI → S7300336.JPG (14:35)
   - 结果：S7300333.AVI ≈ 14:31-14:32
3. 从文件名解析日期（如 `S7300333_1430.AVI`）
4. 结合文件编号推算时间

### 对于照片文件（JPG等）
1. 从照片EXIF数据读取（最准确，精度秒级）
2. 从目录名解析日期（如 `20070922_mcm` → 2007年9月22日）
3. 结合文件编号推算时间

**详见** [`INTERPOLATION.md`](./INTERPOLATION.md) 了解视频时间推断的详细工作原理，以及 [`LAST_FILE_INFERENCE.md`](./LAST_FILE_INFERENCE.md) 了解最后一个文件的推断方法。

## 日志输出

脚本会输出详细的处理日志：

```
2024-01-02 10:30:45,123 - INFO - 处理目录: /path/to/20070922_mcm
2024-01-02 10:30:45,456 - INFO - 找到 20 个图片文件
2024-01-02 10:30:45,789 - INFO - 找到 3 个AVI文件
2024-01-02 10:30:46,012 - INFO - 处理图片: S7300317.JPG
2024-01-02 10:30:46,345 - INFO -   EXIF日期: 2007-09-22 10:30:15
...
```

## 注意事项

- **备份数据** - 处理前建议备份原始文件
- **AVI自动移动** - AVI文件会自动移动到 `archive/` 目录，原位置将被MP4替代
- **时间要求** - 视频转码可能耗时较长（取决于文件大小）
- **所需权限** - 需要对目录的读写权限
- **EXIF更新** - 某些格式（如PNG）可能不支持EXIF更新

## 故障排除

### ffmpeg未找到

确保ffmpeg已安装并在PATH中：
```bash
ffmpeg -version
```

### PIL/piexif导入错误

确保已安装依赖：
```bash
pip install -r requirements.txt
```

### 权限不足

确保对目录有读写权限：
```bash
chmod -R u+rw /path/to/directory
```

## 支持的格式

**图片格式:** JPG, JPEG, PNG, BMP, GIF, TIFF  
**视频格式:** AVI, MP4, MOV, MKV, FLV, WMV

## 许可证

MIT License
