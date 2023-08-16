from easyocr import Reader
import cv2
import numpy as np
from typing import List, Tuple

class OCR:
    def __init__(self):
        self.reader = Reader(['en','tr'], gpu=False)
        
    def detect_text(self, image_data: bytes) -> Tuple[List[Tuple], List[Tuple]]:
        horizontal_list, free_list = self.reader.detect(image_data, text_threshold=0.85)
        return horizontal_list, free_list
    
    def extract_text(self, image_data: bytes, horizontal_list: List[Tuple], free_list: List[Tuple]) -> str:
        allow_list: str = 'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZWXabcçdefgğhıijklmnoöprsştuüvyzwx0123456789 '

        results = self.reader.recognize(image_data, horizontal_list=horizontal_list[0], free_list=free_list[0], allowlist=allow_list, detail=0)
        full_text = " ".join(results)

        return full_text

    def preprocess_image(self, image_data:np.ndarray):
        img = image_data
        (H, W) = image_data.shape[:2]

        if H > 1280 or W > 1280:
            img = cv2.resize(image_data, (1280, 1280), interpolation=cv2.INTER_CUBIC)

        denoised_image = cv2.fastNlMeansDenoising(img, h=3, templateWindowSize=7, searchWindowSize=21)
        
        kernel = np.ones((1, 1), np.uint8)
        eroded_image = cv2.erode(denoised_image, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)

        return dilated_image

    def perform_ocr(self, image_data: bytes) -> str:
        image_data = cv2.imdecode(np.fromstring(image_data, np.uint8), cv2.IMREAD_COLOR)

        preprocessed_image = self.preprocess_image(image_data)
        
        horizontal_list, free_list = self.detect_text(preprocessed_image)
        full_text = self.extract_text(preprocessed_image, horizontal_list, free_list)
        
        #_draw_and_save_text_sections(results, BytesIO(image_data))
        return full_text

    # for debugging purposes
    def _draw_and_save_text_sections(self, ocr_results: List[Tuple], image_data: bytes) -> None:
        image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), 1)
        for result in ocr_results:
            bbox = np.array(result[0]).astype(int)
            text =  f"Text: {result[1]}"
            confidence = f"Confidence: {result[2]:.2f}"
            cv2.rectangle(image, tuple(bbox[0]), tuple(bbox[2]), (0, 0, 255), 2)
            cv2.putText(image, confidence, (bbox[0][0], bbox[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(image, text, (bbox[0][0], bbox[0][1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imwrite("debug".rsplit('.', 1)[0] + '_bbox.jpg', image)