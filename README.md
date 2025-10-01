<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Elxss/Image-Captcha-Solver">
    <img src="https://raw.githubusercontent.com/Elxss/Elxss.github.io/main/src/img/logo.png" alt="Logo" width="300" height="300">
  </a>

  <h3 align="center">Captcha Solver GUI</h3>

  <p align="center">
    <br />
    <a href="https://github.com/Elxss/Image-Captcha-Solver/issues">Report Bug</a>
    ·
    <a href="https://github.com/Elxss/Image-Captcha-Solver/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#About The Project">About The Project</a></li>
    </li>
    <li><a href="#Installation">Installation</a></li>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

### Small Preview !

<img src="https://raw.githubusercontent.com/Elxss/Image-Captcha-Solver/main/Preview/SolverGUI3.gif" alt="Demo" width="75%" align="left">
<img src="https://raw.githubusercontent.com/Elxss/Image-Captcha-Solver/main/Preview/SolverGUI2.gif" alt="Demo" width="75%" align="center">
<img src="https://raw.githubusercontent.com/Elxss/Image-Captcha-Solver/main/Preview/SolverGUI1.gif" alt="Demo" width="75%" align="right">

### About The Project

You're making a bot farm ? or a Scrapper ?

You don't want to have to manage costs while debugging you're system ?

This script is THE solution for your problem !

A Small API running in Python Receives the Tickets and replies to them as if it was a consumer API, Such as 2Captcha

Consider Staring this project if you like it :)

This project uses Python and a few modules

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps. -->

### Installation

_Simple unzip, install modules and voila_

1. If you're interested in this project i assume that you already have bases in computer sience, Python is required to run the project , you can download it directly from [https://www.python.org/](https://www.python.org/)
2. Install the required dependancies with the command ```pip install requirements.txt``` if you're really struggling just start the setup .bat mate
3. The script is ready to be run, you can possibly change the settings in the file ```settings.cfg``` there arent a lot of options so far only ip, port, and the background path

```c
[API]
host = localhost
port = 4848

[general]
background = Themes/theme3.gif

```

4. You need to add the embedings in your scrapping script now, examples are available in the folder ```Examples``` you can use something like this in Python:
```python
import ImgCaptchaClient

Img_Captcha_Local = True

LocalSolver = ImgCaptchaClient.Solver("http://localhost:4848")

if Img_Captcha_Local:
    Response = LocalSolver.solve_image("IMAGE PATH")
else:
    ## your normal script
    print("Consumer API image Captcha Solver")
```

IF YOU'RE NOT USING PYTHON THIS IS JUST A POST REQUEST TO : ```http://localhost:1825/api/submit``` with who you'll get a request id (req_id) that you'll need to ping ```http://localhost:1825/api/check/{req_id}``` you'll get your queue_position 

here is the script of ```ImgCaptchaClient.py``` for you to understand properly :

```python
import requests
import time
import sys

class SolverClient:
    def __init__(self, server_url='http://localhost:4848'):
        self.api_url = server_url
    
    def solve_image(self, image_path):
        try:

            with open(image_path, 'rb') as f:
                response = requests.post(
                    f"{self.api_url}/api/submit",
                    files={'image': f}
                )
            
            if not response.ok:
                print(f"HTTP Error {response.status_code}")
                return None
                
            data = response.json()
            req_id = data['request_id']
            print(f"ID: {req_id}")
            print(f"Position in queue: {data['queue_position']}")
            
            while True:
                response = requests.get(f"{self.api_url}/api/check/{req_id}")
                data = response.json()
                
                if data['status'] != 'PENDING':
                    return data['status']
                
                print(f"\rWaiting... Position: {data['queue_position']}", end="")
                time.sleep(1)
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: client.py <path_image>")
        sys.exit(1)
    
    client = SolverClient()
    result = client.solve_image(sys.argv[1])
    print(f"Result: {result}")
```



4. You're done :)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Make it work
- [ ] Youtube Video

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Elxss - discord: eliasss8886_ - elxssgitcontact@gmail.com - website: [elxss.github.io](https://elxss.github.io/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<p align="center">This is a Readme.md <a href="https://github.com/othneildrew/Best-README-Template/blob/master/README.md">Template</a></p>
