# 혼밥남녀

[![CircleCI](https://circleci.com/gh/Flative/hbnn.svg?style=shield&circle-token=c1aadac44ee58ffe8d6a8cf56d033a2135637552)](https://circleci.com/gh/Flative/hbnn)

## 개요
서비스 는 [해당 문서](https://github.com/Flative/hbnn/wiki/%EB%AA%85%EC%84%B8%EC%84%9C)를 참조합니다.

## 설치

1. 이 저장소를 클론 받습니다.
2. 개발 의존성을 설치합니다.
```bash
$ pip install -r requirements/dev.txt
```

## 실행

1. 데이터 베이스를 마이그레이션 합니다. (현재 Sqlite3.)
```bash
$ python manage.py migrate
```
2. 개발 서버를 실행합니다.
```bash
$ python manage.py runserver
```

## 배포

1. 도커 이미지를 굽습니다.
```bash
$ docker build -t hbnn:some-tag latest
```
2. 알아서 잘 올립니다. (추후 기재)
