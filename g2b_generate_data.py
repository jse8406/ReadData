import glob
import sqlite3
import json
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
DB_GLOB = os.path.join(DB_DIR, "g2b_*.db")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "html", "data", "g2bRateData.json")

# Rate bands: 99.5% ~ 101.0% in 0.1% increments (16 bands)
RATE_BANDS = [round(99.5 + 0.1 * i, 1) for i in range(16)]


def get_band_index(rate):
    """Return the index of the rate band for a given rate, or None if out of range."""
    rounded = round(rate, 1)
    if rounded < 99.5 or rounded > 101.0:
        return None
    idx = round((rounded - 99.5) * 10)
    if 0 <= idx < 16:
        return idx
    return None


def main():
    # 모든 연도 DB 를 순회하며 결과 누적
    data = {}  # {year: {month: [count_per_band x 16]}}
    db_paths = sorted(glob.glob(DB_GLOB))
    if not db_paths:
        print(f"WARNING: {DB_GLOB} 에 매칭되는 DB 파일이 없습니다.")
        return

    for db_path in db_paths:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT date, base_amount, predict_price
                FROM bid_results
                WHERE base_amount > 0
            """)
        except sqlite3.OperationalError:
            conn.close()
            continue

        for row in cursor.fetchall():
            date_str, base_amount, predict_price = row
            if not date_str or base_amount == 0:
                continue

            rate = predict_price / base_amount * 100
            band_idx = get_band_index(rate)
            if band_idx is None:
                continue

            parts = date_str.split("/")
            if len(parts) < 2:
                continue
            year = int(parts[0])
            month = int(parts[1])

            if year not in data:
                data[year] = {}
            if month not in data[year]:
                data[year][month] = [0] * 16

            data[year][month][band_idx] += 1

        conn.close()

    # Build output JSON: {year: {counts: [[16 bands x 12 months]], percentages: [[16 bands x 12 months]]}}
    result = {}
    for year in sorted(data.keys()):
        counts_by_band = []  # 16 arrays, each with 12 values
        pcts_by_band = []

        for band_idx in range(16):
            band_counts = []
            for month in range(1, 13):
                count = data[year].get(month, [0] * 16)[band_idx]
                band_counts.append(count)
            counts_by_band.append(band_counts)

        # Calculate percentages: for each band, percentage = count / band_total * 100
        # (각 band의 12개월 합이 100%가 되도록)
        for band_idx in range(16):
            band_total = sum(counts_by_band[band_idx])
            band_pcts = []
            for month_idx in range(12):
                if band_total > 0:
                    pct = round(counts_by_band[band_idx][month_idx] / band_total * 100, 2)
                else:
                    pct = 0.0
                band_pcts.append(pct)
            pcts_by_band.append(band_pcts)

        result[str(year)] = {
            "counts": counts_by_band,
            "percentages": pcts_by_band
        }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Generated {OUTPUT_PATH}")
    print(f"Years: {list(result.keys())}")
    for year, d in result.items():
        total = sum(sum(band) for band in d["counts"])
        print(f"  {year}: {total} records in range")


if __name__ == "__main__":
    main()
