
# Code Generator

A simple API for generate a qr code and bar code 


## Installation

clone this repository and install python 3.8 or highter, and install dependencies

```bash
pip install Pillow python-barcode qrcode fastapi requests "uvicorn[standard]"
```
    

## Usage

run this command to run the project:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 80
```

## Run in Docker

First install docker 

```bash
docker compose up -d
```




## API Reference

#### Documentation

you can go to on http://localhost:8080/docs for test

#### Generate a qr code

```bash
  POST /qr-code/generate
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `data` | `string` | **Required**. Your data |
| `color` | `string` | **Optional**. Color of your qr code [hex] (default: #000000)|
| `bg_color` | `string` | **Optional**. Color of the background [hex] (default: #ffffff) |
| `style_points` | `string` | **Optional**. style of the points [square/gapped_square/circle/rounded/vertical_bar/horizontal_bar] (default:square) |
| `image_url` | `string` | **Optional**. add an image in your qr code (default:empty) |

#### Generate a bar code

```bash
  POST /bar-code/generate
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `data` | `string` | **Required**. Your data |



## Tech Stack
<a href="https://www.python.org" target="_blank">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
</a>
<a href="https://www.docker.com/">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white">
</a>
<a href="https://fastapi.tiangolo.com/">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009485?style=for-the-badge&logo=fastapi&logoColor=white">
</a>


