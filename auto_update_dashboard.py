#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동화 대시보드 업데이트 스크립트 (수정된 버전)
- 웹 크롤링 (mpdbBring, yydbBring)
- 데이터 집계 (updateAmount, updatePercent)
- script.js 파일 자동 업데이트 (대괄호 오류 수정)
"""

import subprocess
import sys
import sqlite3
import pandas as pd
import re
import os
from datetime import datetime
from count import count_nums

class DashboardAutomator:
    def __init__(self, year=None):
        self.year = year or str(datetime.now().year)
        self.base_dir = os.path.dirname(__file__)
        self.mp_db_path = os.path.join(self.base_dir, 'db', 'priceDB.db')
        self.yy_db_path = os.path.join(self.base_dir, 'db', 'yongyuk.db')
        self.script_js_path = os.path.join(self.base_dir, 'html', 'js', 'script.js')
        
    def run_crawler(self, crawler_script, args=None):
        """크롤러 스크립트 실행"""
        try:
            cmd = [sys.executable, crawler_script]
            if args:
                cmd.extend(args)
                
            print(f"🕷️  {' '.join(cmd)} 실행 중...")
            # Run subprocess without capture_output so child process stdout/stderr
            # are forwarded to this console (shows crawler logs in real time).
            result = subprocess.run(cmd, cwd=self.base_dir)
            if result.returncode == 0:
                print(f"✅ {crawler_script} 실행 완료")
                return True
            else:
                print(f"❌ {crawler_script} 실행 실패 (returncode={result.returncode})")
                return False
        except Exception as e:
            print(f"❌ {crawler_script} 실행 중 오류: {e}")
            return False
    
    def get_amount_data(self, db_path):
        """수량 데이터 계산 (updateAmount.py 로직)"""
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql("SELECT date, predict_price, base_price FROM price_set ORDER BY date ASC", conn)
            conn.close()
            
            # 6개의 예가율 범위별로 12개월 데이터 초기화
            y_values = [[0 for _ in range(12)] for _ in range(6)]
            
            # 범위에 따른 예가율 갯수 세기
            for i in range(len(df['date'])):
                for j in range(12):
                    month = j + 1
                    month_str = f"{self.year}.{month:02d}" if month < 10 else f"{self.year}.{month}"
                    
                    if month_str in df.at[i, 'date']:
                        predict_rate = round(df.at[i, 'predict_price'] / df.at[i, 'base_price'] * 100, 1)
                        count_nums(y_values, predict_rate, j)
            
            return y_values
            
        except Exception as e:
            print(f"❌ 수량 데이터 계산 오류: {e}")
            return None
    
    def get_percent_data(self, db_path):
        """비율 데이터 계산 (updatePercent.py 로직)"""
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql("SELECT date, predict_price, base_price FROM price_set ORDER BY date ASC", conn)
            conn.close()
            
            # 6개의 예가율 범위별로 12개월 데이터 초기화
            y_values = [[0 for _ in range(12)] for _ in range(6)]
            
            # 범위에 따른 예가율 갯수 세기
            for i in range(len(df['date'])):
                for j in range(12):
                    month = j + 1 
                    month_str = f"{self.year}.{month:02d}" if month < 10 else f"{self.year}.{month}"
                    
                    if month_str in df.at[i, 'date']:
                        predict_rate = round(df.at[i, 'predict_price'] / df.at[i, 'base_price'] * 100, 1)
                        count_nums(y_values, predict_rate, j)
            
            # 비율 계산
            result = []
            for i in range(len(y_values)):
                result.append(sum(y_values[i]))
            
            # 백분율로 변환
            for i in range(6):
                for j in range(12):
                    if result[i] != 0:
                        y_values[i][j] = round(y_values[i][j] / result[i] * 100, 2)
            
            return y_values
            
        except Exception as e:
            print(f"❌ 비율 데이터 계산 오류: {e}")
            return None
    
    def update_script_js(self, mp_amt_data, mp_rate_data, yy_amt_data, yy_rate_data):
        """script.js 파일의 const 변수들을 자동 업데이트 (대괄호 오류 수정)"""
        try:
            print("📝 script.js 파일 업데이트 중...")
            
            # script.js 파일 읽기
            with open(self.script_js_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 데이터를 올바른 JavaScript 배열 형식으로 변환
            def format_js_array(data):
                if not data:
                    return "[]"
                formatted_rows = [f"[{', '.join(map(str, row))}]" for row in data]
                return f"[{', '.join(formatted_rows)}]"

            # 동적 연도 적용
            target_year = self.year

            # 물품 비율 업데이트
            content = re.sub(
                fr"(const yValrate{target_year}\s*=\s*)\[.*?\];",
                f"\\1{format_js_array(mp_rate_data)};",
                content,
                flags=re.DOTALL
            )
            # 물품 수량 업데이트
            content = re.sub(
                fr"(const yValamt{target_year}\s*=\s*)\[.*?\];",
                f"\\1{format_js_array(mp_amt_data)};",
                content,
                flags=re.DOTALL
            )
            # 용역 비율 업데이트
            content = re.sub(
                fr"(const yValrate{target_year}yy\s*=\s*)\[.*?\];",
                f"\\1{format_js_array(yy_rate_data)};",
                content,
                flags=re.DOTALL
            )
            # 용역 수량 업데이트
            content = re.sub(
                fr"(const yValamt{target_year}yy\s*=\s*)\[.*?\];",
                f"\\1{format_js_array(yy_amt_data)};",
                content,
                flags=re.DOTALL
            )
            
            # 파일에 쓰기
            with open(self.script_js_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print("✅ script.js 파일 업데이트 완료")
            return True
            
        except Exception as e:
            print(f"❌ script.js 업데이트 오류: {e}")
            return False
    
    def run_full_automation(self, run_crawlers=True):
        """전체 자동화 프로세스 실행"""
        print(f"🚀 대시보드 자동 업데이트 시작 (연도: {self.year})")
        print("=" * 50)
        
        # 1. 크롤러 실행 (선택적)
        if run_crawlers:
            print("1️⃣  웹 크롤링 단계")
            mp_success = self.run_crawler('mpdbBring.py')
            yy_success = self.run_crawler('yydbBring.py')
            
            if not (mp_success and yy_success):
                print("⚠️  크롤링 실패, 기존 데이터로 진행합니다.")
        else:
            print("1️⃣  웹 크롤링 단계 건너뜀 (기존 데이터 사용)")
        
        # 2. 데이터 집계
        print("\n2️⃣  데이터 집계 단계")
        
        # 물품 데이터 (priceDB.db)
        print("📊 물품 데이터 집계 중...")
        mp_amt_data = self.get_amount_data(self.mp_db_path)
        mp_rate_data = self.get_percent_data(self.mp_db_path)
        
        # 용역 데이터 (yongyuk.db)
        print("📊 용역 데이터 집계 중...")
        yy_amt_data = self.get_amount_data(self.yy_db_path)
        yy_rate_data = self.get_percent_data(self.yy_db_path)
        
        if not all([mp_amt_data, mp_rate_data, yy_amt_data, yy_rate_data]):
            print("❌ 데이터 집계 실패")
            return False
        
        # 3. script.js 업데이트
        print("\n3️⃣  대시보드 파일 업데이트 단계")
        success = self.update_script_js(mp_amt_data, mp_rate_data, yy_amt_data, yy_rate_data)
        
        if success:
            print("\n🎉 대시보드 자동 업데이트 완료!")
            print(f"📈 물품 수량 데이터: {mp_amt_data}")
            print(f"📊 물품 비율 데이터: {mp_rate_data}")
            print(f"📈 용역 수량 데이터: {yy_amt_data}")
            print(f"📊 용역 비율 데이터: {yy_rate_data}")
        else:
            print("\n❌ 대시보드 업데이트 실패")
        
        return success

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='대시보드 자동 업데이트 스크립트')
    parser.add_argument('--year', type=str, default=str(datetime.now().year),
                       help='업데이트할 연도 (기본값: 현재 연도)')
    parser.add_argument('--no-crawl', action='store_true',
                       help='크롤링 건너뛰고 기존 데이터만 사용')

    args = parser.parse_args()

    automator = DashboardAutomator(year=args.year)
    success = automator.run_full_automation(run_crawlers=not args.no_crawl)

    # average.py 실행하여 평균 예가율 JSON 업데이트
    print('\n📊 average.py 실행 (DB -> JSON)')
    avg_success = automator.run_crawler('average.py', args=['--year', automator.year])
    if avg_success:
        print('✅ JSON 업데이트 완료')
    else:
        print('⚠️  JSON 업데이트 실패')

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
