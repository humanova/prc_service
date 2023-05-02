from io import BytesIO

from easyocr import Reader
import numpy as np
import cv2



# for debugging purposes
def _draw_and_save_text_sections(ocr_results, image_data):
    image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), 1)
    for result in ocr_results:
        bbox = np.array(result[0]).astype(int)
        text =  f"Text: {result[1]}"
        confidence = f"Confidence: {result[2]:.2f}"
        cv2.rectangle(image, tuple(bbox[0]), tuple(bbox[2]), (0, 0, 255), 2)
        cv2.putText(image, confidence, (bbox[0][0], bbox[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(image, text, (bbox[0][0], bbox[0][1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imwrite("debug".rsplit('.', 1)[0] + '_bbox.jpg', image)

def perform_ocr(image_data:bytes):
    reader = Reader(['en','tr'], gpu=False)

    results = reader.readtext(image_data, text_threshold=0.85)
    # optional
    #_draw_and_save_text_sections(results, BytesIO(image_data))

    text_sections = [r[1] for r in results]

    full_text = " ".join(text_sections)
    return full_text