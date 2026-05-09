@echo off
echo ========================================
echo     대시보드 자동 업데이트 시스템
echo ========================================
echo.

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

echo 선택하세요:
echo 1. 전체 자동화 (크롤링 + 데이터 집계 + 대시보드 업데이트)
echo 2. 데이터 집계만 (기존 DB 데이터로 대시보드 업데이트)
echo 3. 특정 연도 지정해서 업데이트
echo 4. 종료
echo.

set /p choice=번호를 입력하세요 (1-4): 

if "%choice%"=="1" (
    echo.
    echo 🚀 전체 자동화를 시작합니다...
    python -m pipeline.auto_update_dashboard
) else if "%choice%"=="2" (
    echo.
    echo 📊 기존 데이터로 대시보드를 업데이트합니다...
    python -m pipeline.auto_update_dashboard --no-crawl
) else if "%choice%"=="3" (
    set /p year=업데이트할 연도를 입력하세요 (예: 2025): 
    echo.
    echo 📅 %year%년 데이터로 대시보드를 업데이트합니다...
    python -m pipeline.auto_update_dashboard --year %year%
) else if "%choice%"=="4" (
    echo 종료합니다.
    exit /b 0
) else (
    echo 잘못된 선택입니다.
    pause
    goto :start
)

echo.
echo 작업이 완료되었습니다.
pause
