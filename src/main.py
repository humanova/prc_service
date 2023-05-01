import base64
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response
from pydantic import BaseModel
from typing import List
import uvicorn

import cimri
import ocr

app = FastAPI()

class PriceResponse(BaseModel):
    name: str
    image: str
    prices: List[dict]

class ImageRequest(BaseModel):
    image: str


@app.post("/api/price", response_model=PriceResponse)
async def get_price(image_req: ImageRequest):
    print("got the request!")
    # decode base64 image string and convert to bytes object
    image_data = base64.b64decode(image_req.image)
    
    # perform ocr
    text = ocr.perform_ocr(image_data)
    
    # send sugesstion request
    print("sending suggestion request")
    cimri_data = cimri.get_search_suggestions(text, limit=5)
    if not cimri_data or len(cimri_data) == 0:
        raise HTTPException(status_code=404, detail="No product found")
    
    print(cimri_data)
    # get the first product and its details
    product = cimri_data["products"][0]
    product_title = product["title"]
    image_id = product["imageIds"][0]
    product_id = product["id"]
    product_url = f'https://www.cimri.com{product["path"]}'

    resolution = (600, 600)
    image_url = f"https://cdn.cimri.io/market/{resolution[0]}x{resolution[1]}/-_{image_id}.jpg"
    
    offers = cimri.get_product_offers(product_url)

    if not offers:
        raise HTTPException(status_code=404, detail="No offer found for the product")
    

    # prepare response data
    prices = []
    for offer in offers:
        store_name = offer["store"]
        price = offer["price"]
        prices.append({"store": store_name, "price": price})

    price_response = PriceResponse(name=product_title, image=image_url, prices=prices)
    return price_response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)