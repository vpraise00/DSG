from pathlib import Path
from lxml import etree as ET
import pandas as pd

CONFIG = None

class Config:
    def __init__(self, input_file, output_file):
        self.input_file = Path(input_file).resolve()
        self.data_dir = self.input_file.parent
        self.output_path = self.data_dir / output_file
        self.mgeo_dir = self.data_dir / "MGeo"
        self.mgeo_link_set = None

        if (self.mgeo_dir / "link_set.json").exists():
            self.mgeo_link_set = pd.read_json(self.mgeo_dir / "link_set.json", encoding="utf-8")
        else:
            print("[warn] MGeo/link_set.json does not exist.")

        self.tree = ET.parse(self.input_file)
        self.root = self.tree.getroot()


a = 10