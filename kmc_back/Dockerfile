FROM python:3.7-alpine
WORKDIR /kmc_back
COPY req.txt /kmc_back/
RUN apk update &&  apk add --no-cache \
    postgresql-dev gcc python3-dev musl-dev py3-setuptools \
    tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
    libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
    libxcb-dev libpng-dev
RUN pip install --no-cache-dir -r req.txt
COPY . /kmc_back
EXPOSE 2271