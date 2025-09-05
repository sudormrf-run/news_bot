#!/bin/bash
# 뉴스 발송 간편 스크립트

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL 확인
if [ -z "$1" ]; then
    echo -e "${RED}❌ 오류: URL을 입력해주세요${NC}"
    echo "사용법: ./publish.sh <URL> [옵션]"
    echo ""
    echo "예시:"
    echo "  ./publish.sh https://news.smol.ai/issues/25-09-01"
    echo "  ./publish.sh https://news.smol.ai/issues/25-09-01 --dry-run"
    echo "  ./publish.sh https://news.smol.ai/issues/25-09-01 --github-only"
    echo "  ./publish.sh https://news.smol.ai/issues/25-09-01 --discord-only"
    exit 1
fi

URL=$1
shift # 첫 번째 인자(URL) 제거

echo -e "${GREEN}🚀 뉴스 발송 시작${NC}"
echo "URL: $URL"
echo "옵션: $@"
echo "-----------------------------------"

# Python 스크립트 실행
python publish_news.py "$URL" "$@"

# 종료 코드 확인
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 발송 완료!${NC}"
else
    echo -e "${RED}❌ 발송 중 오류가 발생했습니다${NC}"
    exit 1
fi