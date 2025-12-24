---
title: Sheet Skill Changelog
---

## 2024-12-23 - Initial Release

### Added

#### Core Features
- `info` - Spreadsheet 메타데이터 조회
- `read` - 범위 읽기 (table/json/csv 출력)
- `update` - 범위 업데이트
- `append` - 행 추가
- `clear` - 범위 삭제

#### Formatting Features
- `bgcolor` - 배경색 설정
- `border` - 테두리 설정 (SOLID, DASHED, DOTTED, DOUBLE 등)
- `textfmt` - 텍스트 서식 (bold, italic, size, color)
- `table` - 테이블 스타일 (헤더 + 테두리 한번에)

#### Pivot Table
- `pivot` - 피벗 테이블 생성 (rows, columns, values, summarize functions)

### Documentation
- `SKILL.md` - 사용법 문서
- `docs/RESEARCH.md` - API 조사 결과 (인증, 포맷팅, 피벗테이블)
- `docs/SPEC.md` - 구현 명세서

### Scripts
- `scripts/utils.py` - 인증, 서비스 빌더, URL 파서
- `scripts/sheet_api.py` - API 함수 + CLI

### Authentication
- ADC (Application Default Credentials) 방식 사용
- gcloud CLI 기반 인증
- 팀 공용 프로젝트: `data-470906`
