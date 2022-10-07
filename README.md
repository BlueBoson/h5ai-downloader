# h5ai-downloader

## Quik Start

h5ai-dl is a script for downloading files from h5ai-based website.

```bash
pip install -r requirements.txt
python h5ai-dl.py <target_url>
```

This will create a folder named `target_url` and download files recursively into it.

Tested on [https://vcb-s.nmm-hd.org/](https://vcb-s.nmm-hd.org/)

## Usage

```
usage: h5ai-dl.py [-h] [-w WORKERS] [-o OUTPUT] [--no-dir] [-t] [-s] [--overwrite] [-b BLOCK] url

positional arguments:
  url                   URL to h5ai directory (with or without http(s):// both supported)

options:
  -h, --help            show this help message and exit
  -w WORKERS, --workers WORKERS
                        Number of workers
  -o OUTPUT, --output OUTPUT
                        Output directory
  --no-dir              Do not create a seperate directory
  -t, --test            Only print files
  -s, --ssl             Force to use SSL
  --overwrite           Overwrite existing files
  -b BLOCK, --block BLOCK
                        Block size
```
