import sqlite3

# 데이터베이스 경로
db_path = 'db/priceDB.db'

# SQLite 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# min_rate 값이 0인 행 삭제
delete_query = "DELETE FROM price_set WHERE min_rate = 0 or min_rate = ''"
cursor.execute(delete_query)

# 변경사항 저장 (Commit)
conn.commit()

# 삭제된 행 수 출력
print(f"삭제된 행 수: {cursor.rowcount}")

# 연결 종료
conn.close()
