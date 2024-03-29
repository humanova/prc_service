import base64

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

import cimri
from ocr import OCR
import cache


app = FastAPI()
ocr = OCR()

class PriceResponse(BaseModel):
    name: str
    image: str
    query: str
    prices: List[dict]

class PriceRequest(BaseModel):
    image: Optional[str] = None
    text: Optional[str] = None

@app.post("/api/price", response_model=PriceResponse)
async def get_price(price_req: PriceRequest):
    if not price_req.image and not price_req.text:
        raise HTTPException(status_code=400, detail="No text or image provided")
    
    query = str()
    if price_req.image:
        image_data = base64.b64decode(price_req.image)
        ocr_text = ocr.perform_ocr(image_data)
        print(f"OCR result : {ocr_text}")
        # to handle bad ocr results, use a search result from DDG 
        search_result_titles = cimri.get_duckduckgo_search_results(ocr_text)
        print(search_result_titles)
        query = search_result_titles[0]
    else:
        query = price_req.text
        print(f"request query {query}")
    
    # send suggestion request
    cimri_data = cimri.get_search_suggestions(query, limit=5)
    if not cimri_data or len(cimri_data["products"]) == 0:
        raise HTTPException(status_code=404, detail="No product found")
    
    product = cimri_data["products"][0]
    product_id = product["id"]
    product_title = product["title"]
    product_url = f'https://www.cimri.com{product["path"]}'
    image_url = f"https://cdn.cimri.io/market/600x600/-_{product['imageIds'][0]}.jpg"
    
    prices = cache.retrieve_product_prices(product_id)
    if not prices:
        offers = cimri.get_product_offers(product_url)
        if not offers:
            raise HTTPException(status_code=404, detail="No offer found for the product")
        prices = [{"store": offer["store"], "price": offer["price"]} for offer in offers]
        cache.store_product_prices(product_id, prices)
        print(f"Saving to cache using the key {product_id} : {prices}")
    else:
        print(f"Cache data found for the key {product_id} : {prices}")

    price_response = PriceResponse(name=product_title, image=image_url, query=query, prices=prices)
    return price_response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)