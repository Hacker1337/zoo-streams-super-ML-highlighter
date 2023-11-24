import os
import subprocess
import numpy as np
import yaml
from assess_stream import assess_stream
from os.path import join
import pandas as pd
import logging
from tqdm.auto import tqdm


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open('links.yaml', 'r') as file:
    config = yaml.safe_load(file)

streams = config["streams"]
print(streams)
# os.makedirs("data")  # create directory for photos. Exist not ok.


# assess streams
pdList = []
for stream, link in tqdm(streams.items(), desc="processing streams"):
    assess_stream(link, join("data", stream))
    df = pd.read_csv(join("data", stream, "assessment.csv"))
    pdList.append(df)

overall_df = pd.concat(pdList)

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

probabilities = softmax(overall_df["final_score"])
logger.info(f"max probability of a stream: {max(probabilities)}")

selected_id = np.random.choice(range(len(probabilities)), p=probabilities)
logger.info(f"probability of the selected streams: {probabilities}")
row = overall_df.iloc[selected_id]

selected_path = row["photos"]

possible_captions = pd.read_csv("captions.csv")
caption = np.random.choice(possible_captions["captions"])

# send message to telegram
subprocess.run(["python", "telegram_bot.py", selected_path, "../.env", "--caption", caption])