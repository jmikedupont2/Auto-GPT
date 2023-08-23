# Setting up Turbo

Turbo is a fork of the main Auto-GPT project. 

It is a drop-in replacement for the original, but at this time, it must be installed either by cloning the repository. Example installation instructions are below.

> :warning: **Docker Is Not Supported (v0.4.7)**: The docker installation method will not work at this time.

### Linux/MacOS:

```bash
virtualenv turbo-venv
source agpt-turbo-venv/bin/activate
git clone https://github.com/lc0rp/Auto-GPT-Turbo.git
cd Auto-GPT-Turbo
pip install -r requirements.txt
./run.sh
```

### Windows:

```bash
virtualenv turbo-venv
agpt-turbo-venv\Scripts\activate.bat
git clone https://github.com/lc0rp/Auto-GPT-Turbo.git
cd Auto-GPT-Turbo
pip install -r requirements.txt
.\run.bat
```

See https://docs.agpt.co/setup/ for more details on Auto-GPT installation.