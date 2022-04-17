import asyncio, io
from aiohttp import web, ClientSession
# from concurrent.futures.process import ProcessPoolExecutor    # I get some bugs at freeing resources
from concurrent.futures.thread import ThreadPoolExecutor
from PIL import Image   # it releases GIL

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
            if resp.status == 200:
                orig_img = await resp.read()
                res_img = await run_in_renderpool(worker, orig_img, int(request.query['img_w']), int(request.query['img_h']))

    return web.Response(body=res_img, status=resp.status, content_type='image/jpg')


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=8000)
