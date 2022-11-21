# Groot Backend

This project is one of three projects which make up the conversational agent ```Groot```.

It is intended to use in conjunction with the two other modules ```Groot Frontend``` and ```NLP Module```.

## Prerequisits
- Python 3.9
- Package installer for Python (pip/pipwin)

## Getting Started
1. clone repository
1. navigate to src folder
1. create virtual environment  
    ```python -m venv venv```
1. install requirements  
    ```pip install -r requirements.txt```
1. activate virtual environment
    - ```source venv/bin/activate```
    - ```venv/Scripts/activate ```
1. add flask to then environment variables  
    - ```set FLASK_APP="groot.py"```
    - ```export FLASK_APP="groot.py"```
1. initialize database  
    ```flask init-db```
1. run app  
    ```python groot.py```

## Known Issues
Currently, there are two known issues:
1. WSL2.0 does not support audio yet. There are some workarounds, but they are very unintuitive. We suggest refraining from using WSL2.0 for this project.
2. Two packages may not be downloaded using requirements.txt:
    - Install pyaudio on Windows --> ```pipwin install pyaudio```
    - Install flask-sock --> ```pip install flask-sock```