#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
照片和视频处理脚本
功能：
1. 读取照片的EXIF拍摄日期，如果没有则猜测时间
2. 处理AVI视频文件，转换为MP4并写入元数据
"""

import sys
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL not installed, will skip EXIF reading")

try:
    import piexif
    HAS_PIEXIF = True
except ImportError:
    HAS_PIEXIF = False
    logger.warning("piexif not installed")


class MediaProcessor:
    """媒体文件处理类"""
    
    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    # 支持的视频格式
    VIDEO_EXTENSIONS = {'.avi', '.mp4', '.mov', '.mkv', '.flv', '.wmv', '.3gp'}
    # 支持的音频格式
    AUDIO_EXTENSIONS = {'.amr', '.mp3', '.wav', '.aac', '.flac'}
    
    def __init__(self, source_dir: str):
        """
        初始化处理器
        
        Args:
            source_dir: 源目录路径
        """
        self.source_dir = Path(source_dir)
        self.archive_dir = self.source_dir.parent / 'archive' / self.source_dir.name
        
        if not self.source_dir.exists():
            raise ValueError(f"源目录不存在: {self.source_dir}")
        
        logger.info(f"处理目录: {self.source_dir}")
        logger.info(f"归档目录: {self.archive_dir}")
    
    def process_all(self):
        """处理目录中的所有文件"""
        logger.info("开始处理媒体文件...")
        
        files = list(self.source_dir.iterdir())
        
        # 处理图片
        image_files = [f for f in files if f.suffix.lower() in self.IMAGE_EXTENSIONS]
        logger.info(f"找到 {len(image_files)} 个图片文件")
        for image_file in image_files:
            self.process_image(image_file)
        
        # 处理AVI文件
        avi_files = [f for f in files if f.suffix.lower() == '.avi']
        logger.info(f"找到 {len(avi_files)} 个AVI文件")
        for avi_file in avi_files:
            self.process_avi(avi_file)
        
        # 处理3GP文件
        threeGp_files = [f for f in files if f.suffix.lower() == '.3gp']
        logger.info(f"找到 {len(threeGp_files)} 个3GP文件")
        for threeGp_file in threeGp_files:
            self.process_3gp(threeGp_file)
        
        # 处理AMR文件
        amr_files = [f for f in files if f.suffix.lower() == '.amr']
        logger.info(f"找到 {len(amr_files)} 个AMR文件")
        for amr_file in amr_files:
            self.process_amr(amr_file)
        
        logger.info("处理完成！")
    
    def process_image(self, image_path: Path):
        """
        处理图片文件
        
        Args:
            image_path: 图片路径
        """
        logger.info(f"处理图片: {image_path.name}")
        
        # 尝试读取EXIF日期
        exif_date = self.get_exif_datetime(image_path)
        
        if exif_date:
            logger.info(f"  EXIF日期: {exif_date}")
        else:
            # 猜测时间
            exif_date = self.guess_datetime_from_filename(image_path)
            logger.info(f"  猜测日期: {exif_date}")
            
            # 如果成功猜测或读取，更新图片EXIF
            if exif_date:
                self.set_exif_datetime(image_path, exif_date)
                logger.info("  已更新图片日期")
    
    def process_avi(self, avi_path: Path):
        """
        处理AVI文件
        
        Args:
            avi_path: AVI文件路径
        """
        logger.info(f"处理AVI: {avi_path.name}")
        
        # 创建归档目录
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动AVI文件到归档目录
        archive_avi_path = self.archive_dir / avi_path.name
        shutil.move(str(avi_path), str(archive_avi_path))
        logger.info(f"  已移动到: {archive_avi_path}")
        
        # 生成MP4文件
        mp4_name = avi_path.stem + '.mp4'
        mp4_path = self.source_dir / mp4_name
        
        if self.convert_avi_to_mp4(archive_avi_path, mp4_path):
            logger.info(f"  已生成MP4: {mp4_path.name}")
            
            # 从文件名猜测创建时间并写入MP4元数据
            media_date = self.guess_datetime_from_filename(avi_path)
            if media_date:
                self.set_mp4_metadata(mp4_path, media_date)
                logger.info(f"  已设置MP4时间戳: {media_date}")
    
    def process_3gp(self, threeGp_path: Path):
        """
        处理3GP文件（与AVI相同的操作）
        
        Args:
            threeGp_path: 3GP文件路径
        """
        logger.info(f"处理3GP: {threeGp_path.name}")
        
        # 创建归档目录
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动3GP文件到归档目录
        archive_3gp_path = self.archive_dir / threeGp_path.name
        shutil.move(str(threeGp_path), str(archive_3gp_path))
        logger.info(f"  已移动到: {archive_3gp_path}")
        
        # 生成MP4文件
        mp4_name = threeGp_path.stem + '.mp4'
        mp4_path = self.source_dir / mp4_name
        
        if self.convert_3gp_to_mp4(archive_3gp_path, mp4_path):
            logger.info(f"  已生成MP4: {mp4_path.name}")
            
            # 从文件名猜测创建时间并写入MP4元数据
            media_date = self.guess_datetime_from_filename(threeGp_path)
            if media_date:
                self.set_mp4_metadata(mp4_path, media_date)
                logger.info(f"  已设置MP4时间戳: {media_date}")
    
    def process_amr(self, amr_path: Path):
        """
        处理AMR文件：转换为MP3并猜测时间戳，存档备份
        
        Args:
            amr_path: AMR文件路径
        """
        logger.info(f"处理AMR: {amr_path.name}")
        
        # 创建归档目录
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动AMR文件到归档目录备份
        archive_amr_path = self.archive_dir / amr_path.name
        shutil.move(str(amr_path), str(archive_amr_path))
        logger.info(f"  已移动到: {archive_amr_path}")
        
        # 生成MP3文件
        mp3_name = amr_path.stem + '.mp3'
        mp3_path = self.source_dir / mp3_name
        
        if self.convert_amr_to_mp3(archive_amr_path, mp3_path):
            logger.info(f"  已生成MP3: {mp3_path.name}")
            
            # 从文件名猜测创建时间并写入MP3元数据
            media_date = self.guess_datetime_from_filename(amr_path)
            if media_date:
                self.set_mp3_metadata(mp3_path, media_date)
                logger.info(f"  已设置MP3时间戳: {media_date}")
    
    def get_exif_datetime(self, image_path: Path) -> Optional[datetime]:
        """
        从图片EXIF读取拍摄日期
        
        Args:
            image_path: 图片路径
            
        Returns:
            datetime对象或None
        """
        try:
            # 优先使用piexif
            if HAS_PIEXIF:
                try:
                    exif_dict = piexif.load(str(image_path))
                    if 36867 in exif_dict["Exif"]:  # DateTimeOriginal
                        datetime_str = exif_dict["Exif"][36867].decode('utf-8')
                        return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                except Exception as e:
                    logger.debug(f"piexif读取失败: {e}")
            
            # 使用PIL作为备选
            if HAS_PIL:
                image = Image.open(image_path)
                exif_data = image._getexif()
                if exif_data:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        # 查找DateTimeOriginal或DateTime
                        if tag_name in ['DateTimeOriginal', 'DateTime']:
                            try:
                                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            except Exception:
                                pass
        except Exception as e:
            logger.debug(f"读取EXIF失败: {e}")
        
        return None
    
    def set_exif_datetime(self, image_path: Path, dt: datetime):
        """
        设置图片EXIF拍摄日期
        
        Args:
            image_path: 图片路径
            dt: datetime对象
        """
        if not HAS_PIEXIF:
            logger.warning(f"无法更新{image_path.name}的EXIF（需要piexif）")
            return
        
        try:
            # 读取现有EXIF数据
            try:
                exif_dict = piexif.load(str(image_path))
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}}
            
            # 更新DateTime字段
            datetime_str = dt.strftime('%Y:%m:%d %H:%M:%S')
            exif_dict["Exif"][36867] = datetime_str.encode('utf-8')  # DateTimeOriginal
            exif_dict["0th"][306] = datetime_str.encode('utf-8')      # DateTime
            
            # 写入EXIF
            exif_bytes = piexif.dump(exif_dict)
            Image.open(image_path).save(image_path, exif=exif_bytes)
            logger.debug(f"EXIF已更新: {image_path.name}")
        except Exception as e:
            logger.error(f"更新EXIF失败: {e}")
    
    def guess_datetime_from_filename(self, file_path: Path) -> Optional[datetime]:
        """
        从文件名猜测创建日期
        
        尝试多种文件名模式（优先级递减）：
        - 对于最后一个视频或音频：从前一个媒体文件时间+1分钟（最准确）
        - 通过相邻照片EXIF时间插值（最准确）
        - YYYYMMDD_HHMM
        - YYYYMMDD_HH
        - YYYYMMDD
        - 目录名YYYYMMDD
        
        Args:
            file_path: 文件路径
            
        Returns:
            datetime对象或None
        """
        # 模式0: 对于视频或音频文件，如果是最后一个文件，尝试从前一个文件时间+1分钟
        if file_path.suffix.lower() in {'.avi', '.3gp', '.amr'}:
            last_file_date = self._get_datetime_from_last_file(file_path)
            if last_file_date:
                logger.info(f"  （最后一个文件）从前一个文件推断时间: {last_file_date}")
                return last_file_date
            
            # 模式1: 对于视频文件，尝试通过相邻照片的EXIF时间插值
            if file_path.suffix.lower() in {'.avi', '.3gp'}:
                interpolated_date = self._interpolate_datetime_from_neighbors(file_path)
                if interpolated_date:
                    logger.info(f"  通过相邻照片插值得到时间: {interpolated_date}")
                    return interpolated_date
        
        # 模式2: 从目录名解析 YYYYMMDD
        dir_name = file_path.parent.name
        match = re.search(r'(\d{8})', dir_name)
        if match:
            date_str = match.group(1)
            try:
                base_date = datetime.strptime(date_str, '%Y%m%d')
                # 从文件名提取时间信息
                file_name = file_path.stem
                
                # 尝试YYYYMMDD_HHMM或_HH模式
                time_match = re.search(r'_(\d{2})(\d{2})(?:_\d+)?$', file_name)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    return base_date.replace(hour=hour, minute=minute)
                
                time_match = re.search(r'_(\d{2})(?:_\d+)?$', file_name)
                if time_match:
                    hour = int(time_match.group(1))
                    return base_date.replace(hour=hour)
                
                # 如果没有时间信息，使用基础日期加时间序列
                # 根据文件编号猜测时间
                file_num_match = re.search(r'(\d+)', file_name)
                if file_num_match:
                    file_num = int(file_num_match.group(1))
                    # 假设每个文件相隔几秒到几分钟
                    file_seq = file_num % 1000
                    minutes_offset = (file_seq % 60)
                    hours_offset = (file_seq // 60) % 24
                    return base_date.replace(hour=hours_offset, minute=minutes_offset)
                
                return base_date
            except Exception as e:
                logger.debug(f"从目录名解析日期失败: {e}")
        
        return None
    
    def _interpolate_datetime_from_neighbors(self, video_path: Path) -> Optional[datetime]:
        """
        通过相邻照片的EXIF时间插值来获取视频的创建时间
        
        假设文件编号连续，找到视频前后的照片，
        读取它们的EXIF时间，使用线性插值估算视频时间
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            插值得到的datetime对象或None
        """
        try:
            # 提取视频文件编号
            video_name = video_path.stem
            video_num_match = re.search(r'(\d+)', video_name)
            if not video_num_match:
                return None
            
            video_num = int(video_num_match.group(1))
            
            # 获取同目录所有文件
            all_files = list(video_path.parent.iterdir())
            
            # 筛选图片文件并提取编号
            image_files = {}
            for f in all_files:
                if f.suffix.lower() in self.IMAGE_EXTENSIONS:
                    num_match = re.search(r'(\d+)', f.stem)
                    if num_match:
                        num = int(num_match.group(1))
                        image_files[num] = f
            
            if not image_files:
                return None
            
            # 找到视频前后最接近的两张照片
            before_num = max([n for n in image_files.keys() if n < video_num], default=None)
            after_num = min([n for n in image_files.keys() if n > video_num], default=None)
            
            # 需要前后都有照片才能插值
            if before_num is None or after_num is None:
                logger.debug(f"无法找到{video_name}前后的照片用于插值")
                return None
            
            before_file = image_files[before_num]
            after_file = image_files[after_num]
            
            # 读取两张照片的EXIF时间
            before_date = self.get_exif_datetime(before_file)
            after_date = self.get_exif_datetime(after_file)
            
            if not before_date or not after_date:
                logger.debug(f"无法读取照片EXIF时间: {before_file.name} 或 {after_file.name}")
                return None
            
            # 线性插值计算视频时间
            # 假设前后两张照片的编号与时间成线性关系
            time_diff_seconds = (after_date - before_date).total_seconds()
            num_diff = after_num - before_num
            
            # 每个编号之间相隔的秒数
            seconds_per_num = time_diff_seconds / num_diff
            
            # 计算视频对应的时间
            video_seconds_offset = (video_num - before_num) * seconds_per_num
            interpolated_date = before_date + timedelta(seconds=video_seconds_offset)
            
            logger.debug(
                f"从 {before_file.name}({before_date}) 到 {after_file.name}({after_date}) "
                f"插值得到 {video_name} 的时间: {interpolated_date}"
            )
            
            return interpolated_date
        
        except Exception as e:
            logger.debug(f"插值计算失败: {e}")
            return None
    
    def _get_datetime_from_last_file(self, video_path: Path) -> Optional[datetime]:
        """
        对于最后一个文件，获取前一个媒体文件（照片、视频或音频）的时间，并加1分钟
        
        Args:
            video_path: 视频或音频文件路径
            
        Returns:
            推断得到的datetime对象或None
        """
        try:
            # 提取文件编号
            file_name = video_path.stem
            file_num_match = re.search(r'(\d+)', file_name)
            if not file_num_match:
                return None
            
            file_num = int(file_num_match.group(1))
            
            # 获取同目录所有媒体文件（照片、视频和音频）
            all_files = list(video_path.parent.iterdir())
            media_files = {}
            
            for f in all_files:
                suffix = f.suffix.lower()
                if suffix in self.IMAGE_EXTENSIONS or suffix in self.VIDEO_EXTENSIONS or suffix in self.AUDIO_EXTENSIONS:
                    num_match = re.search(r'(\d+)', f.stem)
                    if num_match:
                        num = int(num_match.group(1))
                        media_files[num] = f
            
            if not media_files:
                return None
            
            # 检查当前文件是否是最后一个媒体文件
            max_num = max(media_files.keys())
            if file_num != max_num:
                logger.debug(f"{file_name}不是最后一个文件（最后文件编号{max_num}），无法使用此方法")
                return None
            
            # 找前一个媒体文件（编号小于当前文件）
            before_num = max([n for n in media_files.keys() if n < file_num], default=None)
            if before_num is None:
                logger.debug(f"无法找到{file_name}前的媒体文件")
                return None
            
            before_file = media_files[before_num]
            before_date = None
            
            # 首先尝试获取照片的EXIF时间
            if before_file.suffix.lower() in self.IMAGE_EXTENSIONS:
                before_date = self.get_exif_datetime(before_file)
                if before_date:
                    logger.debug(f"从照片{before_file.name}读取EXIF时间: {before_date}")
            
            # 如果是视频或音频文件或前面的照片没有EXIF，尝试从视频/音频获取
            if not before_date and before_file.suffix.lower() in self.VIDEO_EXTENSIONS:
                # 对于视频文件，尝试使用已经处理过的时间信息
                # 这需要在处理前一个视频时记录其时间
                logger.debug(f"前一个文件{before_file.name}是视频，尝试通过插值获取")
                before_date = self._interpolate_datetime_from_neighbors(before_file)
            
            if not before_date:
                logger.debug(f"无法从前一个文件{before_file.name}获取时间")
                return None
            
            # 给前一个文件的时间加1分钟
            result_date = before_date + timedelta(minutes=1)
            logger.info(f"  从前一个文件({before_file.name}: {before_date})推断，加1分钟得到: {result_date}")
            
            return result_date
        
        except Exception as e:
            logger.debug(f"从前一个文件推断时间失败: {e}")
            return None
    
    def convert_avi_to_mp4(self, avi_path: Path, mp4_path: Path) -> bool:
        """
        使用ffmpeg将AVI转换为MP4
        
        Args:
            avi_path: AVI文件路径
            mp4_path: 输出MP4文件路径
            
        Returns:
            转换是否成功
        """
        try:
            # 检查ffmpeg是否已安装
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("ffmpeg未安装，无法转换视频")
            return False
        
        try:
            # 使用ffmpeg转换视频，保持质量
            # 使用 -q:v 1 保持高质量，或者使用特定的码率
            cmd = [
                'ffmpeg',
                '-i', str(avi_path),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',  # 质量参数，18很高，0是无损
                '-c:a', 'aac',
                '-q:a', '9',
                '-y',  # 覆盖输出文件
                str(mp4_path)
            ]
            
            logger.info(f"  转换中: {avi_path.name} -> {mp4_path.name}")
            subprocess.run(cmd, check=True, 
                         capture_output=True,
                         timeout=3600)  # 1小时超时
            
            return mp4_path.exists()
        except subprocess.TimeoutExpired:
            logger.error(f"转换超时: {avi_path.name}")
            return False
        except Exception as e:
            logger.error(f"转换失败: {e}")
            return False
    
    def convert_3gp_to_mp4(self, threeGp_path: Path, mp4_path: Path) -> bool:
        """
        使用ffmpeg将3GP转换为MP4
        
        Args:
            threeGp_path: 3GP文件路径
            mp4_path: 输出MP4文件路径
            
        Returns:
            转换是否成功
        """
        try:
            # 检查ffmpeg是否已安装
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("ffmpeg未安装，无法转换视频")
            return False
        
        try:
            # 使用ffmpeg转换3GP为MP4，保持质量
            cmd = [
                'ffmpeg',
                '-i', str(threeGp_path),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',  # 质量参数，18很高，0是无损
                '-c:a', 'aac',
                '-q:a', '9',
                '-y',  # 覆盖输出文件
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
    
    def convert_amr_to_mp3(self, amr_path: Path, mp3_path: Path) -> bool:
        """
        使用ffmpeg将AMR转换为MP3
        
        Args:
            amr_path: AMR文件路径
            mp3_path: 输出MP3文件路径
            
        Returns:
            转换是否成功
        """
        try:
            # 检查ffmpeg是否已安装
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("ffmpeg未安装，无法转换音频")
            return False
        
        try:
            # 使用ffmpeg转换AMR为MP3
            cmd = [
                'ffmpeg',
                '-i', str(amr_path),
                '-c:a', 'libmp3lame',
                '-q:a', '4',  # MP3质量参数，4是高质量
                '-y',  # 覆盖输出文件
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
    
    def set_mp4_metadata(self, mp4_path: Path, dt: datetime):
        """
        使用ffmpeg设置MP4文件的创建时间元数据
        
        Args:
            mp4_path: MP4文件路径
            dt: datetime对象
        """
        try:
            # 先检查ffmpeg是否支持元数据修改
            # 创建临时文件
            temp_mp4 = mp4_path.parent / (mp4_path.stem + '_temp.mp4')
            
            # 格式化时间戳为ISO 8601格式
            timestamp = dt.isoformat()
            
            cmd = [
                'ffmpeg',
                '-i', str(mp4_path),
                '-c', 'copy',
                '-metadata', f'creation_time={timestamp}',
                '-y',
                str(temp_mp4)
            ]
            
            subprocess.run(cmd, check=True,
                         capture_output=True,
                         timeout=600)
            
            # 用临时文件替换原文件
            shutil.move(str(temp_mp4), str(mp4_path))
            logger.debug(f"MP4元数据已更新: {mp4_path.name}")
        except Exception as e:
            logger.warning(f"设置MP4元数据失败: {e}")
            # 不中断处理流程
    
    def set_mp3_metadata(self, mp3_path: Path, dt: datetime):
        """
        使用ffmpeg设置MP3文件的创建时间元数据
        
        Args:
            mp3_path: MP3文件路径
            dt: datetime对象
        """
        try:
            # 创建临时文件
            temp_mp3 = mp3_path.parent / (mp3_path.stem + '_temp.mp3')
            
            # 格式化时间戳为ISO 8601格式
            timestamp = dt.isoformat()
            
            cmd = [
                'ffmpeg',
                '-i', str(mp3_path),
                '-c', 'copy',
                '-metadata', f'creation_time={timestamp}',
                '-y',
                str(temp_mp3)
            ]
            
            subprocess.run(cmd, check=True,
                         capture_output=True,
                         timeout=600)
            
            # 用临时文件替换原文件
            shutil.move(str(temp_mp3), str(mp3_path))
            logger.debug(f"MP3元数据已更新: {mp3_path.name}")
        except Exception as e:
            logger.warning(f"设置MP3元数据失败: {e}")
            # 不中断处理流程
    
    def get_directory_date(self) -> Optional[datetime]:
        """
        从目录名解析日期（YYYYMMDD格式）
        
        Returns:
            datetime对象或None
        """
        match = re.search(r'(\d{8})', self.source_dir.name)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y%m%d')
            except ValueError:
                pass
        return None


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python main.py <目录路径> [目录路径2] ...")
        print("\n示例:")
        print("  python main.py ./20070922_mcm")
        print("  python main.py ./20070922_mcm ./20070923_mcm")
        sys.exit(1)
    
    for dir_path in sys.argv[1:]:
        try:
            processor = MediaProcessor(dir_path)
            processor.process_all()
        except Exception as e:
            logger.error(f"处理目录失败 {dir_path}: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
