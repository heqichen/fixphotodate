#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


VIDEO_EXTENSIONS = {
	".3gp",
	".amr",
	".asf",
	".avi",
	".flv",
	".m2ts",
	".m4v",
	".mkv",
	".mov",
	".mpg",
	".mpeg",
	".mts",
	".rm",
	".rmvb",
	".ts",
	".vob",
	".webm",
	".wmv",
}


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="将目录中的视频文件转换为 MP4（保持原始质量，不改变分辨率与尺寸，输出名为原文件名+.mp4）"
	)
	parser.add_argument("directory", help="待处理目录路径")
	parser.add_argument(
		"-r",
		"--recursive",
		action="store_true",
		help="递归遍历所有子目录中的视频文件",
	)
	parser.add_argument(
		"--overwrite",
		action="store_true",
		help="若目标 mp4 已存在则覆盖（默认跳过）",
	)
	return parser.parse_args()


def is_video_file(path: Path) -> bool:
	return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def normalize_datetime_text(value: str) -> str | None:
	text = value.strip()
	if not text:
		return None

	if text.upper().startswith("UTC "):
		text = text[4:].strip()

	text = text.replace("/", "-")
	if len(text) >= 5 and (text[-5] in ("+", "-") and text[-3] != ":"):
		text = f"{text[:-2]}:{text[-2:]}"

	if " " in text and "T" not in text:
		text = text.replace(" ", "T", 1)

	time_candidates = [text]
	if text.endswith("Z"):
		time_candidates.append(text[:-1] + "+00:00")

	for candidate in time_candidates:
		try:
			dt = datetime.fromisoformat(candidate)
			if dt.tzinfo is None:
				dt = dt.replace(tzinfo=timezone.utc)
			return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
		except ValueError:
			continue

	for fmt in (
		"%Y:%m:%d %H:%M:%S",
		"%Y-%m-%d %H:%M:%S",
		"%Y-%m-%dT%H:%M:%S",
	):
		try:
			dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
			return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
		except ValueError:
			continue

	return None


def extract_creation_time_ffprobe(input_file: Path) -> str | None:
	if shutil.which("ffprobe") is None:
		return None

	cmd = [
		"ffprobe",
		"-v",
		"error",
		"-print_format",
		"json",
		"-show_format",
		"-show_streams",
		str(input_file),
	]

	try:
		result = subprocess.run(
			cmd,
			check=True,
			capture_output=True,
			text=True,
		)
		data = json.loads(result.stdout)
	except (subprocess.CalledProcessError, json.JSONDecodeError):
		return None

	tag_keys = [
		"creation_time",
		"com.apple.quicktime.creationdate",
		"media_create_date",
		"track_create_date",
		"date",
		"creationdate",
		"encoded_date",
		"tagged_date",
	]

	def pick_from_tags(tags: dict[str, str] | None) -> str | None:
		if not tags:
			return None
		lower_map = {k.lower(): str(v) for k, v in tags.items()}
		for key in tag_keys:
			if key in lower_map:
				normalized = normalize_datetime_text(lower_map[key])
				if normalized:
					return normalized
		return None

	format_tags = data.get("format", {}).get("tags")
	picked = pick_from_tags(format_tags)
	if picked:
		return picked

	for stream in data.get("streams", []):
		picked = pick_from_tags(stream.get("tags"))
		if picked:
			return picked

	return None


def extract_creation_time_exiftool(input_file: Path) -> str | None:
	if shutil.which("exiftool") is None:
		return None

	cmd = ["exiftool", "-j", "-api", "QuickTimeUTC=1", str(input_file)]
	try:
		result = subprocess.run(
			cmd,
			check=True,
			capture_output=True,
			text=True,
		)
		records = json.loads(result.stdout)
		if not records:
			return None
		record = records[0]
	except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError):
		return None

	for key in (
		"MediaCreateDate",
		"TrackCreateDate",
		"CreateDate",
		"CreationDate",
		"DateTimeOriginal",
	):
		value = record.get(key)
		if isinstance(value, str):
			normalized = normalize_datetime_text(value)
			if normalized:
				return normalized

	return None


def extract_creation_time_filesystem(input_file: Path) -> str | None:
	stat = input_file.stat()
	birth_time = getattr(stat, "st_birthtime", None)
	timestamp = birth_time if birth_time is not None else stat.st_mtime
	dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
	return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_media_creation_time(input_file: Path) -> tuple[str | None, str]:
	ffprobe_time = extract_creation_time_ffprobe(input_file)
	if ffprobe_time:
		return ffprobe_time, "ffprobe"

	exiftool_time = extract_creation_time_exiftool(input_file)
	if exiftool_time:
		return exiftool_time, "exiftool"

	fs_time = extract_creation_time_filesystem(input_file)
	return fs_time, "filesystem"


def build_ffmpeg_command(
	input_file: Path,
	output_file: Path,
	overwrite: bool,
	creation_time: str | None,
	video_mode: str,
	audio_mode: str,
) -> list[str]:
	command = [
		"ffmpeg",
		"-hide_banner",
		"-loglevel",
		"error",
		"-y" if overwrite else "-n",
		"-i",
		str(input_file),
		"-map_metadata",
		"0",
		"-map",
		"0:v?",
		"-map",
		"0:a?",
	]

	if video_mode == "copy":
		command.extend(["-c:v", "copy"])
	else:
		command.extend(["-c:v", "libx264", "-preset", "slow", "-crf", "18"])

	if audio_mode == "copy":
		command.extend(["-c:a", "copy"])
	else:
		command.extend(["-c:a", "aac", "-b:a", "320k"])

	if creation_time:
		command.extend(["-metadata", f"creation_time={creation_time}"])

	command.append(str(output_file))
	return command


def get_output_file(input_file: Path) -> Path:
	return input_file.with_name(f"{input_file.name}.mp4")


def convert_video(input_file: Path, overwrite: bool) -> str:
	output_file = get_output_file(input_file)

	if input_file.suffix.lower() == ".mp4":
		print(f"[跳过] 已是 MP4: {input_file.name}")
		return "skipped"

	if output_file.exists() and not overwrite:
		print(f"[跳过] 目标已存在: {output_file.name}")
		return "skipped"

	creation_time, source = get_media_creation_time(input_file)
	if creation_time:
		print(f"[时间] {input_file.name} -> {creation_time} (来源: {source})")

	cmd = build_ffmpeg_command(
		input_file,
		output_file,
		overwrite,
		creation_time,
		video_mode="copy",
		audio_mode="copy",
	)
	try:
		subprocess.run(cmd, check=True)
		print(f"[完成] {input_file.name} -> {output_file.name}")
		return "success"
	except subprocess.CalledProcessError:
		if output_file.exists():
			output_file.unlink(missing_ok=True)
		print(f"[提示] 直接拷贝音频失败，尝试转为 AAC: {input_file.name}")

	retry_cmd = build_ffmpeg_command(
		input_file,
		output_file,
		overwrite,
		creation_time,
		video_mode="copy",
		audio_mode="aac",
	)
	try:
		subprocess.run(retry_cmd, check=True)
		print(f"[完成] {input_file.name} -> {output_file.name} (音频已转 AAC)")
		return "success"
	except subprocess.CalledProcessError:
		if output_file.exists():
			output_file.unlink(missing_ok=True)
		print(f"[提示] 视频流不兼容 MP4，尝试转为 H.264: {input_file.name}")

	final_cmd = build_ffmpeg_command(
		input_file,
		output_file,
		overwrite,
		creation_time,
		video_mode="h264",
		audio_mode="aac",
	)
	try:
		subprocess.run(final_cmd, check=True)
		print(f"[完成] {input_file.name} -> {output_file.name} (视频已转 H.264, 音频已转 AAC)")
		return "success"
	except subprocess.CalledProcessError:
		if output_file.exists():
			output_file.unlink(missing_ok=True)
		print(f"[失败] 转换失败: {input_file.name}")
		return "failed"


def main() -> int:
	args = parse_args()
	directory = Path(args.directory).expanduser().resolve()

	if shutil.which("ffmpeg") is None:
		print("错误: 未找到 ffmpeg，请先安装并确保 ffmpeg 在 PATH 中。", file=sys.stderr)
		return 1

	if not directory.exists() or not directory.is_dir():
		print(f"错误: 目录不存在或不是目录: {directory}", file=sys.stderr)
		return 1

	iterator = directory.rglob("*") if args.recursive else directory.iterdir()
	video_files = sorted(path for path in iterator if is_video_file(path))
	if not video_files:
		print(f"未找到可转换的视频文件: {directory}")
		return 0

	print(f"开始处理目录: {directory}")
	print(f"检测到 {len(video_files)} 个视频文件")

	success_count = 0
	skipped_count = 0
	failed_count = 0

	for video_file in video_files:
		result = convert_video(video_file, args.overwrite)
		if result == "success":
			success_count += 1
		elif result == "skipped":
			skipped_count += 1
		else:
			failed_count += 1

	print("\n处理完成")
	print(f"成功: {success_count}")
	print(f"跳过: {skipped_count}")
	print(f"失败: {failed_count}")
	return 0 if failed_count == 0 else 2


if __name__ == "__main__":
	raise SystemExit(main())
