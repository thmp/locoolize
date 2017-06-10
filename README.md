# Locoolize API

## `[GET] /posts` Retrieve nearby posts

Query Parameters
- `lat` (*required*) latitude
- `long` (*required*) longitude

```
{
  "author": "Thomas",
  "latitude": 0.0,
  "longitude": 0.0,
  "message": "First post",
  "photo_url": "3077f6b411aefedcdd309f21b859b487.jpg"
}
```

## `[POST] /posts` Create photo post

Multipart form data
Post parameters
- `latitude` (float, *required*) latitude
- `longitude` (float, *required*) latitude
- `message` (string, *optional*) post message

File upload with key file