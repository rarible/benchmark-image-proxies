import asyncio, aiohttp, io
from concurrent.futures.process import ProcessPoolExecutor
from PIL import Image
from fastapi import FastAPI, Response

app = FastAPI()

aioclient = aiohttp.ClientSession()

def worker(img: bytes, img_w: int, img_h: int) -> bytes:
    result = io.BytesIO()
    result_img = Image.open(io.BytesIO(img))
    result_img.thumbnail((img_w, img_h))
    result_img.save(result, format='JPEG')

    return result.getvalue()


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result


@app.get("/")
async def handler(url: str, img_w: int, img_h: int):
    res_img = b''
    async with aioclient.get(url) as resp:
        if resp.status == 200:
            orig_img = await resp.read()
            res_img = await run_in_process(worker, orig_img, img_w, img_h)

    return Response(content=res_img, status_code=resp.status, media_type='image/jpg')


@app.on_event("startup")
async def on_startup():
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()
