from easyocr import Reader
import numpy as np
import cv2
from preprocessing import Preprocessing

class OCR(Preprocessing):

    def __init__(self):
        self.reader = Reader(['en','tr'], gpu=False)

    # for debugging purposes
    def _draw_and_save_text_sections(self, ocr_results, image_data):
        image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), 1)
        for result in ocr_results:
            bbox = np.array(result[0]).astype(int)
            text =  f"Text: {result[1]}"
            confidence = f"Confidence: {result[2]:.2f}"
            cv2.rectangle(image, tuple(bbox[0]), tuple(bbox[2]), (0, 0, 255), 2)
            cv2.putText(image, confidence, (bbox[0][0], bbox[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(image, text, (bbox[0][0], bbox[0][1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imwrite("debug".rsplit('.', 1)[0] + '_bbox.jpg', image)

    def text_detection(self, image_data):
        horizontal_list, free_list = self.reader.detect(image_data, text_threshold=0.85)
       
        return horizontal_list, free_list
    
    def text_extraction(self, image_data, horizontal_list, free_list):
        allow_list = 'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZWXabcçdefgğhıijklmnoöprsştuüvyzwx0123456789 '

        results = self.reader.recognize(image_data, horizontal_list=horizontal_list[0], free_list=free_list[0], allowlist=allow_list, detail=0)
        full_text = " ".join(results)

        return full_text

    def perform_ocr(self, image_data):
        nparr = np.fromstring(image_data, np.uint8)
        image_data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        preprocessed_image = self.preprocess_image(image_data)
        
        horizontal_list, free_list = self.text_detection(preprocessed_image)
        full_text = self.text_extraction(preprocessed_image, horizontal_list, free_list)
        
        # optional
        #_draw_and_save_text_sections(results, BytesIO(image_data))

        return full_text