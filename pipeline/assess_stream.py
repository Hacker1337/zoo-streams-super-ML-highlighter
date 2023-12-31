from tqdm import tqdm
import yaml
from downloader import download_frames_from_video
import os
from gradio_client import Client
import json
import pandas as pd
import shutil

import argparse


prompt = "aminal"   # prompt for text model


def assess_stream(stream_link, out_dir):
    result_dict = {}

    # Download images
    with open("downloader_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)  # remove existing photos and assessment results
    os.makedirs(out_dir)
    download_frames_from_video(
        stream_link, out_dir, every_nth=config["every_nth"], amount=config["n_photos"], verbose=True)
    # Segmenting photos

    client = Client("https://waleko-segmentanythingxgroundingdino.hf.space/")

    result_dict["photos"] = [ os.path.join(out_dir, img) for img in os.listdir(out_dir)]
    result_dict["seg_predictions"] = []

    for img in tqdm(result_dict["photos"], desc="Segmenting photos", leave=False):
        result_dict["seg_predictions"].append(client.predict(
            # str representing filepath or URL to image in 'Upload Image' Image component
            img,
            prompt,  # str representing string value in 'Object to Detect' Textbox component
            api_name="/predict"
        ))
    # Assessing photos
    from image_assessment import model_api
    from PIL import Image

    model_api_path = "./image_assessment"

    result_dict["img_score"] = []
    result_dict["subimg_scores"] = []
    photo_sizes = []
    for i in range(len(result_dict["photos"])):

        img = result_dict["photos"][i]
        im = Image.open(img)
        width, height = im.size
        photo_sizes.append(width*height)

        img_score, _ = model_api.predict(img, model_api_path)
        result_dict["img_score"].append(img_score)

        res_path = result_dict["seg_predictions"][i][1]
        files = []
        for root, dirs, f in os.walk(res_path):
            for file in f:
                if file.endswith(".jpeg"):
                    files.append(os.path.join(root, file))
        print(files)
        sub_scores = []
        for file in files:
            sub_score, _ = model_api.predict(file, model_api_path)
            sub_scores.append(sub_score)
        result_dict["subimg_scores"].append(sub_scores)

    # animal fraction computing

    fractions = []
    for i in range(len(result_dict["photos"])):
        json_path = result_dict["seg_predictions"][i][0]
        # read json file
        with open(json_path, 'r') as f:
            meta_info = json.load(f)

        print(meta_info)
        fract = 0
        for obj in meta_info["objects"]:
            area = abs((obj["box"][0] - obj["box"][1])
                       * (obj["box"][2] - obj["box"][3]))

            fract += obj["dino_score"]*area/photo_sizes[i]
        fractions.append(fract)
    result_dict["fractions"] = fractions

    df = pd.DataFrame(result_dict)
    filtered = df[df["subimg_scores"].apply(len) > 0].copy()    # remove images with no subimages
    filtered["avg_subimg_score"] = filtered["subimg_scores"].apply(
        lambda x: sum(x)/len(x))
    print(filtered)
    filtered["final_score"] = filtered["img_score"] + \
        filtered["fractions"]*20 + filtered["avg_subimg_score"]
    filtered.sort_values(by="final_score", ascending=False)

    filtered.to_csv(os.path.join(out_dir, "assessment.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream_link", required=True, type=str, help="link to youtube stream or rtmp link",)
    parser.add_argument("--out_dir", required=True, type=str, help="path to dir for images and evaluation csv",)

    args = parser.parse_args()

    assess_stream(args.stream_link, args.out_dir)