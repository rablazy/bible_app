## BibleAPI

Different versions of **Bible** are imported based on defined format, then accessible via **API**.
You can import other version following the same format.

Currently imported versions :
- fr :
    - Bible Louis Second 21 (LSG_21)
- en :
    - King James Version (KJV)
    - American Standard Version (ASV_1901)
- mg :
    - Baiboly Malagasy 1886 (BMG_1886)

## Motivation

This is part of a bigger project to manage choir activities (scriptures, music media, playlist, music sheets, events, ...) in my local community. <br>
Also an opportunity to practice ***FastAPI*** and ***SQLAlchemy***

## Build status
![GitHub CI](https://github.com/rablazy/choir_app/actions/workflows/ci.yml/badge.svg)


## Tech / framework used

<b>Built with</b>
- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)


## Local Development

Make sure you are in a virtual environment with Python >= 3.9

Then install poetry and project dependencies
```bash
$ pip install poetry
$ cd backend/app
$ poetry install
```

The project is configured to use sqlite by default.
(Move to postgresql later)

Run the initial script which will run migrations and import initial data.

It will import initial (or future) different versions of bible in your local db

```bash
$ chmod +x prestart.sh
$ ./prestart.sh
```

Local run with uvicorn in dev mode
```bash
$ chmod +x dev.sh
$ ./dev.sh
```

It will serve a simple API at `http://localhost:8001`

FastAPI docs at `http://localhost:8001/docs`

To reverse engineering existing bible in db to json, use <ins></ind></in>*reverse.sh*</ins> script

Output file saved in app/export/bible/[lang]/[version].json

```bash
$ cd backend/app
$ chmod +x reverse.sh
$ ./reverse.sh
```

## Tests

You can run tests with one of these commands
```bash
$ make test
$ make testcov
```

## Run with docker

```bash
$ docker build -t <image_name> .
$ docker run -p 8001:8001 --name <container_name> <image_name>
```

## API Reference

- [ ] Detailed doc
- [x] Default doc  `http://localhost:8001/docs`


## Credits

- Project template : <ins>https://github.com/ChristopherGS/ultimate-fastapi-tutorial</ins>
- Bible versions :  <ins>https://www.bicaso.fr/Bible.html</ins>
- MG1886 bible version : <ins>TOVOHERY Zafimanantsoa Pascal</ins>


## License
MIT © <b>Olivier SIMON</b> 🇲🇬 [blazeorjohny6\@gmail.com](mailto:blazeorjohny6@gmail.com)