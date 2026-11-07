트랜스포트 피버 3 PvE 모드 (MPFever 포크, pve 브랜치)
=====================================================

AI 경쟁사 1~3곳과 한 맵에서 겨루는 PvE 모드입니다. AI 경쟁사(컴퓨터 회사)는 MPFever 에 이미
있는 기능을 쓰고, 이 브랜치가 PvE 규칙을 덧붙입니다.

이 브랜치가 더하는 것
- AI 만 파산합니다. 플레이어는 파산하지 않습니다 (기본 게임과 같음).
- 파산한 AI 는 게임에서 탈락하고 다시 시작하지 않습니다.
- 파산 자산 처리: 기본은 MPFever 경매. 옵션으로 경매 없이 즉시 제거(선로 포함).
- AI 성향: 공격적 / 균형 / 보수적 확장 (난이도와 별개).
- 플레이어 철거 규칙: 마을 건물, 산업 시설, 기존 도로의 철거를 금지/허용.
- 모든 AI 가 파산하면 승리 메시지. 그 뒤로도 계속 플레이할 수 있습니다.

바뀐 파일: mod/mpfever_1/content 의 mpfever_eco.lua, mpfever_ai.lua, mpfever_bridge.script.lua
(바뀐 곳마다 "[PvE]" 표시), tests/test_pve*.py, pve/ 폴더, build.bat (이 두 파일을 zip 에 넣음).


1. 받기와 설치
--------------
 1) 포크의 Actions 탭 -> 최근 pve 브랜치의 CI 실행 -> Artifacts 의 MPFever-<커밋> 을 받습니다.
    (14일 보관. 그 안의 MPFever-<버전>.zip 이 완성된 MPFever 입니다.)
 2) MPFever-<버전>.zip 을 원하는 폴더에 풉니다. 이전 MPFever 폴더가 있으면 그 위에 덮어써도 됩니다
    (mpfever_settings.txt 는 zip 에 없으므로 설정은 남습니다).
 3) 서명 없는 빌드라 처음 실행할 때 Windows 경고가 뜨면 "추가 정보 -> 실행" 을 누릅니다.
 4) MPFever 자동 업데이트는 꺼 두세요: MPFever 의 Settings 창에서 끄거나, MPFever.exe 옆
    mpfever_settings.txt 에 autoupdate=0 한 줄. 켜 두면 원본(dkdknight/MPFever) 릴리스로 덮어씁니다.


2. 게임 시작
------------
 1) Start-PvE.bat 를 더블클릭합니다. (MPFever.exe 를 직접 실행하면 PvE 규칙이 꺼집니다.)
 2) 게임의 메인 메뉴에서 Multiplayer 카드 -> Host a game.
 3) Company mode: "One company per player" (플레이어마다 회사 하나).
 4) 새 맵은 New game..., 기존 세이브는 그 세이브 아래의 Host.
 5) 로비의 "Game settings..." 에서:
    - Start money of a company: 0  -> 기본 게임처럼 0원에서 대출로 시작
    - A company in debt goes bankrupt after: 3 / 6 / 12 / 24개월 (0 이면 AI 도 파산 없음)
    - Auction of a bankruptcy: MPFEVER_PVE_REMOVE=0 일 때만 쓰입니다.
 6) "Add a computer company" 로 1~3곳 추가, 각각 난이도(Easy/Normal/Hard)와 색상 선택.
    컴퓨터 회사의 시작 자금은 기본값(플레이어와 같게)으로 둡니다.
    번호(Computer 1, 2, 3)가 Start-PvE.bat 의 성향 번호입니다. 게임 안 이름은 번호 순서대로
    Regional Transport, Valley Coaches, Coastal Lines 입니다.
 7) Start the game.


3. 설정 (Start-PvE.bat 안)
--------------------------
메모장으로 열어 값을 바꾸고 저장한 뒤, MPFever 를 닫았다가 다시 실행하세요.

  MPFEVER_PVE=1                    PvE 모드 켜기 (0 이면 MPFever 원래 규칙)
  MPFEVER_PVE_REMOVE=0             파산 자산: 0=경매(기본), 1=경매 없이 즉시 제거
  MPFEVER_PVE_STYLE=1:balanced,2:aggressive,3:conservative
                                   AI 번호별 성향
  MPFEVER_PVE_DEMOLISH_TOWN=0      플레이어 마을 건물 철거 (1=허용, 0=금지)
  MPFEVER_PVE_DEMOLISH_INDUSTRY=0  플레이어 산업 시설 철거 (1=허용, 0=금지)
  MPFEVER_PVE_DEMOLISH_ROAD=0      플레이어 기존 도로 철거 (1=허용, 0=금지)
  MPFEVER_AIKEEPBUILDINGS=1        AI 의 마을 건물 철거 (1=안 함(기본), 0=함)

성향이 바꾸는 것 (난이도 값에 곱해짐):
  aggressive    남겨 두는 돈 0.6배, 성장 전 여유 자금 0.5배, 다음 노선까지 대기 0.5배,
                첫 노선 +1개, 플레이어가 운영 중인 마을과 산업에도 진입
  conservative  남겨 두는 돈 1.5배, 여유 자금 1.5배, 대기 1.5배, 첫 노선 -1개,
                플레이어와 겹치는 곳 피함
  balanced      난이도 그대로


4. 상류(MPFever) 업데이트 받기
------------------------------
 1) GitHub 의 포크 페이지에서 "Sync fork" 로 main 을 상류와 맞춥니다.
 2) pve 브랜치에 main 을 병합합니다 (GitHub 의 PR: base pve <- compare main, 또는 git merge main).
 3) 충돌이 나면 "[PvE]" 표시가 있는 곳만 살려서 고칩니다. 패치는 작은 자리에 모여 있습니다.
 4) 푸시하면 CI 가 테스트(MPFever 테스트 + tests/test_pve*.py)를 돌리고 새 zip 을 만듭니다.


5. 처음 해 볼 점검 (게임 안에서)
--------------------------------
이 브랜치는 게임 없이 오프라인 테스트로만 검증했습니다.

 [ ] 게임이 문제없이 시작되고, 약 1분 뒤 AI 가 정류장과 노선을 짓기 시작한다
 [ ] 내 회사가 빚을 져도 "in debt" 알림이 뜨지 않는다 (플레이어 파산 없음)
 [ ] 불도저로 마을 건물/산업/마을 도로를 누르면 빨간 "PvE 규칙" 문구가 뜨고 철거되지 않는다
 [ ] 내 도로, 내 역은 불도저로 철거된다
 [ ] 빠른 확인: 파산 개월 수 3, AI 를 aggressive 로 두고 4배속. 파산 시 채팅에 "파산! ... 탈락"
 [ ] (MPFEVER_PVE_REMOVE=1) 파산 AI 의 노선, 차량, 역, 차량기지가 사라지고 몇 초 뒤 선로도
     사라지는지, 도로는 남는지
 [ ] 모든 AI 가 파산하면 채팅에 "승리!"

문제가 생기면 MPFever 로그(%TEMP%\mpfever 안, 실행마다 새 폴더)에서 "[PvE]" 줄과 오류 줄을
찾아 주세요. MPFever 창의 Report a problem 은 원본 개발자에게 가므로 쓰지 마세요.


6. 알려진 한계
--------------
- 설정은 로비가 아니라 Start-PvE.bat 에서 합니다 (다음 단계: 로비 화면에 넣기).
- 파산 기준은 "빚(잔액 마이너스) N개월" 하나입니다.
- 즉시 제거에서도 도로 위 버스 정류장은 남습니다 (MPFever 가 정류장 철거를 막아 둠).
- 승리는 채팅 메시지로만 알립니다.
- AI 는 대출을 한 번에 1건까지만 받습니다 (MPFever 원래 규칙).

라이선스: MPFever 와 같은 GPL v3.
