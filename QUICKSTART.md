# 快速开始指南

## 5分钟快速上手

### 步骤1：安装依赖（第一次使用）

```bash
# 安装Python包
pip3 install -r requirements.txt

# 安装ffmpeg（如果还未安装）
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg
```

### 步骤2：验证环境

```bash
python3 test_env.py
```

输出应该显示所有项都✓通过。

### 步骤3：处理文件

```bash
python3 main.py ./20070922_mcm
```

### 步骤4：查看结果

处理完成后，您会看到：

```
20070922_mcm/
  ├── S7300317.JPG (EXIF已更新)
  ├── S7300333.MP4 (新转码视频 ← 从AVI生成)
  └── ... 其他文件

archive/
  └── 20070922_mcm/
      ├── S7300333.AVI (原始AVI已备份)
      └── ... 其他AVI文件
```

## 处理多个目录

```bash
python3 main.py ./20070922_mcm ./20070923_mcm ./20070924_mcm
```

## 脚本做了什么？

✓ **照片**：读取EXIF日期，如无则猜测并更新  
✓ **视频**：AVI → MP4转码，移动原文件到archive/，设置时间戳  
✓ **日志**：详细输出处理过程  

## 常见问题

**Q: 需要多久？**  
A: 取决于文件大小。照片处理很快（毫秒级），视频转码最耗时（可能需要10-30分钟）。

**Q: 原始文件会被删除吗？**  
A: 不会。AVI被移动到archive/目录备份，图片保留在原位置。

**Q: 如何停止？**  
A: 按 Ctrl+C 中断。已处理的文件保持不变。

**Q: 可以更改转码质量吗？**  
A: 可以。编辑 `config.ini` 修改 `FFMPEG_CRF` 值：
- CRF=18：高质量（推荐）
- CRF=23：平衡（默认）
- CRF=28：低质量但文件更小

## 下一步

- 查看 `README.md` 获取详细说明
- 查看 `GUIDE.md` 了解技术细节
- 运行 `python3 examples.py <number>` 查看代码示例

---

**需要帮助？** 检查日志输出中的错误信息，通常会指示问题所在。
