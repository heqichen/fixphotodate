# 3GP 和 AMR 文件处理实现细节

## 概述

v3.0 版本添加了对 3GP 视频文件和 AMR 音频文件的支持。两种格式都遵循与现有 AVI 处理相同的工作流程，但针对各自的特性进行了优化。

---

## 1. 3GP 视频文件处理

### 1.1 3GP 格式背景

**3GP (3GPP Multimedia File)** 是一种多媒体容器格式，主要用于手机（特别是 3G 手机）的视频录制。

**特点：**
- 文件扩展名：`.3gp`
- 典型视频编码：MPEG-4 Part 2, H.263, H.264
- 典型音频编码：AMR, AAC
- 尺寸：通常较小（为了节省手机存储空间）
- 兼容性：现代设备兼容性有限

### 1.2 处理流程

```
3GP 文件处理流程：

VID_002.3gp (原始位置)
    ↓
[1] 移动到 archive 备份
    archive/VID_002.3gp
    ↓
[2] 使用 ffmpeg 转换
    ffmpeg -i archive/VID_002.3gp \
           -c:v libx264 -crf 18 \
           -c:a aac -q:a 9 \
           VID_002.mp4
    ↓
[3] 推断时间戳
    • 优先：最后文件 + 1分钟
    • 次选：相邻照片 EXIF 插值
    • 备选：文件名、目录名等
    ↓
[4] 写入 MP4 元数据
    ffmpeg -i VID_002.mp4 \
           -metadata creation_time=YYYY-MM-DDTHH:MM:SS \
           VID_002_temp.mp4
    ↓
VID_002.mp4 (最终输出，含时间戳)
```

### 1.3 代码实现

#### `process_3gp()` 方法

```python
def process_3gp(self, threeGp_path: Path):
    """
    处理 3GP 文件（与 AVI 相同的操作）
    """
    logger.info(f"处理3GP: {threeGp_path.name}")
    
    # 创建归档目录
    self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 移动 3GP 文件到归档目录
    archive_3gp_path = self.archive_dir / threeGp_path.name
    shutil.move(str(threeGp_path), str(archive_3gp_path))
    logger.info(f"  已移动到: {archive_3gp_path}")
    
    # 生成 MP4 文件
    mp4_name = threeGp_path.stem + '.mp4'
    mp4_path = self.source_dir / mp4_name
    
    if self.convert_3gp_to_mp4(archive_3gp_path, mp4_path):
        logger.info(f"  已生成MP4: {mp4_path.name}")
        
        # 推断时间并写入元数据
        media_date = self.guess_datetime_from_filename(threeGp_path)
        if media_date:
            self.set_mp4_metadata(mp4_path, media_date)
            logger.info(f"  已设置MP4时间戳: {media_date}")
```

#### `convert_3gp_to_mp4()` 方法

```python
def convert_3gp_to_mp4(self, threeGp_path: Path, mp4_path: Path) -> bool:
    """
    使用 ffmpeg 将 3GP 转换为 MP4
    """
    try:
        # 验证 ffmpeg
        subprocess.run(['ffmpeg', '-version'], 
                     capture_output=True, 
                     check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("ffmpeg未安装，无法转换视频")
        return False
    
    try:
        cmd = [
            'ffmpeg',
            '-i', str(threeGp_path),
            '-c:v', 'libx264',      # H.264 视频编码
            '-preset', 'medium',     # 平衡速度和质量
            '-crf', '18',            # 18 = 高质量 (0-51)
            '-c:a', 'aac',           # AAC 音频编码
            '-q:a', '9',             # 最高音频质量
            '-y',                    # 覆盖输出
            str(mp4_path)
        ]
        
        logger.info(f"  转换中: {threeGp_path.name} -> {mp4_path.name}")
        subprocess.run(cmd, check=True, 
                     capture_output=True,
                     timeout=3600)  # 1小时超时
        
        return mp4_path.exists()
    except subprocess.TimeoutExpired:
        logger.error(f"转换超时: {threeGp_path.name}")
        return False
    except Exception as e:
        logger.error(f"转换失败: {e}")
        return False
```

### 1.4 ffmpeg 参数详解

| 参数 | 值 | 说明 |
|------|-----|------|
| `-c:v` | `libx264` | H.264 视频编码器（高压缩、广泛兼容） |
| `-preset` | `medium` | 编码速度预设（fast/medium/slow） |
| `-crf` | `18` | 质量参数（0=最高, 51=最低, 18=很高质量） |
| `-c:a` | `aac` | AAC 音频编码器（MP4 标准） |
| `-q:a` | `9` | 音频质量（0-9, 9=最高） |
| `-y` | - | 自动覆盖输出文件 |
| `timeout` | `3600` | 转换超时时间（秒） |

### 1.5 质量考虑

**选择 H.264 和 CRF=18 的原因：**
- **兼容性**：H.264 是最广泛支持的视频编码
- **质量**：CRF 18 提供高质量，与原始 3GP 相当
- **大小**：相对原始文件，MP4 通常更小（3GP 本身已压缩）
- **速度**：medium 预设在速度和质量间平衡

**性能估计：**
- 100MB 的 3GP 文件 → 约 2-5 分钟转换时间（取决于硬件）

---

## 2. AMR 音频文件处理

### 2.1 AMR 格式背景

**AMR (Adaptive Multi-Rate)** 是一种音频编码格式，主要用于手机语音通话和录音。

**特点：**
- 文件扩展名：`.amr`（单声道）或 `.awb`（宽带）
- 编码方式：AMR-NB (8kHz) 或 AMR-WB (16kHz)
- 码率：4.75-12.2 kbps (NB) 或 6.60-23.85 kbps (WB)
- 主要用途：语音录音、通话记录
- 文件大小：非常小（高压缩比）
- 兼容性：现代播放器支持有限

### 2.2 处理流程

```
AMR 文件处理流程：

AUD_004.amr (原始位置)
    ↓
[1] 移动到 archive 备份
    archive/AUD_004.amr
    ↓
[2] 使用 ffmpeg 转换
    ffmpeg -i archive/AUD_004.amr \
           -c:a libmp3lame \
           -q:a 4 \
           AUD_004.mp3
    ↓
[3] 推断时间戳
    • 优先：最后文件 + 1分钟
    • 次选：相邻文件推断
    • 备选：文件名、目录名等
    ↓
[4] 写入 MP3 元数据
    ffmpeg -i AUD_004.mp3 \
           -metadata creation_time=YYYY-MM-DDTHH:MM:SS \
           AUD_004_temp.mp3
    ↓
AUD_004.mp3 (最终输出，含时间戳)
```

### 2.3 代码实现

#### `process_amr()` 方法

```python
def process_amr(self, amr_path: Path):
    """
    处理 AMR 文件：转换为 MP3 并猜测时间戳，存档备份
    """
    logger.info(f"处理AMR: {amr_path.name}")
    
    # 创建归档目录
    self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 移动 AMR 文件到归档目录备份
    archive_amr_path = self.archive_dir / amr_path.name
    shutil.move(str(amr_path), str(archive_amr_path))
    logger.info(f"  已移动到: {archive_amr_path}")
    
    # 生成 MP3 文件
    mp3_name = amr_path.stem + '.mp3'
    mp3_path = self.source_dir / mp3_name
    
    if self.convert_amr_to_mp3(archive_amr_path, mp3_path):
        logger.info(f"  已生成MP3: {mp3_path.name}")
        
        # 推断时间并写入元数据
        media_date = self.guess_datetime_from_filename(amr_path)
        if media_date:
            self.set_mp3_metadata(mp3_path, media_date)
            logger.info(f"  已设置MP3时间戳: {media_date}")
```

#### `convert_amr_to_mp3()` 方法

```python
def convert_amr_to_mp3(self, amr_path: Path, mp3_path: Path) -> bool:
    """
    使用 ffmpeg 将 AMR 转换为 MP3
    """
    try:
        # 验证 ffmpeg
        subprocess.run(['ffmpeg', '-version'], 
                     capture_output=True, 
                     check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("ffmpeg未安装，无法转换音频")
        return False
    
    try:
        cmd = [
            'ffmpeg',
            '-i', str(amr_path),
            '-c:a', 'libmp3lame',   # LAME MP3 编码器
            '-q:a', '4',            # 4 = 高质量 (0-9)
            '-y',                   # 覆盖输出
            str(mp3_path)
        ]
        
        logger.info(f"  转换中: {amr_path.name} -> {mp3_path.name}")
        subprocess.run(cmd, check=True, 
                     capture_output=True,
                     timeout=1800)  # 30分钟超时
        
        return mp3_path.exists()
    except subprocess.TimeoutExpired:
        logger.error(f"转换超时: {amr_path.name}")
        return False
    except Exception as e:
        logger.error(f"转换失败: {e}")
        return False
```

#### `set_mp3_metadata()` 方法

```python
def set_mp3_metadata(self, mp3_path: Path, dt: datetime):
    """
    使用 ffmpeg 设置 MP3 文件的创建时间元数据
    """
    try:
        # 创建临时文件
        temp_mp3 = mp3_path.parent / (mp3_path.stem + '_temp.mp3')
        
        # 格式化时间戳
        timestamp = dt.isoformat()
        
        cmd = [
            'ffmpeg',
            '-i', str(mp3_path),
            '-c', 'copy',                              # 无重新编码
            '-metadata', f'creation_time={timestamp}', # 写入时间戳
            '-y',
            str(temp_mp3)
        ]
        
        subprocess.run(cmd, check=True,
                     capture_output=True,
                     timeout=600)
        
        # 替换原文件
        shutil.move(str(temp_mp3), str(mp3_path))
        logger.debug(f"MP3元数据已更新: {mp3_path.name}")
    except Exception as e:
        logger.warning(f"设置MP3元数据失败: {e}")
```

### 2.4 ffmpeg 参数详解

| 参数 | 值 | 说明 |
|------|-----|------|
| `-c:a` | `libmp3lame` | LAME MP3 编码器（开源、高质量） |
| `-q:a` | `4` | VBR 质量参数（0=最高, 9=最低, 4=高质量） |
| `-y` | - | 自动覆盖输出文件 |
| `timeout` | `1800` | 转换超时时间（秒，通常音频更快） |

### 2.5 质量考虑

**选择 MP3 和 Q=4 的原因：**
- **兼容性**：MP3 是最广泛支持的音频格式
- **质量**：Q=4 (VBR) 提供与原始 AMR 相近的质量
- **大小**：MP3 通常与 AMR 文件大小相近或更小
- **可读性**：MP3 元数据支持更好
- **速度**：音频转换很快（通常 < 1 秒）

**码率对比：**
```
AMR-NB: 4.75-12.2 kbps (非常小，语音清晰但有失真)
MP3 Q=4: ~128 kbps (相对高质量)

关键：由于 AMR 本身就是为语音优化，MP3 转换后质量会提高
```

**性能估计：**
- 1MB 的 AMR 文件 → 约 1-2 秒转换时间

---

## 3. 时间推断的扩展

### 3.1 更新的 `guess_datetime_from_filename()` 方法

现在支持对 3GP 和 AMR 文件的时间推断：

```python
# 对于 3GP 和 AMR：
if file_path.suffix.lower() in {'.avi', '.3gp', '.amr'}:
    # 尝试最后文件检测
    last_file_date = self._get_datetime_from_last_file(file_path)
    if last_file_date:
        return last_file_date
    
    # 仅 3GP 支持插值（音频无法插值）
    if file_path.suffix.lower() in {'.avi', '.3gp'}:
        interpolated_date = self._interpolate_datetime_from_neighbors(file_path)
        if interpolated_date:
            return interpolated_date
```

### 3.2 更新的 `_get_datetime_from_last_file()` 方法

现在考虑音频文件：

```python
# 扫描所有媒体文件（包括音频）
for f in all_files:
    suffix = f.suffix.lower()
    if suffix in self.IMAGE_EXTENSIONS or \
       suffix in self.VIDEO_EXTENSIONS or \
       suffix in self.AUDIO_EXTENSIONS:  # ← 新增
        num_match = re.search(r'(\d+)', f.stem)
        if num_match:
            num = int(num_match.group(1))
            media_files[num] = f
```

### 3.3 时间推断优先级（更新）

```
对于 3GP：
  Level 1: 最后文件检测（前一个媒体：照片/视频/音频 + 1分钟）
  Level 2: EXIF 插值（从相邻照片）
  Level 3: 文件名模式
  Level 4: 文件序号推导
  Level 5: 目录名解析

对于 AMR：
  Level 1: 最后文件检测（前一个媒体：照片/视频/音频 + 1分钟）
  Level 2: 文件名模式（无法插值，因为音频无 EXIF）
  Level 3: 文件序号推导
  Level 4: 目录名解析
```

---

## 4. 扩展的媒体文件类型识别

### 4.1 新增的扩展类别

```python
# v2.1
VIDEO_EXTENSIONS = {'.avi', '.mp4', '.mov', '.mkv', '.flv', '.wmv'}

# v3.0
VIDEO_EXTENSIONS = {'.avi', '.mp4', '.mov', '.mkv', '.flv', '.wmv', '.3gp'}
AUDIO_EXTENSIONS = {'.amr', '.mp3', '.wav', '.aac', '.flac'}
```

### 4.2 处理流程顺序

在 `process_all()` 中的处理顺序：

```python
1. 图片文件（.jpg, .jpeg, .png, .bmp, .gif, .tiff）
   └─ 读取 EXIF，推断时间，更新 EXIF

2. AVI 文件（.avi）
   └─ 备份 → 转换为 MP4 → 推断时间 → 写元数据

3. 3GP 文件（.3gp）← v3.0 新增
   └─ 备份 → 转换为 MP4 → 推断时间 → 写元数据

4. AMR 文件（.amr）← v3.0 新增
   └─ 备份 → 转换为 MP3 → 推断时间 → 写元数据

其他视频文件（.mp4, .mov, etc.）
   └─ 不处理（保留原状）

其他音频文件（.mp3, .wav, etc.）
   └─ 不处理（保留原状）
```

---

## 5. 与 AVI 处理的相似性和差异

### 5.1 相似性

| 方面 | AVI | 3GP |
|------|-----|-----|
| 处理流程 | 备份 → 转换 → 推断 → 元数据 | 备份 → 转换 → 推断 → 元数据 |
| 转换格式 | MP4 | MP4 |
| 时间推断 | 支持插值和最后文件 | 支持插值和最后文件 |
| 元数据写入 | MP4 元数据 | MP4 元数据 |
| 超时时间 | 3600 秒 | 3600 秒 |

### 5.2 差异

| 方面 | AVI | 3GP | AMR |
|------|-----|-----|-----|
| 文件大小 | 中等 | 小 | 极小 |
| 转换时间 | 中等 | 中等 | 快速 |
| 输出格式 | MP4 (视频) | MP4 (视频) | MP3 (音频) |
| 时间推断支持 | 完全 | 完全 | 部分 |
| 插值支持 | ✓ | ✓ | ✗ |
| 转换超时 | 3600s | 3600s | 1800s |

---

## 6. 归档目录结构

处理前后的文件结构对比：

**处理前：**
```
source_dir/
├─ IMG_001.jpg
├─ IMG_002.jpg
├─ VID_003.avi
├─ VID_004.3gp          ← 新格式
├─ AUD_005.amr          ← 新格式
└─ IMG_006.jpg
```

**处理后：**
```
source_dir/
├─ IMG_001.jpg          ← 保持不变（EXIF 已更新）
├─ IMG_002.jpg          ← 保持不变（EXIF 已更新）
├─ VID_003.mp4          ← 从 AVI 转换（含时间戳）
├─ VID_004.mp4          ← 从 3GP 转换（含时间戳）← v3.0
├─ AUD_005.mp3          ← 从 AMR 转换（含时间戳）← v3.0
├─ IMG_006.jpg          ← 保持不变（EXIF 已更新）
└─ archive/source_dir/
   ├─ VID_003.avi       ← 备份
   ├─ VID_004.3gp       ← 备份（v3.0 新增）
   └─ AUD_005.amr       ← 备份（v3.0 新增）
```

---

## 7. 错误处理和恢复策略

### 7.1 转换失败恢复

```python
# 如果转换失败，原始文件已在 archive/ 目录
try:
    if self.convert_3gp_to_mp4(archive_3gp_path, mp4_path):
        # 成功
        logger.info(f"已生成MP4: {mp4_path.name}")
    else:
        # 失败：文件在 archive/，可以稍后重新转换
        logger.error(f"转换失败: {threeGp_path.name}")
        # 原始 3GP 文件保存在 archive/ 中
except Exception as e:
    logger.error(f"处理 3GP 失败: {e}")
    # 原始 3GP 文件保存在 archive/ 中
```

### 7.2 时间推断失败恢复

```python
media_date = self.guess_datetime_from_filename(threeGp_path)
if media_date:
    self.set_mp4_metadata(mp4_path, media_date)
    logger.info(f"已设置MP4时间戳: {media_date}")
else:
    # 失败：MP4 文件仍然有效，只是没有时间戳元数据
    logger.warning(f"无法推断 {threeGp_path.name} 的时间戳")
    # MP4 文件可以手动编辑元数据
```

### 7.3 元数据写入失败恢复

```python
try:
    # 写入元数据（使用临时文件）
    subprocess.run(cmd, check=True, ...)
    shutil.move(str(temp_mp4), str(mp4_path))
except Exception as e:
    logger.warning(f"设置MP4元数据失败: {e}")
    # 不中断处理：MP4 文件仍然有效
```

---

## 8. 性能和资源考虑

### 8.1 CPU 使用率

| 操作 | CPU 使用率 | 说明 |
|------|-----------|------|
| 3GP → MP4 转换 | 高 (100%) | H.264 编码需要大量计算 |
| AMR → MP3 转换 | 中 (50%) | MP3 编码相对轻量 |
| 元数据写入 | 低 (10%) | 只是复制数据 |

### 8.2 磁盘空间需求

对于 100MB 的 3GP 文件：
```
原始 3GP：        100 MB
→ 转换后 MP4：     50-80 MB（H.264 压缩）
→ Archive 备份：   100 MB
总需要：          250-280 MB 磁盘空间
```

对于 10MB 的 AMR 文件：
```
原始 AMR：        10 MB
→ 转换后 MP3：     8-12 MB（取决于音频长度）
→ Archive 备份：   10 MB
总需要：          28-32 MB 磁盘空间
```

### 8.3 转换时间估计

| 文件大小 | 3GP → MP4 | AMR → MP3 |
|---------|-----------|----------|
| 10 MB | 10-20 秒 | < 1 秒 |
| 100 MB | 2-5 分钟 | 2-3 秒 |
| 1 GB | 20-50 分钟 | 20-30 秒 |

（估计值基于现代硬件，实际时间取决于 CPU、磁盘速度等）

---

## 总结

v3.0 版本通过添加 3GP 和 AMR 支持，扩展了脚本的适用范围，特别是对于来自旧型手机的多媒体文件。两种格式都遵循一致的处理流程：

1. **备份**：原始文件移动到 archive/
2. **转换**：使用 ffmpeg 转换为更兼容的格式
3. **推断**：使用 5 层级联系统推断时间戳
4. **元数据**：写入创建时间到输出文件

这个设计保证了：
- **数据安全**：原始文件总是被备份
- **智能推断**：多种方法确保尽可能推断出正确时间
- **广泛兼容**：输出格式（MP4/MP3）在现代设备上广泛支持
- **向后兼容**：不影响现有的照片和 AVI 处理

