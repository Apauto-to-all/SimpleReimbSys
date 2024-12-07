# 所有表的定义
# 用于生成数据库表
# 生成的表结构如下

tables_json = {
    "roles": {
        "role_id": "serial",  # 角色ID：自增整数
        "role_name": "varchar(50) not null UNIQUE",  # 角色名称：长度50，字符串，不能为空，唯一
        "primary_key": "(role_id)",  # 主键：role_id
    },
    "users": {
        "user_id": "serial",  # 用户ID：自增整数
        "username": "varchar(50) not null UNIQUE",  # 用户名：长度50，字符串，不能为空，唯一
        "password": "varchar(60) not null",  # 密码：长度60（加密后），字符串，不能为空
        "real_name": "varchar(50)",  # 真实姓名：长度50，字符串
        "role_id": "int not null references roles(role_id)",  # 角色ID，外键关联roles表
        "primary_key": "(user_id)",  # 主键：user_id
    },
    "categories": {  # 报销类别表
        "category_id": "serial",  # 类别ID：自增整数
        "category_name": "varchar(50) not null UNIQUE",  # 类别名称：长度50，字符串，不能为空，唯一
        "is_deleted": "boolean not null default false",  # 是否删除：布尔，不能为空，默认为 false
        "primary_key": "(category_id)",  # 主键：category_id
    },
    "categories_manager": {  # 财务人员负责类别表
        "finance_id": "int not null references users(user_id)",  # 财务人员ID，外键关联users表，且用户角色为财务人员
        "category_id": "int not null references categories(category_id)",  # 类别ID，外键关联categories表
        "primary_key": "(finance_id, category_id)",  # 组合主键：finance_id, category_id
    },
    "projects": {  # 项目表
        "project_id": "serial",  # 项目ID：自增整数
        "project_name": "text not null",  # 项目名称：字符串，不能为空
        "project_source": "text",  # 项目来源：字符串
        "category_id": "int not null references categories(category_id)",  # 类别ID，外键关联categories表
        "total_amount": "double precision",  # 立项金额：double
        "balance": "double precision",  # 余额：double
        "is_deleted": "boolean not null default false",  # 是否删除：布尔，不能为空，默认为 false
        "primary_key": "(project_id)",  # 主键：project_id
    },
    "projects_manager": {  # 报销人员可报销项目表
        "employee_id": "int not null references users(user_id)",  # 报销人员ID，外键关联users表
        "project_id": "int not null references projects(project_id)",  # 项目ID，外键关联projects表
        "primary_key": "(employee_id, project_id)",  # 组合主键：employee_id, project_id
    },
    "reimbursement_applications": {  # 报销审核表
        "reimbursement_id": "serial",  # 报销ID：自增整数
        "project_id": "int not null references projects(project_id)",  # 项目ID，外键关联projects表
        "employee_id": "int not null references users(user_id)",  # 报销人员ID，外键关联users表
        "finance_id": "int references users(user_id)",  # 财务人员ID，外键关联users表，报销前为空
        "amount": "double precision",  # 报销金额：double
        "description": "text",  # 报销描述：字符串
        "status": "varchar(10) not null",  # 报销状态：长度10，字符串，不能为空（待审核，已通过，已拒绝）
        "submit_date": "int",  # 提交日期：时间戳，int
        "approve_date": "int",  # 审核日期：时间戳，int
        "comments": "text",  # 审核意见：字符串
        "primary_key": "(reimbursement_id)",  # 主键：reimbursement_id
    },
}
