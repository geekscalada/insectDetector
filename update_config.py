import yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

config['detector']['min_area'] = 800
config['detector']['mog2_var_threshold'] = 32
config['detector']['morph_kernel_size'] = 5

with open("config.yaml", "w") as f:
    yaml.dump(config, f, sort_keys=False)

