![image]([https://github.com/WaNgzh1rUi/Wang-repository/tree/master/images](https://github.com/WaNgzh1rUi/Wang-repository/blob/master/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202024-10-14%20132312.png))

基于YOLOv8的车牌识别代码，可以直接运行（图片和视频都可以识别）
data.yaml 里面的文件路径需要替换为自己的本地路径，否则会报错
train: C:\python_study\CarPlateDetection_1\datasets\PlateData\images\train  # train images (relative to 'path') 128 images
val: C:\python_study\CarPlateDetection_1\datasets\PlateData\images\val  # val images (relative to 'path') 128 images
test:  C:\python_study\CarPlateDetection_1\datasets\PlateData\images\test # val images (optional)

模型已经训练好了，直接调用pt文件就行，如果想要自己训练一下可以直接运行train.py 文件
epoch 和 batch size都可以自己定义
