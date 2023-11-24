

To collect photos from youtube stream run python code in pipeline directory

python assess_stream.py --stream_link https://www.youtube.com/watch?v=g_L1Ay8P244 --out_dir sloth_tv2


Чтобы склонировать себе репозиторий с submodules используй
`git clone --recurse-submodules main_project_name`

Или чтобы скачать submodules в уже загруженный репозиторий
`git submodule init`

Модель для оценки фотографий можно скачать тут https://drive.google.com/drive/folders/1WvWWj7_U8pcoFRQnJ-4uaoBuICbHlz3A
Положить чекпоинт нужно в pipeline/image_assessment/pretrained_model/

Or via bash command (библиотека gdown лежит в requirements.txt)

`gdown 1TuK5ZPh7hW5f1-B0XCdH-xEToMiBikxn -O pipeline/im
age_assessment/pretrained_model/epoch-82.pth`