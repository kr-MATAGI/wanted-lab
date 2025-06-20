#!/bin/bash

echo "🚀 Wantedlab API Docker 배포 시작..."

# 기존 컨테이너 정리
echo "📦 기존 컨테이너 정리 중..."
docker-compose down

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build --no-cache

# 서비스 시작
echo "▶️  서비스 시작 중..."
docker-compose up -d

# 서비스 상태 확인
echo "📊 서비스 상태 확인 중..."
sleep 10
docker-compose ps

# 헬스체크
echo "🏥 헬스체크 중..."
sleep 5

# PostgreSQL 연결 확인
echo "🗄️  PostgreSQL 연결 확인 중..."
docker-compose exec -T postgres pg_isready -U postgres -d wantedlab

# API 서비스 확인
echo "🌐 API 서비스 확인 중..."
curl -f http://localhost:8001/ || echo "API 서비스가 아직 준비되지 않았습니다."

echo "✅ 배포 완료!"
echo "📖 API 문서: http://localhost:8001/docs"
echo "🔍 로그 확인: docker-compose logs -f" 