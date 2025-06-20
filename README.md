# wanted-lab
시니어 파이썬 개발자 채용 과제

# Wantedlab API

FastAPI 기반의 회사 및 태그 관리 API 서비스입니다.

## 🚀 Docker 배포

### 사전 요구사항
- Docker
- Docker Compose

### 배포 방법

1. **저장소 클론**
```bash
git clone <repository-url>
cd wanted-lab
```

2. **Docker Compose로 서비스 시작**
```bash
docker-compose up -d
```

3. **서비스 상태 확인**
```bash
docker-compose ps
```

4. **로그 확인**
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs app
docker-compose logs postgres
```

### 서비스 접속 정보

- **FastAPI 애플리케이션**: http://localhost:8001
- **API 문서**: http://localhost:8001/docs
- **PostgreSQL DB**: localhost:5432
  - 데이터베이스: wantedlab
  - 사용자: postgres
  - 비밀번호: postgres

### 서비스 관리

```bash
# 서비스 중지
docker-compose down

# 서비스 중지 및 볼륨 삭제
docker-compose down -v

# 서비스 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart app
```

## 📝 API 사용법

### 헤더 설정
모든 API 요청 시 다음 헤더를 포함해야 합니다:
```
x-wanted-language: ko
```

### 주요 엔드포인트

- `GET /companies/{company_name}` - 회사 정보 조회
- `POST /companies/` - 새 회사 등록
- `PUT /companies/{company_name}/tags` - 회사 태그 추가
- `DELETE /companies/{company_name}/tags/{tag}` - 회사 태그 삭제

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
```bash
cp .env.dev.example .env.dev
# .env.dev 파일에서 데이터베이스 설정 수정
```

4. **애플리케이션 실행**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_parse_csv.py
```
