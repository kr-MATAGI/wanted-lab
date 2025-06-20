# Wantedlab API

시니어 파이썬 개발자 채용 과제

## DB 설계

<h3>dump.sql 파일에 csv 내 기본 데이터가 삽입되어 있습니다.</h3>

![wanted_lab_db_img](https://github.com/user-attachments/assets/3a0bed4d-838f-4a25-9628-acb66b351154)


## 🚀 Docker 배포

### 사전 요구사항
- Docker
- Docker Compose

### 배포 방법

1. **저장소 클론**
```bash
git clone https://github.com/kr-MATAGI/wanted-lab.git
```

2. **Docker Compose로 서비스 시작**
```bash
docker-compose up -d
```

3. **서비스 관리**
```bash
docker-compose down
```

4. **서비스 재시작**
```bash
docker-compose restart
```

### 서비스 접속 정보

- **FastAPI 애플리케이션**: http://localhost:8001
- **API 문서**: http://localhost:8001/docs
- **PostgreSQL DB**: localhost:5432
  - 데이터베이스: wantedlab
  - 사용자: postgres
  - 비밀번호: postgres

## 📝 API 사용법

### 헤더 설정
모든 API 요청 시 다음 헤더를 포함해야 합니다:
```
x-wanted-language: ko
```

## 🔧 개발 환경

### 로컬 개발 환경 설정

1. **가상환경 생성**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **환경 변수 설정**
```yaml
# .env.dev
DB_HOST="localhost"
DB_PORT=5432
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_NAME="wantedlab"
DB_ECHO=False
```

4. **애플리케이션 실행**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 🧪 테스트
 - 제공해주신 pytest의 json.loads(...) 대신 resp.json()을 사용했습니다.
```python
json.loads(resp.data.decode("utf-8")) # Flask
resp.json() # FastAPI
```

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_parse_csv.py

# 테스트 파일의 특정 함수만 실행
pytest tests/test_senior_app.py::test_company_name_autocomplete
```
