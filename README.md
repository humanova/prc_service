# PRC Service

This service accepts an image of a product and returns its price data from various online stores. 
- Product name is extracted from the image using EasyOCR. 
- The price data is then retrieved from Cimri.com and cached (for an hour) using Redis.
- To handle the bad OCR output, a Fuzzy Matching algorithm is applied to DuckDuckGo search results before querying the Cimri API.

[Mobile App](https://github.com/humanova/prc_app)

### Endpoints

POST /api/price HTTP/1.1

Content-Type: application/json
```
{
    "image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDA..."
}
```

Response:
```
{
    "name": "Eti 142 gr Hoşbeş Gofret",
    "image": "https://cdn.cimri.io/market/600x600/eti-142-gr-hosbes-gofret-_1428163.jpg",
    "query": "Eti 142 gr Hoşbeş Gofret",
    "prices": [
        {
            "store": "şok",
            "price": 13.25
        },
        {
            "store": "a101",
            "price": 14.00
        }
    ]
}
```
