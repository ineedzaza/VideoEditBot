import discord
from discord.ext import commands
import subprocess
import os
import random

# Bot setup
bot = commands.Bot(command_prefix="veb ")

TEMP_DIR = "./temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def run_ffmpeg(input_path, output_path, vf_filters=[], af_filters=[]):
    vf = ",".join(vf_filters) if vf_filters else "null"
    af = ",".join(af_filters) if af_filters else None

    command = ["ffmpeg", "-i", input_path]

    if vf_filters:
        command += ["-vf", vf]

    if af_filters:
        command += ["-af", af]

    command += ["-c:a", "aac", "-c:v", "libx264", output_path]
    return subprocess.run(command)

@bot.command()
async def veb(ctx,
              speed: float = 1.0,
              wave: int = 0,
              wav: int = 0,
              waveamount: int = 0,
              wava: int = 0,
              wavestrength: int = 0,
              wavs: int = 0,
              fisheye: bool = False,
              v360: bool = False,
              pitch: int = 0,
              tremolo: int = 0,
              datamosh: bool = False,
              ricecake: bool = False,
              shake: int = 0,
              geq: int = 0,
              hue_value: int = 0,
              saturation: int = 100,
              acid: int = 0,
              hflip: bool = False,
              vflip: bool = False,
              invert: bool = False,
              hmirror: bool = False,
              vmirror: bool = False,
              bgr: bool = False,
              swapuv: bool = False,
              random_effect: bool = False):

    if not ctx.message.attachments:
        await ctx.send("Please attach a video!")
        return

    video = ctx.message.attachments[0]
    input_path = os.path.join(TEMP_DIR, video.filename)
    output_path = os.path.join(TEMP_DIR, f"processed_{video.filename}")
    await video.save(input_path)

    vf_filters = []
    af_filters = []

    # Video filters
    if hflip: vf_filters.append("hflip")
    if vflip: vf_filters.append("vflip")
    if invert: vf_filters.append("negate")
    if hmirror: vf_filters.append("hflip")  # example
    if vmirror: vf_filters.append("vflip")  # example
    if bgr: vf_filters.append("swapuv")     # approximate BGR swap
    if swapuv: vf_filters.append("swapuv")
    if hue_value != 0 or saturation != 100: vf_filters.append(f"hue=h={hue_value}:s={saturation}")
    if wave > 0 or wav > 0 or waveamount > 0 or wava > 0 or wavestrength > 0 or wavs > 0:
        vf_filters.append(f"geq='r=clip(X+{wave+wav+waveamount+wava},0,255):g=clip(Y+{wavestrength+wavs},0,255):b=clip(X+{wave},0,255)'")
    if fisheye: vf_filters.append("lenscorrection")
    if v360: vf_filters.append("v360")
    if datamosh: vf_filters.append("framestep=2")  # simple datamosh approximation
    if ricecake: vf_filters.append("tblend=all_mode=average")  # simple ricecake effect
    if shake > 0: vf_filters.append(f"translate=x='sin(n/{shake})*{shake}':y='cos(n/{shake})*{shake}'")
    if geq > 0: vf_filters.append(f"geq='r={geq}:g={geq}:b={geq}'")
    if acid > 0: vf_filters.append("chromashift")

    # Audio filters
    if speed != 1.0: af_filters.append(f"atempo={speed}")
    if pitch != 0: af_filters.append(f"asetrate=44100*2^{pitch/12},aresample=44100")
    if tremolo > 0: af_filters.append(f"tremolo=f={tremolo}")
    if random_effect: vf_filters.append(random.choice(["negate","hflip","vflip","swapuv"]))

    # Run FFmpeg
    process = run_ffmpeg(input_path, output_path, vf_filters, af_filters)

    if process.returncode == 0:
        await ctx.send(file=discord.File(output_path))
        os.remove(input_path)
        os.remove(output_path)
    else:
        await ctx.send("Failed to process video.")

bot.run("YOUR_BOT_TOKEN")
