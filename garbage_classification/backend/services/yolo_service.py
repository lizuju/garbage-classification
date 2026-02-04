import io
import os
from pathlib import Path
import json

import numpy as np
import torch
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont


class YoloService:
    def __init__(self, yolov5_path: Path, project_root: Path):
        self.yolov5_path = Path(yolov5_path)
        self.project_root = Path(project_root)

        # 确保 yolov5 的 import 生效
        import sys
        if str(self.yolov5_path) not in sys.path:
            sys.path.insert(0, str(self.yolov5_path))

        from models.experimental import attempt_load
        from utils.general import check_img_size, non_max_suppression

        self.attempt_load = attempt_load
        self.check_img_size = check_img_size
        self.non_max_suppression = non_max_suppression

        self.model, self.device, self.imgsz, self.stride = self._load_model()
        self.class_names = ['可回收垃圾', '有害垃圾', '厨余垃圾', '其他垃圾']

    def _find_weights(self):
        search_paths = [
            self.project_root / 'best.pt',
            self.yolov5_path / 'runs/train/garbage_model/weights/best.pt',
            self.yolov5_path / 'best.pt',
            self.yolov5_path / 'yolov5m.pt',
            self.yolov5_path / 'yolov5s.pt',
        ]
        for p in search_paths:
            if p.exists():
                return p
        return None

    def _select_device(self):
        # CUDA -> MPS -> CPU
        if torch.cuda.is_available():
            return torch.device('cuda')
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return torch.device('mps')
        return torch.device('cpu')

    def _load_model(self):
        weights = self._find_weights()
        if weights is None:
            raise FileNotFoundError("❌ 未能找到任何权重文件 (.pt)")

        device = self._select_device()
        model = self.attempt_load(weights, device=device)
        stride = int(model.stride.max())
        imgsz = self.check_img_size(640, s=stride)

        is_gpu = device.type in ['cuda', 'mps']
        if is_gpu:
            model.half()
        else:
            model.float()

        # warmup
        warmup_img = torch.zeros(1, 3, imgsz, imgsz, device=device)
        warmup_img = warmup_img.half() if is_gpu else warmup_img.float()
        model(warmup_img)

        print(f"✅ YOLOv5 路径: {self.yolov5_path}")
        print(f"✅ 模型文件: {weights}")
        print(f"✅ 推理设备: {device}")
        return model, device, imgsz, stride

    def _load_chinese_font(self, size=16):
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simkai.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def detect(self, img_bytes: bytes):
        if self.model is None or self.device is None:
            return [], None

        # 模型输入：固定 resize 到 imgsz（保持你原逻辑）
        img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
        img = img.resize((self.imgsz, self.imgsz), PILImage.LANCZOS)
        img_array = np.array(img)

        img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).to(self.device)
        img_tensor = img_tensor / 255.0
        is_gpu = self.device.type in ['cuda', 'mps']
        img_tensor = img_tensor.half() if is_gpu else img_tensor.float()
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)

        with torch.no_grad():
            pred = self.model(img_tensor, augment=False)[0]

        pred = self.non_max_suppression(pred, 0.1, 0.45, None, False, max_det=1000)

        # 结果图：用原图尺寸绘制
        display_img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
        result_img_pil = display_img.copy()
        draw = ImageDraw.Draw(result_img_pil)
        font = self._load_chinese_font(16)

        results = []
        display_w, display_h = display_img.size
        scale_x = display_w / self.imgsz
        scale_y = display_h / self.imgsz

        for det in pred:
            if len(det):
                det_scaled = det.clone()
                det_scaled[:, 0] *= scale_x
                det_scaled[:, 2] *= scale_x
                det_scaled[:, 1] *= scale_y
                det_scaled[:, 3] *= scale_y

                for *xyxy, conf, cls in reversed(det_scaled):
                    c = int(cls)
                    x1, y1, x2, y2 = [int(x) for x in xyxy]

                    if c == 0:
                        color = (53, 118, 202)
                    elif c == 1:
                        color = (220, 53, 69)
                    elif c == 2:
                        color = (40, 167, 69)
                    else:
                        color = (108, 117, 125)

                    draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=3)

                    label = f"{self.class_names[c]} {conf:.2f}"
                    label_size = draw.textbbox((0, 0), label, font=font)[2:]
                    if y1 - label_size[1] - 5 > 0:
                        text_origin = (x1, y1 - label_size[1] - 5)
                    else:
                        text_origin = (x1, y1 + 5)

                    draw.rectangle(
                        [text_origin[0], text_origin[1],
                         text_origin[0] + label_size[0], text_origin[1] + label_size[1]],
                        fill=color
                    )
                    draw.text(text_origin, label, fill=(255, 255, 255), font=font)

                    results.append({
                        'class': c,
                        'class_name': self.class_names[c],
                        'confidence': float(conf),
                        'bbox': [float(x) for x in xyxy]
                    })

        return results, result_img_pil

