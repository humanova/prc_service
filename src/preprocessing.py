import cv2
import numpy as np

class Preprocessing:
    def preprocess_image(image_data:np.ndarray):
        img = image_data
        (H, W) = image_data.shape[:2]

        resized_image = None
        if H > 1280 and W > 1280:
            resized_image = cv2.resize(image_data, (1280, 1280), interpolation=cv2.INTER_CUBIC)
            img = resized_image

        denoised_image = cv2.fastNlMeansDenoising(img, h=3, templateWindowSize=7, searchWindowSize=21)
        
        kernel = np.ones((1, 1), np.uint8)
        eroded_image = cv2.erode(denoised_image, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)

        return dilated_image
