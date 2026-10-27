from asyncio import Event, sleep

from utils.time import time
from utils.unifer import UniferContext

async def loading(activity: Event, *, context: UniferContext|None = None, console: bool = True): # Пассивное отписывание в чат и терминал раз в n секунд (полезно для долгих функций).
    loading = "Loading"
    stime = time("str:%H:%M:%S")
    message = None
    
    if context:
        message = await context.channel.send(loading)
    
    while not activity.is_set():
        
        if console:
            print(f"\r[{stime}–{time("str:%H:%M:%S")}] {loading}   ", end = "", flush = True)
        
        loading += "."
        
        await sleep(1)
        
        if len(loading) >= 11:
            loading  = "Loading"
        
        if message:
            await message.edit(content = loading)

    if message:
        await message.delete()
    print(end = "\n")