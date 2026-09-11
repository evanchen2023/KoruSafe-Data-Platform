from faker import Faker
import csv
import os
from datetime import datetime, timedelta
import random

# 初始化 Faker (中文)
fake = Faker('zh_CN')

# 确保输出目录存在
output_dir = 'data/generated'
os.makedirs(output_dir, exist_ok=True)

# 设置随机种子，保证每次运行生成的数据一致（方便调试）
fake.seed_instance(12345)
random.seed(12345)

# ========== 配置参数 ==========
NUM_ORGANISATIONS = 100
NUM_EMPLOYEES = 1000
NUM_INCIDENTS = 5000
NUM_INJURIES = 2000
NUM_CLAIMS = 1500

# ========== 辅助数据池 ==========
industries = ['制造业', '建筑业', '医疗健康', '物流运输', '零售业', '餐饮业', '信息技术', '金融保险', '教育', '能源', '矿业', '农业']
regions = ['华北', '华东', '华南', '西南', '西北', '东北', '华中']

job_roles = ['操作员', '技术员', '工程师', '主管', '经理', '总监', '助理', '专员', '顾问', '分析师', '项目经理', '安全主管']
departments = ['生产部', '工程部', '安全部', '人事部', '财务部', '运营部', '市场部', '研发部', '物流部', '维修部']
employment_types = ['全职', '兼职', '合同工', '临时工', '实习生']

incident_types = ['机械故障', '滑倒摔伤', '化学品泄漏', '火灾', '坠落事故', '触电', '物体打击', '交通事故', '过劳', '职业病']
severity_levels = ['轻度', '中度', '重度', '致命']
locations = ['仓库', '车间', '办公室', '工地', '户外', '实验室', '停车场', '电梯间', '食堂', '维修区']

injury_types = ['骨折', '扭伤', '割伤', '烧伤', '擦伤', '中毒', '压迫伤', '肌肉拉伤', '冲击伤', '窒息', '听力损伤', '视力损伤']
body_parts = ['手部', '腿部', '头部', '背部', '胸部', '手臂', '脚部', '眼睛', '肩膀', '膝盖', '腰', '颈椎']

claim_types = ['工伤保险', '医疗保险', '伤残赔偿', '误工费', '医疗费用', '康复费用']
claim_statuses = ['待审核', '审核中', '已批准', '已拒绝', '已支付', '已完成']

# ========== 1. 生成 Organisations (100条) ==========
print("📊 生成 Organisations...")
organisations = []
for i in range(1, NUM_ORGANISATIONS + 1):
    created_date = fake.date_between(start_date='-10y', end_date='-1y')
    organisations.append([
        i,  # organisation_id (SERIAL, 从1开始)
        fake.company(),  # organisation_name
        random.choice(industries),  # industry
        random.randint(10, 5000),  # employee_count
        random.choice(regions),  # region
        created_date.strftime('%Y-%m-%d')  # created_date (转为字符串)
    ])

# 保存 organisations.csv
with open(os.path.join(output_dir, 'organisations.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['organisation_id', 'organisation_name', 'industry', 'employee_count', 'region', 'created_date'])
    writer.writerows(organisations)
print(f"✅ 生成 {len(organisations)} 条组织数据")

# ========== 2. 生成 Employees (1,000条) ==========
print("👤 生成 Employees...")
employees = []
for i in range(1, NUM_EMPLOYEES + 1):
    org = random.choice(organisations)
    start_date = fake.date_between(start_date='-5y', end_date='today')
    employees.append([
        i,  # employee_id
        org[0],  # organisation_id (引用已有组织)
        random.choice(job_roles),  # job_role
        random.choice(departments),  # department
        random.choice(employment_types),  # employment_type
        org[4],  # region (与组织所在区域一致)
        start_date.strftime('%Y-%m-%d')  # start_date (转为字符串)
    ])

# 保存 employees.csv
with open(os.path.join(output_dir, 'employees.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['employee_id', 'organisation_id', 'job_role', 'department', 'employment_type', 'region', 'start_date'])
    writer.writerows(employees)
print(f"✅ 生成 {len(employees)} 条员工数据")

# ========== 3. 生成 Incidents (5,000条) ==========
print("🚨 生成 Incidents...")
incidents = []
for i in range(1, NUM_INCIDENTS + 1):
    emp = random.choice(employees)
    org_id = emp[1]  # employee 所属的组织
    
    # 确保 incident_date 在员工入职之后 (emp[6] 现在是字符串)
    emp_start_date = datetime.strptime(emp[6], '%Y-%m-%d').date()
    incident_date = fake.date_between(start_date=emp_start_date, end_date='today')
    
    incidents.append([
        i,  # incident_id
        org_id,  # organisation_id
        emp[0],  # employee_id
        incident_date.strftime('%Y-%m-%d'),  # incident_date
        random.choice(incident_types),  # incident_type
        random.choice(severity_levels),  # severity
        random.choice(locations),  # location
        fake.sentence(nb_words=10)  # description
    ])

# 保存 incidents.csv
with open(os.path.join(output_dir, 'incidents.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['incident_id', 'organisation_id', 'employee_id', 'incident_date', 'incident_type', 'severity', 'location', 'description'])
    writer.writerows(incidents)
print(f"✅ 生成 {len(incidents)} 条事故数据")

# ========== 4. 生成 Injuries (2,000条) ==========
print("🏥 生成 Injuries...")
# 从 incidents 中随机选一部分作为有伤害的事故
selected_incidents = random.sample(incidents, min(NUM_INJURIES, len(incidents)))

injuries = []
for i in range(1, NUM_INJURIES + 1):
    incident = selected_incidents[i - 1] if i <= len(selected_incidents) else random.choice(incidents)
    
    # 根据事故严重程度调整医疗费用和休息天数
    severity = incident[5]  # severity
    if severity == '致命':
        medical_cost = random.randint(50000, 200000)
        days_off = random.randint(90, 365)
    elif severity == '重度':
        medical_cost = random.randint(20000, 80000)
        days_off = random.randint(30, 120)
    elif severity == '中度':
        medical_cost = random.randint(5000, 25000)
        days_off = random.randint(7, 45)
    else:  # 轻度
        medical_cost = random.randint(500, 6000)
        days_off = random.randint(0, 10)
    
    injuries.append([
        i,  # injury_id
        incident[0],  # incident_id
        incident[2],  # employee_id (incident 中的 employee_id)
        random.choice(injury_types),  # injury_type
        random.choice(body_parts),  # body_part
        severity,  # severity (与事故严重程度一致)
        medical_cost,  # medical_cost
        days_off  # days_off_work
    ])

# 保存 injuries.csv
with open(os.path.join(output_dir, 'injuries.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['injury_id', 'incident_id', 'employee_id', 'injury_type', 'body_part', 'severity', 'medical_cost', 'days_off_work'])
    writer.writerows(injuries)
print(f"✅ 生成 {len(injuries)} 条伤害数据")

# ========== 5. 生成 Claims (1,500条) ==========
print("📋 生成 Claims...")
# 从 injuries 中随机选一部分作为有索赔的伤害
selected_injuries = random.sample(injuries, min(NUM_CLAIMS, len(injuries)))

claims = []
for i in range(1, NUM_CLAIMS + 1):
    injury = selected_injuries[i - 1] if i <= len(selected_injuries) else random.choice(injuries)
    
    # 根据伤害严重程度调整索赔金额
    severity = injury[5]  # severity
    if severity == '致命':
        claim_amount = random.randint(100000, 500000)
    elif severity == '重度':
        claim_amount = random.randint(50000, 150000)
    elif severity == '中度':
        claim_amount = random.randint(10000, 60000)
    else:  # 轻度
        claim_amount = random.randint(1000, 15000)
    
    # 索赔日期在事故之后
    incident = next(inc for inc in incidents if inc[0] == injury[1])
    incident_date = datetime.strptime(incident[3], '%Y-%m-%d').date()
    claim_date = fake.date_between(start_date=incident_date, end_date='today')
    
    claims.append([
        i,  # claim_id
        injury[0],  # injury_id
        injury[2],  # employee_id
        claim_date.strftime('%Y-%m-%d'),  # claim_date
        random.choice(claim_types),  # claim_type
        claim_amount,  # claim_amount
        random.choice(claim_statuses)  # claim_status
    ])

# 保存 claims.csv
with open(os.path.join(output_dir, 'claims.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['claim_id', 'injury_id', 'employee_id', 'claim_date', 'claim_type', 'claim_amount', 'claim_status'])
    writer.writerows(claims)
print(f"✅ 生成 {len(claims)} 条索赔数据")

# ========== 总结 ==========
print("\n" + "="*50)
print("🎉 所有数据生成完成！")
print(f"📁 保存位置: {os.path.abspath(output_dir)}")
print("="*50)
print(f"  • organisations: {len(organisations)} 条")
print(f"  • employees:     {len(employees)} 条")
print(f"  • incidents:     {len(incidents)} 条")
print(f"  • injuries:      {len(injuries)} 条")
print(f"  • claims:        {len(claims)} 条")
print("="*50)

# 验证外键关系
print("\n🔍 数据关系验证:")
print(f"  • 每个员工都关联到一个组织 (org_id 1-{NUM_ORGANISATIONS})")
print(f"  • 每个事故都关联到员工和组织")
print(f"  • {len(selected_incidents)} 个事故关联了伤害记录")
print(f"  • {len(selected_injuries)} 个伤害关联了索赔记录")
print("\n💡 提示: 使用 PostgreSQL 的 COPY 命令或 \\COPY 导入这些 CSV 文件")