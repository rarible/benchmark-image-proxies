import asyncio, io
from aiohttp import web, ClientSession
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import shared_memory
from PIL import Image

renderpool = ThreadPoolExecutor()

routes = web.RouteTableDef()

def worker(shm_name, img_w: int, img_h: int) -> bytes:
    shm = shared_memory.SharedMemory(name=shm_name)
    result = io.BytesIO()
    result_img = Image.open(io.BytesIO(shm.buf))
    result_img.thumbnail((img_w, img_h))
    result_img.save(result, result_img.format)
    shm.close()
    result_img.close()

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
            if resp.status == 200:
                shm = shared_memory.SharedMemory(create=True, size=int(resp.headers['Content-Length']))
                # здесь всетаки копирование. aiohttp сейчас не имеет метода чтения сразу в буффер readinto()
                shm.buf[:] = await resp.read()
                res_img = await run_in_renderpool(worker, shm.name, int(request.query['img_w']), int(request.query['img_h']))
                shm.unlink()

    return web.Response(body=res_img, status=resp.status, content_type='image/jpg')


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=8000)
