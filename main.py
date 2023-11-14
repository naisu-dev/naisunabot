import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols
from sympy.plotting import plot
import enum
import discord
from discord import app_commands
from io import BytesIO, StringIO
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import requests
import pandas as pd
import random

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def fibonacci_calc(x: int, y:int, count:int) -> list:
    z = [x, y]
    for i in range(count):
        z.append(z[i] + z[i+1])
    return z

def aliquot_calc(x: int) -> list:
    z = [i for i in range(1, x+1) if x % i ==0]
    if len(z) == 2:
        return z
    else:
        answer = [x]
        while True:
            if len(z) == 2:
                answer.append(1)
                return answer
                break
            else:
                del z[len(z)-1]
                sumz = sum(z)
                z = [i for i in range(1, sum(z)+1) if sum(z) % i ==0]
                answer.append(sumz)
                if answer[len(answer)-1] == answer[len(answer)-2]:
                    return [x]
                    break

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Game(name=f"{len(client.guilds)}Servers"))

@tree.command(name="fibonacci", description="【naisumath】フィボナッチ数列を計算します")
async def fibonacci(interaction: discord.Interaction, start1: int, start2: int, count: int):
    await interaction.response.send_message(fibonacci_calc(start1, start2, count))

@tree.command(name="aliquot", description="【naisumath】アリコット数列を計算します")
async def qliquot(interaction: discord.Interaction, x: int):
    await interaction.response.send_message(aliquot_calc(x))

class modes(enum.Enum):
    fibonacci = "fibonacci"
    aliquot = "aliquot"
    formula = "formula"

class colors(enum.Enum):
    blue = ["tab:blue","#1f77b4"]
    orange = ["tab:orange","#ff7f0e"]
    green = ["tab:green","#2ca02c"]
    red = ["tab:red","#d62728"]
    purple = ["tab:purple","#9467bd"]
    brown = ["tab:brown","#8c564b"]
    pink = ["tab:pink","#e377c2"]
    gray = ["tab:gray","#7f7f7f"]
    olive = ["tab:olive","#bcbd22"]
    cyan = ["tab:cyan","#17becf"]

@tree.command(name="graph", description="【naisumath】グラフの作成")
async def graph(interaction: discord.Interaction, mode: modes, color: colors=None, start1: int=None, start2: int=None, count: int=None, x: int=None, formula: str=None):
    if mode == modes.fibonacci:
        if start1 is not None and start2 is not None and count is not None:
            if color is None:
                plt.clf()
                plt.plot(fibonacci_calc(start1, start2, count))
            else:
                plt.clf()
                plt.plot(fibonacci_calc(start1, start2, count), color=color.value[0])
            file = BytesIO()
            plt.savefig(file)
            file.seek(0)
            guild = client.get_guild(1169631010833580043)
            channel = guild.get_channel(1169631011366260818)
            message = await channel.send(file=discord.File(file, "file.png"))
            embed = discord.Embed(title="グラフ", color=discord.Colour.teal())
            embed.set_image(url=message.attachments[0].url)
            await interaction.response.send_message(embed=embed)
            await message.delete()
        else:
            await interaction.response.send_message("引数を正しく入力してください")
    elif mode == modes.aliquot:
        if x is not None:
            if color is None:
                plt.plot(aliquot_calc(x), color="tab:blue")
            else:
                plt.plot(aliquot_calc(x), color=color.value[0])
            file = BytesIO()
            plt.savefig(file)
            file.seek(0)
            guild = client.get_guild(1169631010833580043)
            channel = guild.get_channel(1169631011366260818)
            message = await channel.send(file=discord.File(file, "file.png"))
            embed = discord.Embed(title="グラフ", description=aliquot_calc(x), color=discord.Colour.teal())
            embed.set_image(url=message.attachments[0].url)
            await interaction.response.send_message(embed=embed)
            await message.delete()
        else:
            await interaction.response.send_message("引数を正しく入力してください")
    elif mode == modes.formula:
        if formula is not None:
            try:
                x = sp.Symbol("x")
                file = BytesIO()
                if color is None:
                    sp.plotting.plot(formula, (x,-8,8), ylim=(-8,8), legend=True, show=False).save(file)
                elif color is not None:
                    sp.plotting.plot(formula, (x,-8,8), ylim=(-8,8), legend=True, show=False, line_color=color.value[1]).save(file)
                file.seek(0)
                guild = client.get_guild(1169631010833580043)
                channel = guild.get_channel(1169631011366260818)
                message = await channel.send(file=discord.File(file, "file.png"))
                embed = discord.Embed(title="グラフ", description=formula, color=discord.Colour.teal())
                embed.set_image(url=message.attachments[0].url)
                await interaction.response.send_message(embed=embed)
            except:
                embed = discord.Embed(title="グラフ", description="エラー", color=discord.Colour.teal())
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("引数を正しく入力してください")

def number(number: int):
    try:
        ketsui_csv = pd.read_csv("https://raw.githubusercontent.com/naisu-dev/ketsui.py/main/ketsui.csv")
        number_sam = ketsui_csv[ketsui_csv["indexnumber"] == number]
        return [(number_sam["roomnumber"].iloc[-1]),str(number_sam["roomname"].iloc[-1]),str(number_sam["ketsuimessage"].iloc[-1])]
    except:
        return "numberの値がおかしい可能性があります"

@tree.command(name="ketsui", description="ケツイがみなぎった")
async def ketsui(interaction: discord.Interaction):
    embed = discord.Embed(title="ケツイ", color=discord.Color.teal())
    randomketsui = random.randrange(1, 26, 1)
    embed.add_field(name=number(randomketsui)[1], value=number(randomketsui)[2])
    await interaction.response.send_message(embed=embed)

class img_mode(enum.Enum):
    info = "info"
    gray = "gray"
    brighten = "brighten"
    darken = "darken"
    mosaic = "mosaic"
    invert = "invert"
    mirror = "mirror"
    flip = "flip"

@tree.command(name="img", description="【naisuimg】画像の編集")
async def img(interaction: discord.Interaction, attachment: discord.Attachment, mode: img_mode):
    try:
        im = Image.open(BytesIO(requests.get(attachment.url).content))
        im = im.convert("RGB")
        if mode == img_mode.info:
            pass
        elif mode == img_mode.gray:
            im = im.convert("LA")
        elif mode == img_mode.brighten:
            enhancer = ImageEnhance.Brightness(im)
            im = enhancer.enhance(1.5)
        elif mode == img_mode.darken:
            enhancer = ImageEnhance.Brightness(im)
            im = enhancer.enhance(0.5)
        elif mode == img_mode.mosaic :
            im = im.filter(ImageFilter.GaussianBlur(4))
            im.resize([x // 8 for x in im.size]).resize(im.size)
        elif mode == img_mode.invert:
            im = ImageOps.invert(im)
        elif mode == img_mode.mirror:
            im = ImageOps.mirror(im)
        elif mode == img_mode.flip:
            im = ImageOps.flip(im)
        file = BytesIO()
        im.save(file, format="png")
        file.seek(0)
        guild = client.get_guild(1169631010833580043)
        channel = guild.get_channel(1169631011366260818)
        message = await channel.send(file=discord.File(file, "file.png"))
        embed = discord.Embed(title=attachment.filename, color=discord.Colour.teal())
        embed.set_image(url=message.attachments[0].url)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("ファイル形式に対応しておりません")

@tree.command(name="whois", description="whois検索")
async def whwois(interaction: discord.Interaction, domain: str):
    res = requests.get("https://api.whoisproxy.info/whois/"+domain).text
    file = StringIO(res)
    await interaction.response.send_message(file=discord.File(file, "whois.txt"))

@tree.command(name="dig", description="dig検索")
async def whwois(interaction: discord.Interaction, domain: str):
    res = requests.get("https://api.whoisproxy.info/dig/"+domain).text
    file = StringIO(res)
    await interaction.response.send_message(file=discord.File(file, "dig.txt"))

@tree.command(name="postcode", description="郵便番号検索")
async def whwois(interaction: discord.Interaction, code: str):
    res = requests.get("https://zipcloud.ibsnet.co.jp/api/search?zipcode="+code).text
    file = StringIO(res)
    await interaction.response.send_message(file=discord.File(file, "postcode.txt"))

class commandall(enum.Enum):
    fibonacci = "fibonacci"
    aliquot = "aliquot"
    graph = "graph"
    img = "img"
    ketsui = "ketsui"
    whois = "whois"
    dig = "dig"
    postcode = "postcode"

@tree.command(name="help", description="ヘルプの表示")
async def help(interaction: discord.Interaction, command: commandall=None):
    if command is None:
        embed = discord.Embed(title="naisunabotヘルプ", description="詳しくは/help <コマンド名>で調べてください",color=discord.Colour.teal())
        embed.add_field(name="fibonacci", value="フィボナッチ数列を計算します", inline=False)
        embed.add_field(name="aliquot", value="アリコット数列を計算します", inline=False)
        embed.add_field(name="graph", value="グラフを作成します", inline=False)
        embed.add_field(name="img", value="簡単な画像編集をします", inline=False)
        embed.add_field(name="ketsui", value="...ケツイがみなぎった", inline=False)
        embed.add_field(name="whois", value="whois検索をします", inline=False)
        embed.add_field(name="dig", value="dig検索をします", inline=False)
        embed.add_field(name="postcode", value="郵便番号検索をします", inline=False)
        await interaction.response.send_message(embed=embed)
    elif command == commandall.fibonacci:
        embed = discord.Embed(title="fibonacciコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="フィボナッチ数列を計算します", inline=False)
        embed.add_field(name="<start1>", value="最初の数値を入力してください", inline=False)
        embed.add_field(name="<start2>", value="二番目の数値を入力してください", inline=False)
        embed.add_field(name="<count>", value="計算する個数を入力してください", inline=False)
        embed.add_field(name="例", value="/fibonacci start1:1 start2:1 count:10")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.aliquot:
        embed = discord.Embed(title="aliquotコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="アリコット数列を計算します", inline=False)
        embed.add_field(name="<x>", value="最初の数値を入力してください", inline=False)
        embed.add_field(name="例", value="/aliquot x:12", inline=False)
        await interaction.response.send_message(embed=embed)
    elif command == commandall.graph:
        embed = discord.Embed(title="graphコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="グラフを作成します", inline=False)
        embed.add_field(name="<mode>", value="グラフを作成するときの方法を入力してください", inline=False)
        embed.add_field(name="<color>（任意）", value="グラフを作るときの色を入力してください", inline=False)
        embed.add_field(name="<その他の引数>", value="グラフを作るときのデータを入力してください", inline=False)
        embed.add_field(name="例", value="/graph mode:aliquot color:blue x:12")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.img:
        embed = discord.Embed(title="imgコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="簡単な画像編集をします", inline=False)
        embed.add_field(name="<attachment>", value="編集前のファイルを指定してください", inline=False)
        embed.add_field(name="<mode>", value="編集する内容を入力してください", inline=False)
        embed.add_field(name="例", value="/img attachment:[添付ファイル] mode:darken")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.ketsui:
        embed = discord.Embed(title="ketsuiコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="ケツイがみなぎる", inline=False)
        embed.add_field(name="例？", value="/ketsui")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.whois:
        embed = discord.Embed(title="whoisコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="whois検索", inline=False)
        embed.add_field(name="<domain>", value="検索するドメインを入力してください", inline=False)
        embed.add_field(name="例", value="/whois domain:google.com")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.dig:
        embed = discord.Embed(title="digコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="dig検索", inline=False)
        embed.add_field(name="<domain>", value="検索するドメインを入力してください", inline=False)
        embed.add_field(name="例", value="/dig domain:google.com")
        await interaction.response.send_message(embed=embed)
    elif command == commandall.postcode:
        embed = discord.Embed(title="postcodeコマンドヘルプ", color=discord.Color.teal())
        embed.add_field(name="できること", value="郵便番号で検索", inline=False)
        embed.add_field(name="<code>", value="検索する番号を入力してください", inline=False)
        embed.add_field(name="例", value="/postcode code:111222333")
        await interaction.response.send_message(embed=embed)

@tree.command(name="admin-request", description="管理者限定コマンドです")
async def admin_request(interaction: discord.Interaction, url: str):
    if interaction.user.id == 874430259599142922:
        res = requests.get(url).text
        file = StringIO(res)
        await interaction.response.send_message(file=discord.File(file, "request.txt"))
    else:
        await interaction.response.send_message("権限がありません　このコマンドは管理者にしか使用できません")

import os

client.run(os.environ.get("TOKEN"))
