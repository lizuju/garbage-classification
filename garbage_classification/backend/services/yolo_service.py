import io
import os
from pathlib import Path
import json
from collections import deque

import numpy as np
import torch
from PIL import Image as PILImage
from PIL import ImageEnhance, ImageFilter
from PIL import ImageDraw, ImageFont
from torchvision import transforms


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
        self.cls_imgsz = 448
        self.cls_mean = [0.485, 0.456, 0.406]
        self.cls_std = [0.229, 0.224, 0.225]
        self.class_names = self._load_class_names()
        self.model_names = self._normalize_model_names(getattr(self.model, 'names', None))
        self.dict_order = self._build_imagenet_dict_order(len(self.class_names))
        self.realtime_history = {}
        self.realtime_window = 3
        self.realtime_conf_threshold = 0.2
        self.realtime_crop_ratio = 0.7

    def _load_class_names(self):
        candidates = [
            self.project_root / 'classname.txt',
            self.project_root / 'garbage265_hierarchical' / 'classname.txt',
        ]
        for p in candidates:
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    names = [line.strip() for line in f.readlines()]
                names = [n for n in names if n]
                if names:
                    return names
        return ['可回收垃圾', '有害垃圾', '厨余垃圾', '其他垃圾']

    def _normalize_model_names(self, names):
        if names is None:
            return []
        if isinstance(names, dict):
            return [v for _, v in sorted(names.items(), key=lambda kv: kv[0])]
        if isinstance(names, (list, tuple)):
            return list(names)
        return []

    def _build_imagenet_dict_order(self, n):
        # ImageFolder dictionary order (lexicographic) for folder names: 0,1,10,100...
        return sorted([str(i) for i in range(n)])

    def _map_index_to_chinese(self, idx):
        name = self.model_names[idx] if idx < len(self.model_names) else str(idx)
        name_str = str(name)

        if name_str.startswith('class') and name_str[5:].isdigit():
            out_idx = int(name_str[5:])
            if 0 <= out_idx < len(self.dict_order):
                dir_name = self.dict_order[out_idx]
                if dir_name.isdigit():
                    class_id = int(dir_name)
                    if 0 <= class_id < len(self.class_names):
                        return self.class_names[class_id]

        if name_str.isdigit():
            class_id = int(name_str)
            if 0 <= class_id < len(self.class_names):
                return self.class_names[class_id]

        if 0 <= idx < len(self.class_names):
            return self.class_names[idx]

        return name_str

    def _find_weights(self):
        search_paths = [
            self.project_root / 'garbage265_hierarchical' / 'weights' / 'best.pt',
            # self.project_root / 'best.pt',
            # self.yolov5_path / 'runs/train/garbage_model/weights/best.pt',
            # self.yolov5_path / 'best.pt',
            # self.yolov5_path / 'yolov5m.pt',
            # self.yolov5_path / 'yolov5s.pt',
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
        model.eval()
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

    def _select_output(self, outputs):
        # Compatible with DetectMultiBackend outputs (tuple/dict/tensor)
        if isinstance(outputs, (tuple, list)):
            if not outputs:
                return None
            return outputs[0]
        if isinstance(outputs, dict):
            if 'sub_class' in outputs:
                return outputs['sub_class']
            return next(iter(outputs.values()))
        return outputs

    def _preprocess_realtime_image(self, img: PILImage.Image):
        w, h = img.size
        ratio = max(0.5, min(1.0, float(self.realtime_crop_ratio)))
        crop_w = int(w * ratio)
        crop_h = int(h * ratio)
        left = int((w - crop_w) / 2)
        top = int((h - crop_h) / 2)
        img = img.crop((left, top, left + crop_w, top + crop_h))

        # Light denoise + mild tone adjustments
        img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
        img = ImageEnhance.Contrast(img).enhance(1.06)
        img = ImageEnhance.Color(img).enhance(1.05)
        img = ImageEnhance.Brightness(img).enhance(1.02)
        return img

    def _get_realtime_history(self, key):
        if key not in self.realtime_history:
            self.realtime_history[key] = deque(maxlen=self.realtime_window)
        return self.realtime_history[key]

    def detect_realtime(self, img_bytes: bytes, user_key=None):
        if self.model is None or self.device is None:
            return [], None, 0.0

        img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
        img = self._preprocess_realtime_image(img)
        is_gpu = self.device.type in ['cuda', 'mps']

        with torch.no_grad():
            cls_transform = transforms.Compose([
                transforms.Resize((self.cls_imgsz, self.cls_imgsz)),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.cls_mean, std=self.cls_std),
            ])
            img_tensor = cls_transform(img).unsqueeze(0).to(self.device)
            img_tensor = img_tensor.half() if is_gpu else img_tensor.float()
            outputs = self.model(img_tensor)
            pred = self._select_output(outputs)

        if pred is None:
            return [], None, 0.0

        if pred.ndimension() == 1:
            pred = pred.unsqueeze(0)
        if pred.ndimension() != 2:
            return [], None, 0.0

        probs = torch.softmax(pred, dim=1)[0].detach().float().cpu()
        history = self._get_realtime_history(user_key or 'anon')
        history.append(probs)
        avg_probs = torch.stack(list(history)).mean(dim=0)

        top_k = min(5, len(self.class_names) if self.class_names else avg_probs.numel())
        topk_probs, topk_idxs = avg_probs.topk(top_k)

        results = []
        for score, idx in zip(topk_probs.tolist(), topk_idxs.tolist()):
            name = self._map_index_to_chinese(int(idx))
            results.append({
                'class': int(idx),
                'class_name': name,
                'confidence': float(score),
                'bbox': None
            })

        top1_conf = results[0]['confidence'] if results else 0.0
        if top1_conf < self.realtime_conf_threshold:
            return [], None, top1_conf

        return results, None, top1_conf

    def detect(self, img_bytes: bytes):
        if self.model is None or self.device is None:
            return [], None

        img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
        is_gpu = self.device.type in ['cuda', 'mps']

        with torch.no_grad():
            # For classification, use ImageNet normalization and 448x448 input
            cls_transform = transforms.Compose([
                transforms.Resize((self.cls_imgsz, self.cls_imgsz)),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.cls_mean, std=self.cls_std),
            ])
            img_tensor = cls_transform(img).unsqueeze(0).to(self.device)
            img_tensor = img_tensor.half() if is_gpu else img_tensor.float()
            outputs = self.model(img_tensor)
            pred = self._select_output(outputs)

        if pred is None:
            return [], None

        # Classification output: [batch, num_classes]
        if pred.ndimension() == 2:
            probs = torch.softmax(pred, dim=1)[0]
            top_k = min(5, len(self.class_names) if self.class_names else probs.numel())
            topk_probs, topk_idxs = probs.topk(top_k)

            display_img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
            result_img_pil = display_img.copy()
            draw = ImageDraw.Draw(result_img_pil)
            font = self._load_chinese_font(18)

            results = []
            text_lines = []
            for score, idx in zip(topk_probs.tolist(), topk_idxs.tolist()):
                name = self._map_index_to_chinese(int(idx))
                results.append({
                    'class': int(idx),
                    'class_name': name,
                    'confidence': float(score),
                    'bbox': None
                })
                text_lines.append(f"{name} {score * 100:.1f}%")

            if text_lines:
                text = " | ".join(text_lines)
                draw.text((10, 10), text, fill=(255, 255, 255), font=font)

            return results, result_img_pil

        # Detection path (fallback)
        img_resized = img.resize((self.imgsz, self.imgsz), PILImage.LANCZOS)
        img_array = np.array(img_resized)
        img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).to(self.device)
        img_tensor = img_tensor / 255.0
        img_tensor = img_tensor.half() if is_gpu else img_tensor.float()
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)

        with torch.no_grad():
            pred = self.model(img_tensor)[0]

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
