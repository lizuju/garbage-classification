# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run classification inference on images

Usage:
    $ python classify/predict.py --weights yolov5s-cls.pt --source im.jpg
"""

import argparse
import os
import sys
from pathlib import Path

import cv2
import torch.nn.functional as F

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from classify.train import imshow_cls
from models.common import DetectMultiBackend
from utils.augmentations import classify_transforms
from utils.general import LOGGER, check_requirements, colorstr, increment_path, print_args
from utils.torch_utils import select_device, smart_inference_mode, time_sync

CLASSNAME_FILE_CANDIDATES = [
    ROOT / 'classname.txt',
    ROOT.parent / 'classname.txt',
]


def load_classnames():
    for p in CLASSNAME_FILE_CANDIDATES:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f.readlines()]
            return [n for n in names if n]
    return []


def normalize_model_names(names):
    if names is None:
        return []
    if isinstance(names, dict):
        return [v for _, v in sorted(names.items(), key=lambda kv: kv[0])]
    if isinstance(names, (list, tuple)):
        return list(names)
    return []


def build_imagenet_dict_order(n):
    # ImageFolder dictionary order (lexicographic) for folder names: 0,1,10,100...
    return sorted([str(i) for i in range(n)])


def select_sub_logits(outputs):
    # DetectMultiBackend output compatibility
    if isinstance(outputs, (tuple, list)):
        return outputs[0]
    if isinstance(outputs, dict):
        if 'sub_class' in outputs:
            return outputs['sub_class']
        return next(iter(outputs.values()))
    return outputs


def map_index_to_chinese(idx, model_names, cn_names, dict_order):
    name = model_names[idx] if idx < len(model_names) else str(idx)
    name_str = str(name)

    if name_str.startswith('class') and name_str[5:].isdigit():
        out_idx = int(name_str[5:])
        if 0 <= out_idx < len(dict_order):
            dir_name = dict_order[out_idx]
            if dir_name.isdigit():
                class_id = int(dir_name)
                if 0 <= class_id < len(cn_names):
                    return cn_names[class_id]

    if name_str.isdigit():
        class_id = int(name_str)
        if 0 <= class_id < len(cn_names):
            return cn_names[class_id]

    if 0 <= idx < len(cn_names):
        return cn_names[idx]

    return name_str


@smart_inference_mode()
def run(
        weights=ROOT / 'best.pt',  # model.pt path(s)
        source=ROOT / 'data/images/bus.jpg',  # file/dir/URL/glob, 0 for webcam
        imgsz=224,  # inference size
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        show=True,
        project=ROOT / 'runs/predict-cls',  # save to project/name
        name='exp',  # save to project/name
        exist_ok=False,  # existing project/name ok, do not increment
):
    file = str(source)
    seen, dt = 1, [0.0, 0.0, 0.0]
    device = select_device(device)

    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    save_dir.mkdir(parents=True, exist_ok=True)  # make dir

    # Transforms
    transforms = classify_transforms(imgsz)

    # Load model (prefer best.pt)
    weights = Path(weights)
    if not weights.exists() and weights.name == 'best.pt':
        fallback = ROOT.parent / 'best.pt'
        if fallback.exists():
            weights = fallback
    model = DetectMultiBackend(weights, device=device, dnn=dnn, fp16=half)
    model.warmup(imgsz=(1, 3, imgsz, imgsz))  # warmup

    cn_names = load_classnames()
    model_names = normalize_model_names(getattr(model, 'names', None))
    dict_order = build_imagenet_dict_order(len(cn_names))

    # Image
    t1 = time_sync()
    im = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
    im = transforms(im).unsqueeze(0).to(device)
    im = im.half() if model.fp16 else im.float()
    t2 = time_sync()
    dt[0] += t2 - t1

    # Inference
    results = model(im)
    t3 = time_sync()
    dt[1] += t3 - t2

    logits = select_sub_logits(results)
    p = F.softmax(logits, dim=1)  # probabilities
    i = p.argsort(1, descending=True)[:, :5].squeeze()  # top 5 indices
    dt[2] += time_sync() - t3

    topk = []
    for j in i:
        j = int(j)
        label = map_index_to_chinese(j, model_names, cn_names, dict_order)
        topk.append(f"{label} {p[0, j]:.2f}")

    top1_idx = int(i[0]) if hasattr(i, '__len__') else int(i)
    top1_label = map_index_to_chinese(top1_idx, model_names, cn_names, dict_order)
    LOGGER.info(f"image 1/1 {file}: {imgsz}x{imgsz} Top-5: {', '.join(topk)}")
    LOGGER.info(f"Top-1: {top1_label} {p[0, top1_idx]:.2f}")

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    shape = (1, 3, imgsz, imgsz)
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms post-process per image at shape {shape}' % t)
    if show:
        imshow_cls(im, f=save_dir / Path(file).name, verbose=True)
    LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}")
    return p


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'best.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images/bus.jpg', help='file')
    parser.add_argument('--imgsz', '--img', '--img-size', type=int, default=224, help='train, val image size (pixels)')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--project', default=ROOT / 'runs/predict-cls', help='save to project/name')
    parser.add_argument('--name', default='exp', help='save to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    print_args(vars(opt))
    return opt


def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
