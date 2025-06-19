#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스케줄러용 간단 실행 스크립트
Windows 작업 스케줄러나 cron에서 사용할 수 있습니다.
"""

import os
import sys
import logging
from datetime import datetime
from auto_update_dashboard import DashboardAutomator

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard_update.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def scheduled_update():
    """스케줄된 업데이트 실행"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("스케줄된 대시보드 업데이트 시작")
        
        # 현재 연도로 자동화 실행
        automator = DashboardAutomator()
        success = automator.run_full_automation(run_crawlers=True)
        
        if success:
            logger.info("대시보드 업데이트 성공")
        else:
            logger.error("대시보드 업데이트 실패")
            
        return success
        
    except Exception as e:
        logger.error(f"스케줄된 업데이트 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 작업 디렉토리를 스크립트 위치로 변경
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = scheduled_update()
    sys.exit(0 if success else 1)
