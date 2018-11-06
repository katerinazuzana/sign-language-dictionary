FROM katerinazuzana/dictionary-env

MAINTAINER Katerina Zuzanakova <katerina.zuzanakova@gmail.com>

COPY . /usr/src/sign-language-dictionary

WORKDIR /usr/src/sign-language-dictionary/dictionary

CMD ["python", "main.py"]
