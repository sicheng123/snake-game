[app]

# 应用包名和标题
title = 贪吃蛇
package.name = snakegame
package.domain = com.sicheng

# 主入口文件
source.dir = snake_game
source.include_exts = py
source.include_patterns = *.py
main.py = main.py

# 版本
version = 1.0.0

# 依赖需求
requirements = python3,pygame

# Android 权限
android.permissions = WRITE_EXTERNAL_STORAGE

# 屏幕方向: landscape (800×600 游戏)
orientation = landscape

# 全屏沉浸
fullscreen = 1

# 图标（可选，后续添加）
# icon.filename = %(source.dir)s/icon.png

# 预置模式
presplash.color = 000000
presplash.font_color = FFFFFF

# Android API 级别
android.api = 33
android.minapi = 21

# NDK 版本（pygame 需要 r25c，较新 NDK 不兼容 pygame C 扩展）
android.ndk = 25c

# SDK 路径（留空让 Buildozer 自动下载）
android.sdk_path =

# NDK 路径（留空让 Buildozer 自动下载）
android.ndk_path =

# p4a 分支（develop 分支有最新的修复）
p4a.branch = develop

# SDL2 bootstrap（pygame 必需）
p4a.bootstrap = sdl2

# 架构
android.arch = arm64-v8a

# 构建选项
android.gradle_dependencies =
android.add_src =

# 日志级别
log_level = 2

# 不启用 Kivy（我们用的是纯 pygame）
android.skip_update = 0

[buildozer]

# 构建目录
build_dir = .buildozer

# 环境变量
env = CFLAGS=-Wno-error=incompatible-function-pointer-types

# 构建模式: debug（开发）/ release（发布）
mode = debug

# 日志级别
log_level = 2
