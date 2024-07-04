   
CREATE_USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS USERS(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT, 
    birthday TEXT,
    preferred_payment_method TEXT,
    default_split_percentage REAL DEFAULT 0,
    insert_date TEXT
    )
"""

CREATE_TABS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS TABS(
    tab_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    total_amount REAL,
    description TEXT,
    emoji TEXT,
    created_date TEXT
)
"""

CREATE_USER_TAB_MAP_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS USER_TAB_MAP(
    user_id INTEGER,
    tab_id INTEGER,
    amount_owed REAL DEFAULT 0,
    paid INTEGER DEFAULT 0,
    recipient INTEGER DEFAULT 0,
    PRIMARY KEY(user_id,tab_id)
    )
"""

CREATE_USER_PAYMENTS_MAP_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS USER_PAYMENTS_MAP(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    tab_id INTEGER,
    amount REAL,
    payment_date TEXT
)
"""

CREATE_USER_PAYMENT_STATUS_VIEW_SQL  = """ 
CREATE VIEW IF NOT EXISTS USER_PAYMENT_STATUS 
AS
WITH AGGREGATED_USER_PAYMENTS as (
    SELECT 
    up.user_id,
    up.tab_id,
    SUM(CAST(up.amount as REAL)) as payment_amount
    FROM USER_PAYMENTS_MAP up 
    GROUP BY up.user_id, up.tab_id
),
PAYMENT_TAB_MAPPING AS(
    SELECT 
    u.name, 
    utm.user_id, 
    utm.tab_id, 
    utm.amount_owed,
    utm.amount_owed - COALESCE(aup.payment_amount, 0) AS amount_remaining
    FROM USERS u
    INNER JOIN USER_TAB_MAP utm on u.user_id = utm.user_id
    LEFT JOIN AGGREGATED_USER_PAYMENTS aup 
        on aup.tab_id = utm.tab_id
        and aup.user_id = utm.user_id
    WHERE utm.paid = 0 and utm.recipient = 0
)
SELECT 
ptm.name, 
ptm.user_id,
ptm.tab_id,
utm.user_id as recipient_user_id,
t.created_date,
ptm.amount_owed,
ptm.amount_remaining,
ptm.amount_remaining <= 0 as paid,
ptm.amount_remaining < 0 as over_paid
FROM TABS t
INNER JOIN PAYMENT_TAB_MAPPING ptm
    on t.tab_id = ptm.tab_id
INNER JOIN USER_TAB_MAP utm
    on ptm.tab_id = utm.tab_id 
    and utm.recipient = 1
"""

TABLE_DDL = [
    CREATE_USER_TABLE_SQL, 
    CREATE_TABS_TABLE_SQL, 
    CREATE_USER_TAB_MAP_TABLE_SQL, 
    CREATE_USER_PAYMENTS_MAP_TABLE_SQL, 
    CREATE_USER_PAYMENT_STATUS_VIEW_SQL
    ]
