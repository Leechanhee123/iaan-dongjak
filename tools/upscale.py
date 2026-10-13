"""저해상도 사진 한 장을 초해상도 모델로 키운다 (원본을 못 받은 사진의 임시 처방).

실행: python tools/upscale.py <모델.pth> <입력> <출력.png>   (torch + CUDA, spandrel 필요)
모델: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
없던 디테일을 그려 넣는 방식이라 결과는 눈으로 확인하고 쓴다. 원본을 받으면 이 단계는 뺀다.
"""
import sys

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

weights, src, dst = sys.argv[1:4]
model = ModelLoader().load_from_file(weights).cuda().eval()
im = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32) / 255
x = torch.from_numpy(im).permute(2, 0, 1)[None].cuda()
with torch.inference_mode():
    y = model(x)
out = (y[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy() * 255).round().astype(np.uint8)
Image.fromarray(out).save(dst)
print(model.architecture.name, f"x{model.scale}", im.shape[1::-1], "->", out.shape[1::-1])
