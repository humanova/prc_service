import base64

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response
from pydantic import BaseModel
from typing import List
import uvicorn

import cimri
import ocr
import cache

app = FastAPI()

class PriceResponse(BaseModel):
    name: str
    image: str
    prices: List[dict]

class ImageRequest(BaseModel):
    image: str


@app.post("/api/price", response_model=PriceResponse)
async def get_price(image_req: ImageRequest):
    # decode base64 image string and convert to bytes object
    image_data = base64.b64decode(image_req.image)
    
    # perform ocr
    text = ocr.perform_ocr(image_data)
    print(f"OCR result : {text}")

    # send sugesstion request
    cimri_data = cimri.get_search_suggestions(text, limit=5)
    if not cimri_data or len(cimri_data["products"]) == 0:
        raise HTTPException(status_code=404, detail="No product found")
    
    product = cimri_data["products"][0]
    product_id = product["id"]
    product_title = product["title"]
    product_url = f'https://www.cimri.com{product["path"]}'
    image_url = f"https://cdn.cimri.io/market/600x600/-_{product['imageIds'][0]}.jpg"
    
    prices = []
    # check cache for the product prices
    cache_data = cache.retrieve_product_prices(product_id)
    if cache_data:
        print(f"Cache data found for the key {product_id} : {cache_data}")
        prices = cache_data
    else:
        offers = cimri.get_product_offers(product_url)
        if not offers:
            raise HTTPException(status_code=404, detail="No offer found for the product")
        for offer in offers:
            store_name = offer["store"]
            price = offer["price"]
            prices.append({"store": store_name, "price": price})
        # save prices to cache
        print(f"Saving to cache using the key {product_id} : {prices}")
        cache.store_product_prices(product_id, prices)

    price_response = PriceResponse(name=product_title, image=image_url, prices=prices)
    return price_response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)