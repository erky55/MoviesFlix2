import logging

logging.basicConfig(
    level=logging.INFO, handlers=[logging.FileHandler("out.log", encoding="utf8")]
)

from swibots import *
from gomovies import GoMovies
from decouple import config

 

movies = GoMovies()
BOT_TOKEN = config("BOT_TOKEN", default="")

app = Client(
    BOT_TOKEN
)

app.set_bot_commands(
    [
        BotCommand("start", "Get start message", True),
        BotCommand("search", "Search by commands", True),
    ]
)


@app.on_command("start")
async def onMes(ctx: BotContext[CommandEvent]):
    await ctx.event.message.reply_text(
        f"Hi, I am {ctx.user.name}!\n\nClick below button to open app!",
        inline_markup=InlineMarkup(
            [[InlineKeyboardButton("Open APP", callback_data="Home")]]
        ),
    )


@app.on_callback_query(regexp("season"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    season, mId = ctx.event.callback_data.split("|")[1:]
    print(season, mId)
    info = await movies.getInfo(mId)
    episodes = await movies.getEpisodes(mId)
    comps = [
        ListTile(
            thumb=info.get("thumb"),
            title=info.get("title"),
            description=info.get("description", "")[:40],
        ),
        Text(f"Season {season}", TextSize.SMALL),
    ]
    for keys in episodes[season][::-1]:
        comps.append(Button(keys["title"], callback_data=f"watch|{keys['id']}"))

    await ctx.event.answer(
        callback=AppPage(
            components=comps, screen=ScreenType.BOTTOM, show_continue=False
        ),
        new_page=True,
    )


@app.on_callback_query(regexp("watch"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    mId = ctx.event.callback_data.split("|")[-1]
    if not mId.startswith(("/movie/", "movie/")) and mId.count("/") == 2:
        info = await movies.getInfo(mId)
        episodes = await movies.getEpisodes(mId)
        await ctx.event.answer(
            callback=AppPage(
                components=[
                    ListTile(
                        thumb=info.get("thumb"),
                        title=info.get("title"),
                        description=info.get("description", "")[:40],
                    ),
                    Dropdown(
                        "Select Season",
                        options=[
                            ListItem(f"Season {i}", callback_data=f"season|{i}|{mId}")
                            for i in episodes
                        ],
                    ),
                ],
                screen=ScreenType.BOTTOM,
                #               show_continue=False
            ),
            new_page=True,
        )
        return
    info = await movies.getInfo(mId)
    print(info["meta"])
    try:
        sources = await movies.getSources(mId)
    except Exception as er:
        print(er)
        sources = {}
    if not sources:
        return await ctx.event.answer("Something went wrong!", show_alert=True)
    urls = list(sources.values())
    #    print(urls)
    await ctx.event.answer(
        callback=AppPage(
            components=[Embed(urls[-1], full_screen=True, landscape=True,
                             allow_navigation=False)]
        ),
        new_page=True,
    )


@app.on_callback_query(regexp("info"))
async def showMovie(ctx: BotContext[CallbackQueryEvent], movieId=None):
    mId = movieId or ctx.event.callback_data.split("|")[-1]
    info = await movies.getInfo(mId)

    comps = [Text(info["title"], TextSize.SMALL)]
    comps.extend(
        [
            Image(info["thumb"]),
            Text(info["description"]),
            Button("Watch Now", callback_data=f"watch|{mId}"),
        ]
    )
    if movieId:
        comps.append(Button("Home", callback_data="Home"))
    if info.get("meta"):
        for i, y in info["meta"].items():
            comps.append(Text(f"*{i}:* {y}"))
    if info.get("suggestions"):
        comps.append(
            Grid(
                "Suggested",
                options=[
                    GridItem(d["title"], d["thumb"], callback_data=f"info|{d['id']}")
                    for d in info["suggestions"]
                ],
                horizontal=True,
                expansion=Expansion.VERTICAL,
            )
        )
    await ctx.event.answer(callback=AppPage(components=comps), new_page=True)


@app.on_callback_query(regexp("Home"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    comps = [SearchHolder("Search Movies", callback_data="search")]
    home = await movies.getHome()
    if home.get("carousel"):
        comps.append(
            Carousel(
                [
                    Image(d["thumb"], callback_data=f"watch|{d['id']}")
                    for d in home["carousel"]
                ]
            )
        )
    for tag, movie in home.items():
        if tag == "carousel":
            continue
        comps.append(
            Grid(
                tag,
                options=[
                    GridItem(d["title"], d["thumb"], callback_data=f"info|{d['id']}")
                    for d in movie
                ],
                horizontal=True,
                expansion=Expansion.VERTICAL,
            )
        )
    await ctx.event.answer(callback=AppPage(components=comps))


def getBottomBar(selected="Home"):
    Pages = {
        "Home": {
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/0fc4a209-d4df-11ee-a93a-d41b81d4a9f0.png",
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/146e0ad9-d4df-11ee-bf40-d41b81d4a9f0.png",
            "select": "https://f004.backblazeb2.com/file/switch-bucket/1710119c-d4df-11ee-8ac4-d41b81d4a9f0.png",
        },
        "Hot": {
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/1c349296-d4df-11ee-92d8-d41b81d4a9f0.png",
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/1a2df42d-d4df-11ee-a06f-d41b81d4a9f0.png",
            "select": "https://f004.backblazeb2.com/file/switch-bucket/1e7d36c8-d4df-11ee-bd65-d41b81d4a9f0.png",
        },
    }
    tiles = []
    for title, data in Pages.items():
        tiles.append(
            BottomBarTile(
                title,
                callback_data=title,
                selected=selected == title,
                dark_icon=data["dark"],
                selection_icon=data["select"],
                icon=data["icon"],
            )
        )
    return BottomBar(
        tiles,  # theme_color="#c9bd0e"
    )


from bs4 import BeautifulSoup


@app.on_callback_query(regexp("search"))
async def Home(ctx: BotContext[CallbackQueryEvent]):
    comps = [SearchBar("Search Movies", callback_data="search")]
    query = ctx.event.details.search_query
    if query:
        soup = BeautifulSoup(
            (
                await movies.get(
                    f"/ajax/film/search?keyword={query.replace(' ', '+')}",
                    parse_json=True,
                )
            )["result"]["html"],
            "html.parser",
        )
        if soup.find_all("a"):
            comps.append(
                Grid(
                    f"Results for {query}",
                    options=[
                        GridItem(
                            d.text.strip(),
                            media=d.find("img").get("src"),
                            callback_data=f"info|{d.get('href')}",
                        )
                        for d in soup.find_all("a")
                        if d.find("img")
                    ],
                    expansion=Expansion.VERTICAL,
                )
            )
        else:
            comps.append(Text(f"No results found!", TextSize.SMALL))

    await ctx.event.answer(callback=AppPage(components=comps), new_page=not query)


def splitList(lis, n):
    res = []
    while lis:
        res.append(lis[:n])
        lis = lis[n:]
    return res


async def searchMovie(
    ctx: BotContext[CommandEvent], query: str, offset: int = 0, from_callback=False
):
    m = ctx.event.message
    if not from_callback:
        s = await m.reply_text("🔍 Searching Movies")
    wordLength = len(query)
    results = []
    while len(results) < 10 and wordLength:
        soup = BeautifulSoup(
            (
                await movies.get(
                    f"/ajax/film/search?keyword={query.replace(' ', '+')[:wordLength]}",
                    parse_json=True,
                )
            )["result"]["html"],
            "html.parser",
        )
        wordLength -= 1
        for movie in soup.find_all("a")[:-1]:
            data = {"title": movie.text.strip(), "id": movie.get("href")}
            if data not in results:
                results.append(data)
        wordLength -= 1
    size = 8
    splitOut = splitList(results, size)
    splitt = splitOut[offset]
    message = f"""🍿 *Total Results:* {len(results)}\n__{ctx.event.user.name}__ searched for __{query}__"""
    mkup = [
        [InlineKeyboardButton(i["title"], callback_data=f"splay|{i['id']}")]
        for i in splitt
    ]
    bts = []
    try:
        splitOut[offset - 1]
        bts.append(
            InlineKeyboardButton("🔙 Previous", callback_data=f"sct|{query}|{offset-1}")
        )
    except IndexError:
        pass
    try:
        splitOut[offset + 1]
        bts.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"sct|{query}|{offset+1}")
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


@app.on_callback_query(regexp("splay"))
async def showCallback(ctx: BotContext[CallbackQueryEvent]):
    movieID = ctx.event.callback_data.split("|")[-1]
    await showMovie(ctx, movieID)


@app.on_callback_query(regexp("sct"))
async def showCallback(ctx: BotContext[CallbackQueryEvent]):
    query, offset = ctx.event.callback_data.split("|")[1:]
    await searchMovie(ctx, query, int(offset), from_callback=True)


@app.on_command("search")
async def onSearch(ctx: BotContext[CommandEvent]):
    if not ctx.event.params:
        return await ctx.event.message.reply_text(f"🍿 Provide movie name to search!")
    await searchMovie(ctx, ctx.event.params)


app.run()
