# TelegramMusicTagger

python -m venv venv

### Windows
.\venv\Scripts\activate

### Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python main.py



tree -I "venv|__pycache__|.vs|env|.gitattributes|.gitignore"

.\
├── handlers\
│   ├── __init__.py\
│   ├── audio.py\
│   ├── cover.py\
│   ├── musician.py\
│   └── next_name.py\
├── services\
│   ├── __init__.py\
│   ├── extract_audio_info.py\
│   ├── file_service.py\
│   ├── id3_tag_service.py\
│   └── message_quque.py\
├── requirements.txt\
├── README.md\
├── main.py\
├── bot.py\
├── my_states.py\
└── setting.py\