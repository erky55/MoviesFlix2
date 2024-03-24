import logging

logging.basicConfig(level=logging.INFO)

import requests
from swibots import *
from requests_cache import install_cache
from decouple import config

install_cache("moviesV3", expire_after=60 * 60 * 60)

BOT_TOKEN = config("BOT_TOKEN", default="")
TMDB_KEY = config("TMDB_KEY", default="")


def make_request(url):
    return requests.get(
        url,
        headers={
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_KEY}",
        },
    ).json()


app = Client(
    BOT_TOKEN,
    is_app=True,
    home_callback="Home|Movies",
)
app.set_bot_commands(
    [
        BotCommand("start", "Get start message", True),
        BotCommand("search", "Search Movies", channel=True),
        BotCommand("searchtv", "Search TV Shows", channel=True),
    ]
)


def getBottomBar(crt="Home"):
    return BottomBar(
        options=[
            BottomBarTile(
                d,
                selected=d == crt,
                callback_data=f"Home|{d}",
                icon=data["icon"],
                selection_icon=data["selected"],
                dark_icon=data["dark_icon"],
            )
            for d, data in {
                "Movies": {
                    "dark_icon": "https://f004.backblazeb2.com/file/switch-bucket/4db2a819-ea21-11ee-a3ca-d41b81d4a9f0.png",
                    "icon": "https://f004.backblazeb2.com/file/switch-bucket/5fb2cec7-ea21-11ee-af08-d41b81d4a9f0.png",
                    "selected": "https://f004.backblazeb2.com/file/switch-bucket/5d53df18-ea21-11ee-9ddb-d41b81d4a9f0.png",
                },
                "TV": {
                    "icon": "https://f004.backblazeb2.com/file/switch-bucket/5b241bd9-ea21-11ee-afc9-d41b81d4a9f0.png",
                    "dark_icon": "https://f004.backblazeb2.com/file/switch-bucket/52947af2-ea21-11ee-97b4-d41b81d4a9f0.png",
                    "selected": "https://f004.backblazeb2.com/file/switch-bucket/508de24f-ea21-11ee-bab0-d41b81d4a9f0.png",
                },
            }.items()
        ]
    )


def splitList(lis, n):
    res = []
    while lis:
        res.append(lis[:n])
        lis = lis[n:]
    return res


async def searchTag(m: Message, type, query, offset=0, from_callback=False):
    cq = query
    if not from_callback:
        s = await m.reply_text(f"🔎 Searching...")
    results = []
    wordL = len(query)
    while wordL and len(results) < 10:
        url = f"https://api.themoviedb.org/3/search/{type}?query={query.replace(' ', '+')}&include_adult=false&language=en-US&page=1"
        data = make_request(url)
        for res in data["results"]:
            if res not in results:
                results.append(res)
        query = query[:-1]
        wordL -= 1
    if not results:
        await s.edit_text(f"🔍 No results found!")
        return
    size = 8
    splitOut = splitList(results, size)
    splitt = splitOut[offset]
    message = f"""🍿 *Results for {cq}*\n👉 Total: {len(results)}"""
    bts = []
    mkup = [
        [InlineKeyboardButton(i["title"], callback_data=f"{type}|{i['id']}")]
        for i in splitt
    ]
    bts = []
    try:
        splitOut[offset - 1]
        bts.append(
            InlineKeyboardButton(
                "🔙 Previous", callback_data=f"sct|{type}|{query}|{offset-1}"
            )
        )
    except IndexError:
        pass
    try:
        splitOut[offset + 1]
        bts.append(
            InlineKeyboardButton(
                "Next ▶️", callback_data=f"sct|{type}|{query}|{offset+1}"
            )
        )
    except IndexError:
        pass
    if bts:
        mkup.append(bts)
    if from_callback:
        await m.edit_text(message, inline_markup=InlineMarkup(mkup))
    else:
        await m.reply_text(message, inline_markup=InlineMarkup(mkup))
        await s.delete()


@app.on_callback_query(regexp("sct"))
async def showCallback(ctx: BotContext[CallbackQueryEvent]):
    type, query, offset = ctx.event.callback_data.split("|")[1:]
    await searchTag(ctx.event.message, type, query, int(offset), from_callback=True)


@app.on_command("search")
async def onSearch(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    query = ctx.event.params
    if not query:
        await m.send(f"Please provide movie name to search!")
        return
    await searchTag(m, "movie", query)


@app.on_command("searchtv")
async def onSearch(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    query = ctx.event.params
    if not query:
        await m.send(f"Please provide tv name to search!")
        return
    await searchTag(m, "tv", query)


@app.on_command("start")
async def onPage(ctx: BotContext[CommandEvent]):
    await ctx.event.message.reply_text(
        f"Hi {ctx.event.message.user.name}!",
        inline_markup=InlineMarkup(
            [[InlineKeyboardButton("Open APP", callback_data="Home|Movies")]]
        ),
    )


@app.on_callback_query(regexp("askD"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    spl = ctx.event.callback_data.split("|")[1:]
    if len(spl) == 3:
        episodeId = int(spl[-1])
        print(spl)
        comps = [
            Text("Select Episode..", TextSize.SMALL),
            Dropdown(
                options=[
                    ListTile(
                        f"Episode {i}", callback_data=f"play|{spl[0]}|{spl[1]}|{i}"
                    )
                    for i in range(int(episodeId), 0, -1)
                ]
            ),
        ]
    else:
        ID = spl[0]
        url = f"https://api.themoviedb.org/3/tv/{ID}?append_to_response=external_ids&language=en-US"
        details = make_request(url)
        comps = [
            Text("Select Season..", TextSize.SMALL),
            Dropdown(
                "Select Season",
                options=[
                    ListTile(
                        d["name"],
                        callback_data=f"askD|{details['external_ids']['imdb_id']}|{d['season_number']}|{d['episode_count']}",
                    )
                    for d in details["seasons"][::-1]
                ],
            ),
        ]
    await ctx.event.answer(
        callback=AppPage(components=comps, screen=ScreenType.BOTTOM), new_page=True
    )


@app.on_callback_query(regexp("category"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    mId, name = ctx.event.callback_data.split("|")[1:]
    data = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={mId}"
    resp = make_request(data)

    await ctx.event.answer(
        callback=AppPage(
            components=[
                Grid(
                    name,
                    options=[
                        GridItem(
                            d["title"],
                            media=f"https://image.tmdb.org/t/p/w220_and_h330_face/{d['poster_path']}",
                            callback_data=f"movie|{d['id']}",
                        )
                        for d in resp["results"]
                    ],
                    expansion=Expansion.VERTICAL,
                )
            ]
        ),
        new_page=True,
    )


@app.on_callback_query(regexp("(movie|tv)"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    type, mId = ctx.event.callback_data.split("|")
    url = f"https://api.themoviedb.org/3/{type}/{mId}"
    details = make_request(url)
    comps = [
        Image(
            f"https://image.tmdb.org/t/p/w220_and_h330_face/{details['poster_path']}"
        ),
        Text(details.get("title") or details.get("name"), TextSize.SMALL),
        Button(
            Text("Play", color="#ffffff"),
            callback_data=(
                f"askD|{details['id']}"
                if type == "tv"
                else f"play|{details['imdb_id']}"
            ),
            color="#3ab590",
        ),
    ]
    if ov := details.get("overview"):
        comps.append(Text(f"*Description:*\n {ov}"))
    if ov := details.get("release_date"):
        comps.append(Text(f"*Released on:* {ov}"))
    comps.append(
        Text("🎥 *Genres:* " + " | ".join([d["name"] for d in details["genres"]]))
    )
    comps.append(
        Text(
            "🎥 *Languages:* "
            + " | ".join([d["name"] for d in details["spoken_languages"]])
        )
    )
    comps.append(
        Button(
            "Home",
            #            icon="https://f004.backblazeb2.com/file/switch-bucket/54b25c03-ea21-11ee-af4a-d41b81d4a9f0.png",
            callback_data=f"Home|{'Movies' if type == 'movie' else 'TV'}",
            variant="",
        )
    )
    await ctx.event.answer(callback=AppPage(components=comps), new_page=True)


@app.on_callback_query(regexp("play"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    spl = ctx.event.callback_data.split("|")[1:]
    if len(spl) == 1:
        mId = spl[-1]
        url = f"https://vidsrc.to/embed/movie/{mId}"
    else:
        url = f"https://vidsrc.to/embed/tv/{spl[0]}/{spl[1]}/{spl[2]}"
    print(url)
    comps = [Embed(url, landscape=True, view_ratio=100)]
    await ctx.event.answer(callback=AppPage(components=comps), new_page=True)


@app.on_callback_query(regexp("search"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    type = ctx.event.callback_data.split("|")[-1]
    comps = [
        SearchBar(
            "Search Movies.." if type == "movie" else "Search TV Shows..",
            callback_data=f"search|{type}",
        )
    ]
    if query := ctx.event.details.search_query:
        url = f"https://api.themoviedb.org/3/search/{type}?query={query.replace(' ', '+')}&include_adult=false&language=en-US&page=1"
        data = make_request(url)
        if not data["results"]:
            comps.append(Text(f"No Results found!"))
        comps.append(
            Grid(
                f"Results for {query}",
                options=[
                    GridItem(
                        d.get("title") or d.get("name"),
                        media=f"https://image.tmdb.org/t/p/w220_and_h330_face/{d['poster_path']}",
                        callback_data=(
                            ("tv" if type == "tv" else f"movie") + f"|{d['id']}"
                        ),
                    )
                    for d in data["results"]
                ],
                expansion=Expansion.VERTICAL,
            )
        )
    await ctx.event.answer(callback=AppPage(components=comps), new_page=not query)


@app.on_callback_query(regexp("Home"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    cPage = ctx.event.callback_data.split("|")[-1]
    comps = [
        SearchHolder(
            "Search Movies..",
            callback_data=f"search|{'movie' if cPage == 'Movies' else 'tv'}",
        )
    ]
    for genre in make_request("https://api.themoviedb.org/3/genre/movie/list")[
        "genres"
    ]:
        data = f"https://api.themoviedb.org/3/discover/{'movie' if cPage == 'Movies' else 'tv'}?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre['id']}"
        resp = make_request(data)
        if not resp["results"]:
            continue
        comps.append(
            Grid(
                genre["name"],
                horizontal=True,
                options=[
                    GridItem(
                        d.get("title") or d.get("name") or "",
                        media=f"https://image.tmdb.org/t/p/w220_and_h330_face/{d['poster_path']}",
                        callback_data=("movie" if cPage == "Movies" else "tv")
                        + f"|{d['id']}",
                    )
                    for d in resp["results"]
                ],
                right_image="https://f004.backblazeb2.com/file/switch-bucket/9c99cba4-a988-11ee-8ef4-d41b81d4a9ef.png",
                image_callback=f"category|{genre['id']}|{genre['name']}",
                expansion=Expansion.VERTICAL,
            )
        )
    page = AppPage(components=comps, bottom_bar=getBottomBar(cPage))
    await ctx.event.answer(callback=page)


app.run()
