import imageio.v3 as iio
import numpy as np
import cv2
import os


frame_savepath = r"E:\2\vs code\RayTracingOneWeek\bbb"
gif_name = r"E:\2\vs code\RayTracingOneWeek\bbbb.webp"
delay = 200
resize_dim = (1920, 1080)

image = []
for root, dirs, file in os.walk(frame_savepath + '\\'):
    for name in file:
        img_array = iio.imread(root + name)
        img_array = cv2.resize(img_array, resize_dim, cv2.INTER_CUBIC)
        try:
            img_array.shape[2]

        except IndexError:
            img2 = np.zeros((img_array.shape[0], img_array.shape[1], 3)).astype(np.uint8)
            for i in range(3):
                img2[:, :, i] = img_array
            img_array = img2
        image.append(img_array)

print(type(image))

image = np.array(image)
iio.imwrite(gif_name, image, duration=delay, kmax=1)
