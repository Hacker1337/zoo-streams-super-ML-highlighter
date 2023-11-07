import cv2
import argparse
import os
from vidgear.gears import CamGear


def create_dir_if_not_exists(path):
    os.makedirs(path, exist_ok=True)
    if not os.path.isdir(path):
        raise FileExistsError(f"{path} is not a directory!")


def download_frames_from_video(source, destination, every_nth, amount, verbose=True):
    if source.startswith("rtmp://"):
        stream = CamGear(
            source=source,
            logging=verbose
        )
    else:
        stream = CamGear(
            source=source,
            stream_mode=True,
            time_delay=1,
            logging=verbose
        ).start()

    currentframe = 0
    while currentframe <= every_nth * (amount - 1):
        frame = stream.read()
        if frame is None:
            break
        if currentframe % every_nth == 0:
            name = destination + "/frames" + str(currentframe) + ".jpg"
            cv2.imwrite(name, frame)
        currentframe += 1

    stream.stop()


parser = argparse.ArgumentParser(
    prog='LinksToFrames',
    description='Accepts txt file with list of links to videos and dirs, produces frames of the videos to dirs')

parser.add_argument("--file", required=True, type=str, help="Path to the file with links and dirs")
parser.add_argument("--nth", required=False, type=int, default=6, help="Take every nth frame")
parser.add_argument("--amount", required=False, type=int, default=15, help="Amount of frames to take")

if __name__ == "__main__":
    args = parser.parse_args()
    filepath = args.file
    with open(filepath, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line[0] == ';':
            print(f"Skipping line {line} as a comment")
            continue
        link, path_to_dir = line.strip().split(";")
        create_dir_if_not_exists(path_to_dir)
        print(f"Started downloading {link} to {path_to_dir}!")
        download_frames_from_video(link, path_to_dir, args.nth, args.amount)
        print(f"Download complete!")

    # Also create dir if not exist
    # TODO: youtube-streams look-back
    # download_frames_from_video(TEST_LINK, REL_SAVE_PATH, TAKE_EVERY_TH, AMOUNT)
