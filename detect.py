import parser
import os
import shutil
import torch
from pathlib import Path
from typing import Union
import torch
import cv2 as cv
import numpy as np
from copy import deepcopy
import easyocr
from google.colab.patches import cv2_imshow
from colorama import Fore
from deep_sort_realtime.deepsort_tracker import DeepSort

# from utils.experimental import attempt_load
# from utils.utils import check_img_size
# from utils.torch_utils import select_device, TracedModel
# # from utils.datasets import letterbox
# from utils.general import non_max_suppression, scale_coords
from utils.utils import plot_one_box, plot_one_box_PIL
# from utils.lines import make_plate_horizantal


##################################
args = parser.parse_arguments()

project_dir  = args.project_dir
data_dir     = args.data_path
save_dir     = args.save_dir
weights      = args.weights
image_size   = args.image_size
persian_font = args.persian_font

##################################

yolo_path = os.path.join(project_dir, "yolov7")
os.chdir(yolo_path)
print(os.listdir('.'))
from models.experimental import attempt_load
from utils.general import check_img_size
from utils.torch_utils import select_device, TracedModel
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords
os.chdir(project_dir)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('current device: ',device)
trace = False
half = device.type != 'cpu'  # half precision only supported on CUDA

# Load model
model = attempt_load(weights, map_location=device)  # load FP32 model
stride = int(model.stride.max())  # model stride
imgsz = check_img_size(image_size, s=stride)  # check img_size

if trace:
    model = TracedModel(model, device, image_size)

if half:
    model.half()  # to FP16
    
if device.type != 'cpu':
    model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once


# Load OCR
reader = easyocr.Reader(['fa'])


def detect_plate(source_image,img_size = 640):
  
    stride = 32
    img = letterbox(source_image, img_size, stride=stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
        
    with torch.no_grad():
        # Inference
        pred = model(img, augment=True)[0]

    # Apply NMS
    pred = non_max_suppression(pred, 0.25, 0.45, classes=0, agnostic=True)

    plate_detections = []
    det_confidences = []
    
    # Process detections
    for i, det in enumerate(pred):  # detections per image
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], source_image.shape).round()

            # Return results
            for *xyxy, conf, cls in reversed(det):
                coords = [int(position) for position in (torch.tensor(xyxy).view(1, 4)).tolist()[0]]
                plate_detections.append(coords)
                det_confidences.append(conf.item())

    return plate_detections, det_confidences



    return True
def ocr_plate(plate_region):
    # Image pre-processing for more accurate OCR
    # cv.imwrite(os.path.join(savepath, "plate_img.png"), plate_region)
    rescaled = cv.resize(plate_region, None, fx=1.2, fy=1.2, interpolation=cv.INTER_CUBIC)
    if  len( rescaled .shape) > 2:
         grayscale = cv.cvtColor(rescaled, cv.COLOR_BGR2GRAY)
    else:
      grayscale =rescaled
    
          
    # OCR the preprocessed image
    grayscale_blur = cv.medianBlur(grayscale, 1)
    ret, thresh1 = cv.threshold(grayscale_blur, 120, 255, cv.THRESH_BINARY + cv.THRESH_OTSU) 
    # cv.imwrite(os.path.join(savepath, "grayscale_blur.png"), grayscale_blur)
    plate_text_easyocr = reader.readtext(grayscale_blur)
    if plate_text_easyocr:
        (bbox, text_easyocr, ocr_confidence) = plate_text_easyocr[0]
        print("plate_text Easyocr ", text_easyocr)
    else:
        text_easyocr = "_"
        ocr_confidence = 0
    #if ocr_confidence == 'nan':
    
    return text_easyocr, ocr_confidence


def crop(image, coord):
    cropped_image = image[int(coord[1]):int(coord[3]), int(coord[0]):int(coord[2])]
    return cropped_image
def get_plates_from_image(input,save_dir,Save_Name=None,font_location=None):
    if input is None:
        return None
    plate_detections, det_confidences = detect_plate(input)
    plate_texts = []
    ocr_confidences = []
    detected_image = deepcopy(input)
    for coords in plate_detections:
        plate_region = crop(input, coords)
        plate_region_rotated,rot_ang = make_plate_horizantal(plate_region,save_rotated =True,save_path=save_dir,save_name=Save_Name)
        if plate_region_rotated is not None:
          plate_text, ocr_confidence = ocr_plate(plate_region_rotated)
        else:
          plate_text, ocr_confidence = ocr_plate(plate_region)
        plate_texts.append(plate_text)
        ocr_confidences.append(ocr_confidence)
        detected_image = plot_one_box_PIL(coords, detected_image, label=plate_text, color=[0, 150, 255], line_thickness=2,font_path=font_location)
        cv.imwrite(os.path.join(save_dir, 'detected_{}.jpg'.format(Save_Name)),detected_image)
    return detected_image

##################
ALL_img = os.listdir( data_dir)
images_to_process = []
images_names = []
for i in range(len(ALL_img)):
  tem = ALL_img[i].spilt('.')
  if tem[-1] == 'jpg' or tem[-1] =='png':
    images_names.append(tem[0].split('/')[-1])
    images_names.append(ALL_img[i])
if len(images_to_process)  ==0:
  print(Fore.RED,'there is no jpg or png image')

for index in range(len(images_to_process )):
  input_img = images_to_process[index]
  plate_image = cv.imread(input_img)
  result = get_plates_from_image(plate_image,save_dir= save_dir ,Save_Name = images_names[index],font_location=persian_font )

