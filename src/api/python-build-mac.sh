#!/bin/bash 
pipenv run pyinstaller --distpath ../main/static/api_dist swatplus_rest_api.py --noconfirm -D
pipenv run pyinstaller --distpath ../main/static/api_dist swatplus_api.py --noconfirm -D