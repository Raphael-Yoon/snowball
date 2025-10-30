import pandas as pd

# Read Excel file
df = pd.read_excel('RCM_Generate.xlsx', header=None)

print('=== 파일 기본 정보 ===')
print(f'총 행 수: {len(df)}')
print(f'총 컬럼 수: {len(df.columns)}')
print()

print('=== 헤더 구조 (Row 4) ===')
cols = df.iloc[4, :].tolist()
for i, col in enumerate(cols[:40]):
    if pd.notna(col):
        print(f'컬럼 {i}: {col}')
print()

print('=== 데이터 샘플 (Row 7-10) ===')
sample_cols = [1, 2, 3, 4, 8, 9, 14, 15, 16]
print(df.iloc[7:11, sample_cols].to_string())
print()

print('=== 통제 유형 분포 ===')
# Row 7부터가 실제 데이터
data_df = df.iloc[7:, :]
process_col = data_df.iloc[:, 1]
print(process_col.value_counts())
