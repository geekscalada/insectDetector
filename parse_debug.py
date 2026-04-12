import os
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

min_a = config['detector']['min_area']
max_a = config['detector']['max_area']

print(f"min_area: {min_a}, max_area: {max_a}")
