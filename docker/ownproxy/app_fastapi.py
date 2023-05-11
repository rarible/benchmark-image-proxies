# Pillow отпускает GIL внутри, поэтому треды скейлятся по ядрам. Удивительно, но эта имплементация на ~2% быстрее чем асинхронная
import io, http.client, subprocess, random
from PIL import Image
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse

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


@app.get('/gif2mp4')
def gif2mp4(url: str):
    ifile_path = f'/dev/shm/{random.randint(0,10000000)}.gif'
    ofile_path = f'{ifile_path}.mp4'
    scheme, _, host_port, uri = url.split('/', 3)
    if scheme.startswith('https'):
        c = http.client.HTTPSConnection(host_port)
    else:
        c = http.client.HTTPConnection(host_port)
    for _ in range(3):  # retry 3times
        try:
            c.request('GET', f'/{uri}')
            with open(ifile_path, 'wb') as ifile:
                ifile.write(c.getresponse().read())
            retcode = subprocess.call(['ffmpeg', '-v', 'warning', '-i', ifile_path, '-crf', '32', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-f', 'mp4', ofile_path])
            print(f'[ffmpeg exited with {retcode}]')
            break
        except http.client.CannotSendRequest as e:
            print('Error during getting the image from origin host: %s. Retrying..' % e)

    return FileResponse(path=ofile_path)


import cv2
import numpy as np
@app.get('/gif2mp4_')
def gif2mp4_(url: str):
    out_img_path = f'/dev/shm/{random.randint(0,10000000)}.mp4'
    scheme, _, host_port, uri = url.split('/', 3)
    if scheme.startswith('https'):
        c = http.client.HTTPSConnection(host_port)
    else:
        c = http.client.HTTPConnection(host_port)
    for _ in range(3):  # retry 3times
        try:
            c.request('GET', f'/{uri}')
            im = Image.open(io.BytesIO(c.getresponse().read()))
            im.seek(1)
            fps = 1 / im.info['duration'] * 1000
            im.seek(0)
            video = cv2.VideoWriter(out_img_path, cv2.VideoWriter_fourcc(*'avc1'), fps, im.size)
            try:
                while True:
                    video.write(np.array(im.convert('RGB'), copy=False, dtype=np.uint8))
                    im.seek(im.tell() + 1)
            except EOFError:
                pass
            video.release()
            break
        except http.client.CannotSendRequest as e:
            print('Error during getting the image from origin host: %s. Retrying..' % e)

    return FileResponse(path=out_img_path)
