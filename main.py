from pyrogram import *
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)



import os
import sys
import time
import html
import httpx
import psutil
import shutil
import logging
import asyncio
import aiofiles


# Helpers
try:
	import yt1s_fetch
except ImportError as e:
	import Yt_Download.yt1s_fetch as yt1s_fetch




esml = lambda x:html.escape(str(""))
inMark = InlineKeyboardMarkup
inButton = InlineKeyboardButton

# Logging info
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)




def debug(text, filename:str=""):
	with open(f"debug{filename}.txt", "w", encoding="utf8")as f:f.write(str(text))






api_id = 10661093
api_hash = "ffa39e7d5836716e9a084233b828ae34"
key = "5877028651:AAFz5Fd_swxSZyqeCkY96hzlbkgL1J0E_C4"

bot = Client("Youtube1", api_id, api_hash, bot_token=key)


@bot.on_message(filters.command("start"))
async def start_command(c, m):
	debug(m)
	await m.reply("<b>Alive</b>")






# -------- Getting Server Details --------
def get_system_details():
    cpu = psutil.cpu_count()
    mem = dict(psutil.virtual_memory()._asdict())
    total, used, free = shutil.disk_usage("/")
    _ = 2**30
    all_m = f"{mem['total']/_:.2f}"
    use_m = f"{mem['used']/_:.2f}"
    all_d = f"{total / _:.2f}"
    use_d = f"{used / _:.2f}"
    left_d = f"{free/ _:.2f}"
    ug_d = esml(f"{used/total*100:.2f}")
    say = f"""\
CPU : <b>{cpu} Cores</b>
<b><u>       RAM      </u></b>
Total : <b>{all_m} GB</b>
Used  : <b>{use_m} GB</b>
Usage : <b>100/{esml(mem["percent"])} %</b>
<b><u>       DISK     </u></b>
Total : <b>{all_d} GB</b>
Used  : <b>{use_d} GB</b>
Free  : <b>{left_d} GB</b>
Usage : <b>100/{ug_d} %</b>
"""
    return say


@bot.on_message(filters.command("server"))
async def server_c(c,m):
    say = get_system_details()
    await m.reply(say)

@bot.on_message(filters.command(["down", "download"]))
async def custom_download(c, m):
	try:
		url = m.text.split()[1]
	except:
		await m.reply("<b>Please give url after /down</b>")
		return
	
	mes_id = str(m.id)
	
	x = await m.reply(f"""<b>Downloading...\nUrl: <a href="{url}">{url}</a></b>""")
	
	do = await yt1s_fetch.async_download(url, mes_id, m=x)
	await x.edit_text("<b>Downloaded. Now uploading.</b>")
	filename = do.get("filename")
	await c.send_document(m.chat.id, open(filename, "rb"))
	print(os.getcwd())
	os.remove(filename)
	
	
@bot.on_message(filters.command("ping"))
async def ping(c,m):
	s = time.time()
	x = await m.reply("<b>Checking...</b>")
	await x.edit_text(f"<b>Ping: {(time.time()-s)*1000:.2f} ms</b>")



@bot.on_message(filters.text)
async def handle_it(c, m):
	text = m.text
	
	if m.outgoing:
		return 
	if not text.lower().startswith("http"):
		await m.reply("<b>Maybe this isnt a link</b>")
		return 
	
	fetch = await yt1s_fetch.fetch(text)
	ok = fetch.get("ok")
	if not ok:
		await m.reply("<b>Something went wrong</b>")
		print(fetch)
		return

	
	mp4 = fetch.get("mp4")
	mp3 = fetch.get("mp3")
	_3gp = fetch.get("3gp")
	
	title = fetch.get("title")
	video_id = yt1s_fetch.get_the_video_id(text)
	
	buttons = []
	for x, y in mp4.items():
	   a = [inButton(f"{x}p @ {y.get('size')}", callback_data=f"video {video_id} {x}")]
	   k = len(buttons)-1
	   if buttons and len(buttons[k])==1:
	   	buttons[k] += a
	   else:
	   	buttons.append(a)
	
	a = []
	if _3gp:
		a.append(inButton("3gp 144p", callback_data=f"video {video_id} 3gp"))
	if mp3:
		a.append(inButton("Mp3 128kbps", callback_data=f"video {video_id} mp3"))
	if a:
		buttons.append(a)
	
	
	say = f"<b>{title}</b>\n<i>Select desired format</i>"
	
	buttons = inMark(buttons)
	
	await m.reply(say, reply_markup=buttons)
	



@bot.on_callback_query()
async def answer(c:Client, cq):
    data = cq.data
    chat_id = cq.from_user.id
    mes_id = cq.message.id

    async def edit_text(text):
    	await cq.message.edit_text(str(text))
    
    
    # debug(cq)
    
    if data.startswith("video"):
    	data = data.split()
    	quality = data[2]
    	video_id = data[1]
    	
    	await cq.answer(
        f"{quality}p Selected",
        show_alert=False)
        
    	url = f"https://youtube.com/watch?v={video_id}"
    	await edit_text("<b>Processing...</b>")
    	for _ in range(5):
    		avails = await yt1s_fetch.fetch(url)
    		if avails.get("ok"):break
    		await asyncio.sleep(1)
    	else:
    		await edit_text("<b>Failed to fetch data of the video.\nPlease try again after a moment or report to @Roboter403</b>")
    		return 
    	
    	vid = avails.get("vid")
    	title = avails.get("title")
    	if quality in "1080 720 480 360 240 144".split():
    		k = avails.get("mp4").get(int(quality)).get('k')
    		fo = "mp4"
    	
    	else:
    		k = avails.get(quality).get('k')
    		fo = quality
    	
    	for _ in range(5):
    		dlink = await yt1s_fetch.get_download_url(vid, k)
    		if dlink.get("ok"):break
    		await asyncio.sleep(1)
    	else:
    		await edit_text("<b>Failed to retrieve download link of the video.\nPlease try again after a moment or report to @Roboter403</b>")
    		return 
    	
    	
    	dlink = dlink.get("dlink")
    	
    	
    	for _ in range(3):
    		got = await yt1s_fetch.async_download(dlink, str(mes_id), fo, cq.message)
    		ok = got.get("ok")
    		if not ok:continue
    		if int(got.get("size"))>0:break
    		await asyncio.sleep(1)
    	else:
    		await edit_text("<b>Failed to download the video.\nPlease try again after a moment or report to @Roboter403</b>")
    		return 
    	
    	x = await edit_text(f"<b>Downloaded. Now uploading to Telegram.\nTime taken: {got.get('time_taken')} s</b>")
    	print("Downloaded the file for", chat_id, title)
    	
    	filename = got.get("filename")
    	
    	s = time.time()
    	await c.send_document(chat_id, open(filename, "rb"), caption=title, file_name = f"{title}.{fo}")
    	os.remove(filename)
    	await x.edit_text("<b>Downloaded in <i>{got.get('time_taken')} s</i>.\nUploaded in <i>{time.time()-s}</i> s</b>")
    		
    
    # await c.send_message(chat_id, data)














def run_main():
	bot.run()

if __name__=="__main__":
	run_main()
