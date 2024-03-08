from requests import Session
from aiohttp import TCPConnector
from aiohttp_client_cache import CachedSession, SQLiteBackend
from user_agent import generate_user_agent
from bs4 import BeautifulSoup
from helper import getVerid, DecodeLink
import requests, random

FETCH = 20

proxies = []
async def getProxies(max=10):
    proxyBox = []

    async def getProxy(proxy):
        if len(proxyBox) >= max:
            return
        try:
            print("Checking proxy", proxy)
            status = await get("https://ipinfo.io/json", proxy, resp=True)
            if not status[-1]:
                return
            print(proxy, status)
            if status:
                proxyBox.append(proxy)
        except Exception as er:
            print(proxy, er)

    content = requests.get(
        "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"
        #        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        #       "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=8000&country=all&ssl=all&anonymity=all"
    ).text.splitlines()
    random.shuffle(content)
    while content and len(proxyBox) < max:
        await asyncio.gather(*[getProxy(tsk) for tsk in content[:FETCH]])
        content = content[FETCH:]
    return proxyBox


import aiohttp, asyncio
from aiohttp import ClientSession



async def get(url, py=None, resp=False, json=False, headers={}):
    proxy = py
    if not proxy:
        if not proxies:
            proxies.extend(await getProxies(5))
        proxy =proxies[0]
    print(url, proxy)
    conn = aiohttp.TCPConnector(
        ssl=False
        #      ssl_context=ssl.create_default_context(cafile=certifi.where()),
    )
    async with ClientSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Sec-Ch-Ua-Platform": "Windows",
            **headers,
        },
        connector=conn,
    ) as ses:
        try:
            async with ses.get(
                url,  # cookies={d["name"]: d["value"] for d in Cookies}
               proxy=f"http://{proxy}",
                timeout=5,
            ) as res:
                if json:
                    return await res.json()
                if resp:
                    return res.status, await res.read()
                return await res.read()
        except Exception as er:
            if resp:
                return None, None
            print(er)
            try:
                if proxy in proxies:
                    proxies.remove(proxy)
                if not proxies:
                    proxies.extend(await getProxies(3))
                return await get(url)
            except:
                pass


import asyncio

loop = asyncio.get_event_loop()

proxies = loop.run_until_complete(getProxies())


class GoMovies:
    def __init__(self, base_url="https://gomovies.pe") -> None:
        self.base_url = base_url

    async def get(self, path, parse_json=False):
        return await get(f"{self.base_url}{path}",   json=parse_json)
        if not proxies:
            proxies.extend(await getProxies(5))
        proxy = proxies[0]
        try:
            async with CachedSession(
                self.base_url,
                headers={"User-Agent": generate_user_agent()},
                cache=SQLiteBackend("gomovies"),
                #                connector=TCPConnector(verify_ssl=False)
            ) as ses:
                async with ses.get(path, proxy=f"http://{proxy}") as res:
                    if parse_json:
                        return await res.json()
                    return await res.read()
        except Exception as er:
            print(er)
            try:
                del proxies[0]
            except:
                pass
            return await self.get(path, parse_json=parse_json)

    def _parseSlider(self, section):
        mViewedOut = []
        for box in section.find_all("a", "swiper-slide"):
            tags = {}
            status = box.find("div", "status").find_all("span")[1:]
            if status[0].text.isdigit():
                tags["year"] = status[0].text
            tags["rating"] = status[1].text
            tags["duration"] = status[2].text
            mViewedOut.append(
                {
                    "id": box.get("href"),
                    "title": box.find("h4").text.strip(),
                    "thumb": box.find("img").get("src"),
                    "tags": tags,
                }
            )
        return mViewedOut

    async def getHome(self):
        try:
            data = await self.get("/home")
            soup = BeautifulSoup(data, "html.parser")
            response = {
                "carousel": []
            }
            if soup.find("div", "swiper-wrapper"):
                response["carousel"] = [
                    {
                        "title": d.text.strip(),
                        "thumb": d.find("img").get("src"),
                        "id": d.get("href"),
                    }
                    for d in soup.find("div", "swiper-wrapper").find_all("a")
                    if d.find("img")
                ]
            mViewed = soup.find("section", id="most-viewed")

            response[mViewed.find("h2").text.strip()] = self._parseSlider(mViewed)

            for sec in soup.find_all("section")[1:]:
                slider = []
                for box in sec.find_all("div", "inner"):
                    slider.append(
                        {
                            "id": box.find("a", "poster").get("href"),
                            "title": box.find("div", "data").text.strip(),
                            "thumb": box.find("img").get("src"),
                        }
                    )
                response[sec.find("h2").text.strip()] = slider
            return response
        except Exception as er:
            try:
                del proxies[0]
            except:
                pass
            # print(er)
            return await self.getHome()

    async def getSources(
        self,
        id,
    ):
        data = await self.get(id)
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        watchId = soup.find("div", "watch-wrap").get("data-id")
        nVer = getVerid(watchId)
        soup = BeautifulSoup(
            (
                await self.get(
                    f"/ajax/episode/list/{watchId}?vrf={nVer}", parse_json=True
                )
            )["result"],
            "html.parser",
        )
        watchId = [d.get("data-id") for d in soup.find_all("a") if d.get("data-id")][0]
        nVer = getVerid(watchId)
        soup = BeautifulSoup(
            (
                await self.get(
                    f"/ajax/server/list/{watchId}?vrf={nVer}", parse_json=True
                )
            )["result"],
            "html.parser",
        )
        tags = {
            a.text.strip().lower(): a.get("data-link-id")
            for a in soup.find_all("span", "server")
        }
        Resp = {}
        for x, y in tags.items():
            vid = getVerid(y)
            print(y, vid)
            data = await self.get(f"/ajax/server/{y}?vrf={vid}", parse_json=True)
            Resp[x] = DecodeLink(data["result"]["url"])
        return Resp

    async def getEpisodes(self, id):
        print(217, id, type(id))
        data = await self.get(id)
        print(data)
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        watchId = soup.find("div", "watch-wrap").get("data-id")
        nVer = getVerid(watchId)
        resp = await self.get(
                    f"/ajax/episode/list/{watchId}?vrf={nVer}", parse_json=True
                )
        print(resp)
        soup = BeautifulSoup(
           resp["result"],
            "html.parser",
        )
        episodes = {}
        for div in soup.find_all("ul", "episodes"):
            episodes[div.get("data-season")] = [
                {"title": d.text.strip(), "id": d.get("href")}
                for d in div.find_all("a")
            ]
        return episodes

    async def getInfo(self, id):
        data = await self.get(id)
#        with open("out.html", "wb") as f:
#            f.write(data)
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        response = {
            "id": id,
            "title": soup.find("h1", "title").text.strip(),
            "thumb": soup.find("img", itemprop="image").get("src"),
            "rating": soup.find("span", itemprop="aggregateRating").get("data-score"),
            "description": soup.find("p").text.strip(),
            "meta": {},
            "suggestions": [
                {
                    "id": box.find("a", "poster").get("href"),
                    "title": box.find("div", "data").text.strip(),
                    "thumb": box.find("img").get("src"),
                }
                for box in soup.find("div", "swiper-wrapper").find_all("div", "inner")
            ],
        }
        for box in soup.find("div", "meta").find_all("div"):
            bs = box.find("div")
            if not bs:
                print(box)
                continue
            response["meta"][bs.text[:-1]] = (
                box.find("span") or box.find("a")
            ).text.strip()
        episodes = soup.find_all("ul", "episodes")

        epos = {}

        for ep in episodes:
            epos[ep.get("data-season")] = [
                {
                    "title": d.text.strip(),
                    "id": d.get("href"),
                    "episodeId": d.get("data-num"),
                }
                for d in ep.find_all("a")
            ]
        response["episodes"] = epos
        return response


# movie = GoMovies()
# import asyncio

#
#    movie.getHome()
# movie.getEpisodes("/tv/watch-the-big-bang-theory-jjq14")
#    ))
