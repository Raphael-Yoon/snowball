import pandas as pd

# Read Excel file
df = pd.read_excel('RCM_Generate.xlsx', header=None)

print('=== Sub Process 분포 ===')
data_df = df.iloc[7:, :]
subprocess_col = data_df.iloc[:, 2]
print(subprocess_col.value_counts())
print()

print('=== 위험 코드 분포 ===')
risk_code_col = data_df.iloc[:, 8]
print(risk_code_col.value_counts())
print()

print('=== 통제활동 코드 분포 ===')
control_code_col = data_df.iloc[:, 14]
print(control_code_col.value_counts())
print()

print('=== 전체 컬럼명 (Row 4) ===')
cols = df.iloc[4, :].tolist()
for i, col in enumerate(cols):
    if pd.notna(col):
        print(f'{i}: {str(col)[:50]}')
