# persian car plate detection
## plate detection model
As a first step we need to develop a model to detect vehicle registration plate, follow the steps in training_custome_yolov7.ipynb to do so 
or you could use my pretrained model at this link :
https://drive.google.com/file/d/126Td8QOBC80Av1EnGVj7HrB6wEeG36U2/view?usp=sharing


## persian fonts

``` shell
git clone https://github.com/rastikerdar/vazirmatn.git
cp vazirmatn/fonts/ttf/* {your dir} 
```

# reading plate numbers
you can either follow plates notebook or use the command below after cloning to project


``` shell
pip install -r requirements.txt
python detect.py --project_dir /content/project   --data_path /content/data  --save_dir /content --weights weights/best.pt --persian_font persian_font/Vazirmatn-Regular.ttf --image_size 640
```

