#!/bin/bash
# 切换到 yolov5-6.0 目录
cd yolov5-6.0

# 执行 YOLOv5 检测任务
python3 detect.py --weights best.pt --source ../datasets/wangy/images/train --img 640 --conf 0.25

# 暂停（可选）——等待用户按键退出
read -p "Press Enter to exit..."
