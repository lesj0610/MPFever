@echo off
chcp 65001 >nul
rem ================================================================
rem  트랜스포트 피버 3 PvE 모드 실행 (MPFever + PvE 패치)
rem  이 파일은 MPFever.exe 와 같은 폴더에 두고 더블클릭해서 실행합니다.
rem  아래 값을 바꾸고 저장한 뒤, MPFever 를 닫았다가 이 파일로 다시
rem  실행하면 적용됩니다.
rem ================================================================

rem ---- PvE 모드 (1 = 켬, 0 = 끔: 끄면 MPFever 원래 규칙)
set MPFEVER_PVE=1

rem ---- 파산한 AI 의 자산 처리
rem   0 = MPFever 방식: 경매, 안 팔린 것은 제거 (기본)
rem   1 = 경매 없이 즉시 제거: 노선, 차량, 역, 차량기지, 선로와 신호
rem       (도로와 버스 정류장은 남습니다)
set MPFEVER_PVE_REMOVE=0

rem ---- AI 성향: "번호:성향" 을 쉼표로 이어 씁니다
rem   번호 = 로비의 컴퓨터 회사 번호 (Computer 1, Computer 2 ...)
rem   aggressive   = 공격적 확장 (돈을 덜 남기고 빨리 넓힘, 플레이어와 경쟁)
rem   balanced     = 균형 (난이도 설정 그대로)
rem   conservative = 보수적 확장 (돈을 더 남기고 천천히 넓힘, 경쟁 피함)
set MPFEVER_PVE_STYLE=1:balanced,2:aggressive,3:conservative

rem ---- 플레이어의 철거 허용 (1 = 허용, 0 = 금지)
rem   마을 건물 (불도저, 그리고 건물을 밀고 짓는 건설 모두)
set MPFEVER_PVE_DEMOLISH_TOWN=0
rem   산업 시설
set MPFEVER_PVE_DEMOLISH_INDUSTRY=0
rem   기존 도로 (회사 소유가 아닌 마을 도로, 공용 도로) 를 불도저로 철거
rem   (도로 개량과 연결은 언제나 됩니다)
set MPFEVER_PVE_DEMOLISH_ROAD=0

rem ---- AI 의 마을 건물 철거
rem   1 = 철거하지 않음 (기본, 건물이 걸리면 그 공사를 포기)
rem   0 = 도로나 차고를 지을 때 걸리는 건물을 철거함
set MPFEVER_AIKEEPBUILDINGS=1

if not exist "%~dp0MPFever.exe" (
  echo MPFever.exe 를 찾지 못했습니다. 이 파일을 MPFever.exe 와 같은 폴더에 두세요.
  pause
  exit /b 1
)
start "" "%~dp0MPFever.exe"
