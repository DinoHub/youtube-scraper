import time
import argparse
import sys
import subprocess
import shutil
import pydub
from pathlib import Path
from util import make_video_url, make_basename, vtt2txt, autovtt2txt
import pandas as pd
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(
        description="Downloading videos with subtitle.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("lang", type=str, help="language code (ja, en, ...)")
    parser.add_argument(
        "sublist", type=str, help="filename of list of video IDs with subtitles"
    )
    parser.add_argument(
        "--outdir", type=str, default="video", help="dirname to save videos"
    )
    parser.add_argument(
        "--keeporg",
        action="store_true",
        default=False,
        help="keep original audio file.",
    )
    return parser.parse_args(sys.argv[1:])


def download_video(lang, fn_sub, outdir="video", wait_sec=10, keep_org=False):
    """
    Tips:
      If you want to download automatic subtitles instead of manual subtitles, please change as follows.
        1. replace "sub[sub["sub"]==True]" of for-loop with "sub[sub["auto"]==True]"
        2. replace "--write-sub" option of yt-dlp with "--write-auto-sub"
        3. replace vtt2txt() with autovtt2txt()
        4 (optional). change fn["vtt"] (path to save subtitle) to another.
    """

    sub = pd.read_csv(fn_sub)

    for videoid in tqdm(sub[sub["sub"] == True]["videoid"]):  # manual subtitle only
        fn = {}
        for k in ["wav", "wav16k", "vtt", "txt"]:
            fn[k] = Path(outdir) / lang / k / (make_basename(videoid) + "." + k[:3])
            fn[k].parent.mkdir(parents=True, exist_ok=True)

        print(fn["wav"])
        if not fn["wav16k"].exists() or not fn["txt"].exists():

            # download
            url = make_video_url(videoid)
            base = fn["wav"].parent.joinpath(fn["wav"].stem)
            # print("parent", fn["wav"].parent)
            # print("base:",base)
            cp = subprocess.run(
                f"yt-dlp --sub-lang {lang}.*,fil.* --extract-audio --audio-format wav --write-sub {url} -o {base}.\%\(ext\)s",
                shell=True,
                universal_newlines=True,
            )

            if cp.returncode != 0:
                print(f"Failed to download the video: url = {url}")
                continue

            import os

            # (1) move subtitles .vtt file from /wav to /vtt
            try:
                parent_dir = fn["wav"].parent
                for file in os.listdir(parent_dir):
                    if file.endswith(".vtt"):
                        os.rename(
                            os.path.join(parent_dir, file),
                            os.path.join(parent_dir, f"{videoid}.vtt"),
                        )

                shutil.move(f"{base}.vtt", fn["vtt"])
            except Exception as e:
                print(
                    f"Failed to rename subtitle file. The download may have failed: url = {url}, filename = {base}.{lang}.vtt, error = {e}"
                )
                continue

            # (2) vtt -> txt (reformatting)
            try:
                txt = vtt2txt(open(fn["vtt"], "r").readlines())
                # with open("train.vi", "a") as f:
                #     f.writelines([f'"{t[2]}"\n' for t in txt])
                with open(fn["txt"], "w") as f:
                    f.writelines([f'"{t[2]}"\n' for t in txt])

                # remove vtt file
                shutil.rmtree(fn["vtt"].parent)
                print(f"(2) removed dir: {fn['vtt'].parent}")

            except Exception as e:
                print(
                    f"Falied to convert subtitle file to txt file: url = {url}, filename = {fn['vtt']}, error = {e}"
                )
                continue

            # (3) wav -> wav16k (resampling to 16kHz, 1ch)
            try:
                wav = pydub.AudioSegment.from_file(fn["wav"], format="wav")
                wav = (
                    pydub.effects.normalize(wav, 5.0)
                    .set_frame_rate(16000)
                    .set_channels(1)
                )
                wav.export(fn["wav16k"], format="wav", bitrate="16k")
            except Exception as e:
                print(
                    f"Failed to normalize or resample downloaded audio: url = {url}, filename = {fn['wav']}, error = {e}"
                )
                continue

            # remove original wav
            if not keep_org:
                fn["wav"].unlink()
                shutil.rmtree(fn["wav"].parent)
                print(f"(3) removed dir: {fn['wav'].parent}")

            # wait
            if wait_sec > 0.01:
                time.sleep(wait_sec)

    return Path(outdir) / lang


if __name__ == "__main__":
    args = parse_args()
    dirname = download_video(
        args.lang, args.sublist, args.outdir, keep_org=args.keeporg
    )
    print(f"save {args.lang.upper()} videos to {dirname}.")
