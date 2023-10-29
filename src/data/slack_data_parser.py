import os
import json
import re
import csv

external_data_folder_path = "../../data/external"
output_file_path = "../../data/raw/sick.txt"

def clean_and_split_text(text):
    # Remove links
    text = re.sub(r"<http[s]?://[^>]+>", "", text)
    # Remove user mentions
    text = re.sub(r"<@[^>]+>", "", text)
    # Remove emojis
    text = re.sub(r":\S+:", "", text)
    # Remove symbols and special characters
    text = re.sub(r"[^\w\s.]", " ", text)
    # Split into sentences using periods and new lines
    sentences = re.split(r"[.!?]+\s*|\n", text)
    # Remove empty lines
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

with open(output_file_path, "w") as file:
    for filename in os.listdir(external_data_folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(external_data_folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "reactions" in item:
                            is_sick = any(reaction.get("name") == "pill" for reaction in item["reactions"])
                            if is_sick and "text" in item:
                                sentences = clean_and_split_text(item["text"])
                                for sentence in sentences:
                                    if len(sentence) >= 15:
                                        file.write(sentence + "\n")
