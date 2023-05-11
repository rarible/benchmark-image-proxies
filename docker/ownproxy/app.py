import asyncio, io, random
from aiohttp import web, ClientSession
# from concurrent.futures.process import ProcessPoolExecutor    # I get some bugs at freeing resources
from concurrent.futures.thread import ThreadPoolExecutor
from PIL import Image   # it releases GIL

MAX_MEDIA_SIZE = 100*1024*1024

# renderpool = ProcessPoolExecutor()
renderpool = ThreadPoolExecutor()

routes = web.RouteTableDef()

def worker(img: bytes, img_w: int, img_h: int) -> bytes:
    result = io.BytesIO()
    result_img = Image.open(io.BytesIO(img))
    result_img.thumbnail((img_w, img_h))
    result_img.save(result, result_img.format)

    return result.getvalue()


async def run_in_renderpool(fn, *args):
    global renderpool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(renderpool, fn, *args)  # wait and return result


@routes.get('/')
async def handler(request):
    res_img = b''
    async with ClientSession() as session:
        async with session.get(request.query['url']) as resp:
            if resp.status == 200 and int(resp.headers['Content-Length']) < MAX_MEDIA_SIZE:
                orig_img = await resp.read()
                res_img = await run_in_renderpool(worker, orig_img, int(request.query['img_w']), int(request.query['img_h']))

    return web.Response(body=res_img, status=resp.status, content_type='image/jpg')


@routes.get('/gif2mp4')
async def gif2mp4(request):
    async with ClientSession() as session:
        ifile_path = f'/dev/shm/{random.randint(0,10000000)}.gif'
        ofile_path = f'{ifile_path}.mp4'
        async with session.get(request.query['url']) as resp:
            if resp.status == 200 and int(resp.headers['Content-Length']) < MAX_MEDIA_SIZE:
                with open(ifile_path, 'wb') as ifile:
                    ifile.write(await resp.read())

                ffmpeg = await asyncio.create_subprocess_exec('ffmpeg', '-v', 'warning', '-i', ifile_path, '-pix_fmt', 'yuv420p', '-f', 'mp4', ofile_path)
                await ffmpeg.wait()
                print(f'[ffmpeg exited with {ffmpeg.returncode}]')

    return web.FileResponse(path=ofile_path, status=resp.status)


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=8000)
