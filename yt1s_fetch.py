import os
#os.system("pip install aiofiles httpx fake-agent")




import aiofiles, time, httpx, asyncio, sys
from FakeAgent import Fake_Agent
import aiofiles as aiof


def debug(text):
	with open("debug.txt", "w", encoding="utf8")as f:f.write(str(text))


_agent = Fake_Agent()

def get_headars():return {"User-Agent": _agent.random()}

ses = httpx.AsyncClient(timeout=9)
down_ses = httpx.AsyncClient(verify=False, timeout=4620)

async def fetch(url:str):
    if not url.lower().startswith("http"):url = "https://" + url
    d = {
        'q': url,
        'vt': 'home'}
    
    endpoint = "https://yt1s.com/api/ajaxSearch/index"
    
    try:
    	x = await ses.post(endpoint, data=d, headers=get_headars())
    	r = x.json()
    except httpx.ReadTimeout as e:
    	return {"ok":False, "message": "Read Timed out, please try again", "error": str(e)}
    except Exception as e:
    	r = x
    	with open("index.html", "w", encoding="utf8") as f:f.write(r.text)
    	return {"ok":False, "message": "Some Error Occurred", "error": str(e), "text": r.text}
    
   
		
    # Status of the response
    status = r.get("status")
    if status!="ok":
    	return {"ok":False, "message": "An Error Occurred.", "data": r}
    	
    	
    # Title of the video
    title = r.get("title")
    
    links = r.get("links")
    vid = r.get("vid")
    
    mp4s = links.get("mp4")
    mp4_data = {}
    for _, y in mp4s.items():
    	q_str = y.get("q")[:-1]
    	quality = int(q_str) if q_str.isdecimal() else None
    	if not quality:continue
    	
    	size = y.get("size")
    	k_url = y.get("k")
    	mp4_data[quality] = {
    		"size": size,
    		"k":  k_url,
    		"quality": quality,
    		"format":  "mp4"
    	}
    
    has_3gp = links.get("3gp")
    if has_3gp:gp3 = links.get("3gp").get("3gp@144p");_3gp = {
	    	"size": gp3.get("size"),
	    	"k": gp3.get("k"),
	    	"quality": "3gp",
	    	"format":  "3gp"}
	
    has_mp3 = links.get("mp3")
    if has_mp3:
	    mp3x = links.get("mp3").get("mp3128")
	    mp3 = {
	    	"size": mp3x.get("size"),
	    	"k": mp3x.get("k"),
	    	"quality": "mp3",
	    	"format":  "mp3"
	    }
    
    return {
    	"mp4": mp4_data,
    	"mp3": mp3 if has_mp3 else None,
    	"3gp": _3gp if has_3gp else None,
    	"vid": vid,
    	"title": title,
    	"ok": True
    }


async def get_download_url(vid:str, k:str):
	d = {"vid": vid, "k": k}
	endpoint = "https://yt1s.com/api/ajaxConvert/convert"
	
	try:
		r = (await ses.post(endpoint, data=d)).json()
	except httpx.ReadTimeout as e:
		return {"ok":False, "message": "Read Timed out, please try again", "error": str(e)}
		
	
	down_link = r.get("dlink")
	if not down_link:
		print(f"Recalling {vid} in 2 seconds")
		await asyncio.sleep(2)
		return get_download_url(vid, k)
	
	return {
		"ok": True,
		"dlink": down_link
	}
	
def get_the_video_id(url:str):
	url = url.replace('https://', '').replace('http://', '').split('/')[1]
	if '&list' in url:
		url = url[url.find("v=")+2: url.find('&list')]
		return url
	elif "watch?v=" in url:
		url = url[url.find("v=")+2:]
		return url
	
	return url


async def async_download(url, name="10110", fo="", m=None):
	try:
		async with down_ses.stream("GET", url) as r:
			if not fo:
				fo = r.headers["content-type"].split('/')[1]
			for x in " ~`|√π♪÷×{}£$℅^°=[]\\<>,.@#৳%&*-+()!\"':;/?":
				name = name.replace(x, '_')
			name = name.replace('___','_').replace('__','_')
			filename = f"{name}.{fo}"
			total = int(r.headers["content-length"])
			st = time.time()
			ft = time.time()
			async with aiofiles.open(filename, "wb") as file:
				async for chunk in r.aiter_bytes():
					await file.write(chunk)
					dnd = r.num_bytes_downloaded
					cu = time.time()
					
					if cu-st>=2:
						j = 1000**2
						a = f"<b>Downloaded {dnd/j:.2f} MB of {total/j:.2f} MB  @ {dnd/j/(cu-ft):.2f} MB/s</b>"
						if not m:
							print(a)
						if m:await m.edit_text(a)
						st = time.time()
		return {"ok":True, "message":" File has been downloaded", "filename": filename, "size": total, "time_taken": int(time.time()-ft)}
		
	
	
	except httpx.RemoteProtocolError as e:
		return {"ok":False, "message":"Server closed connection unexpectedly", "error": str(e)}
		
	except Exception as e:
		return {"ok":False, "message":"Some error occurred", "error": str(e)}


	





url = """

https://youtu.be/jZURhuJjMqs

""".strip()
print("Starting...")

async def main():
	x = await async_download("https://tgstreamdlbot.cf/AgADFw2057", "hello", "sql")
	f = x.get("filename")
	os.remove(f)
	return 
	x = await fetch(url)
	print(x)
	return 
	print(x.get("title"))
	
	d = x.get("mp4").get(480)
	print(f"The size is {d.get('size')}")
	y = await get_download_url(x.get("vid"), d.get('k'))
	y = y.get("dlink")
	debug(y)
	fo = d.get("format")
	
	print(await async_download(y, x.get("title"), fo))
	

if __name__ =="__main__":
	asyncio.run(main())




	
