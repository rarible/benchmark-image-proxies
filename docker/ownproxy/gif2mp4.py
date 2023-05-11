import subprocess, cv2, http.client, io
from PIL import Image
import numpy as np


def cmd_convert(in_img_path, out_img_path):
    retcode = subprocess.call(['ffmpeg', '-v', 'warning', '-y', '-i', in_img_path, '-pix_fmt', 'yuv420p', '-f', 'mp4', out_img_path])
    print(f'[ffmpeg exited with {retcode}]')


def cv_convert(im: Image, out_img_path: str):
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


def cv_from_file(img_file_path):
    ofile_path = f'/dev/shm/1.mp4'
    im = Image.open(img_file_path)
    cv_convert(im, ofile_path)


def cv_from_url(url):
    out_img_path = f'/dev/shm/1.mp4'
    scheme, _, host_port, uri = url.split('/', 3)
    if scheme.startswith('https'):
        c = http.client.HTTPSConnection(host_port)
    else:
        c = http.client.HTTPConnection(host_port)
    for _ in range(3):  # retry 3times
        try:
            c.request('GET', f'/{uri}')
            im = Image.open(io.BytesIO(c.getresponse().read()))
            cv_convert(im, out_img_path)
            break
        except http.client.CannotSendRequest as e:
            print('Error during getting the image from origin host: %s. Retrying..' % e)
