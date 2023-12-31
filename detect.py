import argparse
import os
import time
import numpy as np
import cv2
from cvu.detector.yolov5 import Yolov5 as Yolov5Onnx
from vidsz.opencv import Reader, Writer


CLASSES = ["5 Arbuz", "Agusha", "Batonchik",  "ChocoBoy", "Cofe Monarch", "Confety Cocos",  "Fresh Bar", "Goroh Bonduelle",  "Jam Strawberry",  "Kuza Lakomkin","Lists Salat", "Machiatto", "Nuts", "Olives","Orbit", "Oreo", "Pechenie Belvita",  "Pechenie Imbir",  "Pivo", "Pure Heinz", "Salat", "Shampoo", "Sochnik","Sosiski", "Sugar", "Tess", "Xleb"]


def detect_video(device, weight, input_video, output_video=None):
    model = Yolov5Onnx(classes=CLASSES,
                       backend="onnx",
                       weight=weight,
                       device=device)
    reader = Reader(input_video)
    writer = Writer(reader,
                    name=output_video) if output_video is not None else None

    # warmup
    warmup = np.random.randint(0, 255, reader.read().shape).astype("float")
    for i in range(10):
        model(warmup)

    inference_time = 0
    for frame in reader:
        # inference
        start = time.time()
        preds = model(frame)
        inference_time += time.time() - start

        # draw on frame
        if writer is not None:
            preds.draw(frame)
            writer.write(frame)

    print("\nModel Inference FPS: ",
          round(reader.frame_count / inference_time, 3))
    print("Output Video Saved at: ", writer.name)
    writer.release()
    reader.release()


def detect_image(device, weight, image_path, output_image):
    # load model
    model = Yolov5Onnx(classes=CLASSES,
                       backend="onnx",
                       weight=weight,
                       device=device)

    # read image
    image = cv2.imread(image_path)

    # inference
    preds = model(image)
    print(preds)

    # draw image
    preds.draw(image)

    # write image
    cv2.imwrite(output_image, image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input',
                        type=str,
                        default='foo.mp4',
                        help='path to input video or image file')

    parser.add_argument('--output',
                        type=str,
                        default='foo_out.jpg',
                        help='name of output video or image file')

    parser.add_argument('--device', type=str, default='cpu', help='cpu or gpu')

    opt = parser.parse_args()

    # image file
    input_ext = os.path.splitext(opt.input)[-1]
    output_ext = os.path.splitext(opt.output)[-1]

    if input_ext in (".jpg", ".jpeg", ".png"):
        if output_ext not in ((".jpg", ".jpeg", ".png")):
            opt.output = opt.output.replace(output_ext, input_ext)
        detect_image(opt.device, 'model/best_product.onnx', opt.input, opt.output)

    # video file
    else:
        detect_video(opt.device, 'model/best_product.onnx', opt.input, opt.output)
