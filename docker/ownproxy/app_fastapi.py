# Pillow отпускает GIL внутри, поэтому треды скейлятся по ядрам. Удивительно, но эта имплементация на ~2% быстрее чем асинхронная
import io, http.client
from PIL import Image
from fastapi import FastAPI, Response

app = FastAPI()

def worker(img: bytes, img_w: int, img_h: int) -> bytes:
    result = io.BytesIO()
    result_img = Image.open(io.BytesIO(img))
    result_img.thumbnail((img_w, img_h))
    result_img.save(result, result_img.format)

    return result.getvalue()


@app.get("/")
def handler(url: str, img_w: int, img_h: int):
    res_img = None
    scheme, _, host_port, uri = url.split('/', 3)
    if scheme.startswith('https'):
        c = http.client.HTTPSConnection(host_port)
    else:
        c = http.client.HTTPConnection(host_port)
    for _ in range(3):  # retry 3times
        try:
            c.request('GET', f'/{uri}')
            res_img = worker(c.getresponse().read(), img_w, img_h)
            break
        except http.client.CannotSendRequest as e:
            print('Error during getting the image from origin host: %s. Retrying..' % e)
    c.close()

    return Response(content=res_img, media_type='image/jpg')
