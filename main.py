# Copyright (c) 2023-2024 Westfall Inc.
#
# This file is part of Windcaller.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, and can be found in the file NOTICE inside this
# git repository.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

## This script downloads and tarballs all images in the containers.txt file.
# Best for bulk downloading all images


import docker
from rich.progress import Progress

tasks = {}

# Show task progress (red for download, green for extract)
def show_progress(line, progress):
    if line['status'] == 'Downloading':
        id = f'[red][Download {line["id"]}]'
    elif line['status'] == 'Extracting':
        id = f'[green][Extract  {line["id"]}]'
    else:
        # skip other statuses
        return

    if id not in tasks.keys():
        tasks[id] = progress.add_task(f"{id}", total=line['progressDetail']['total'])
    else:
        progress.update(tasks[id], completed=line['progressDetail']['current'])

def image_pull(name, tag, platform):
    image_name = "".join([name, ":", tag])
    print(f'Pulling image: {image_name}')
    with Progress() as progress:
        client = docker.from_env()
        resp = client.api.pull(name, tag, platform=platform, stream=True, decode=True)
        for line in resp:
            show_progress(line, progress)

if __name__ == '__main__':
    # Pull a large image
    platform = 'linux/arm64/v8'
    with open('containers.txt','r') as f:
        data = f.readlines()

    for container in data:
        if ":" in container:
            IMAGE_NAME = container.split(":")[0]
            IMAGE_TAG = container.split(":")[1].replace("\n","")
        else:
            IMAGE_NAME = container
            IMAGE_TAG = "latest"
        image = "".join([IMAGE_NAME, ":", IMAGE_TAG])
        image_pull(IMAGE_NAME,IMAGE_TAG,platform)
        cli = docker.from_env()
        image = cli.images.get(image)
        f = open("".join([IMAGE_NAME[IMAGE_NAME.rfind("/")+1:],"_",IMAGE_TAG,"_",platform.replace("/","-"),".tar"]), 'wb')
        for chunk in image.save():
          f.write(chunk)
        f.close()
