import os
import torch
import argparse


def parse_arguments():


    parser = argparse.ArgumentParser(description="persian car plate",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Training parameters
    parser.add_argument("--project_dir", type=str, default=None, help="project path")
    parser.add_argument("--data_path", type=str, help="images or vidoes to test the algoritm")
    parser.add_argument("--save_dir", type=str, default="default",help="Folder to save final images")
    parser.add_argument("--weights", type=str, default="default",help="path to trained yolov7 model for car detection")
    parser.add_argument("--persian_font", type=str)
    parser.add_argument("--image_size", type=int, default=640)


    
    args = parser.parse_args()


    return args
