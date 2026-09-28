"""
odbc_lite - 纯 ctypes ODBC 包装器
提供与 pyodbc 兼容的接口，无需安装任何第三方包。
直接调用 Windows 系统自带的 odbc32.dll，支持 Win7 及以上系统。
"""

import ctypes
from ctypes import (
    byref, c_void_p, c_short, c_ushort, c_int, c_uint,
    c_size_t, c_ssize_t, c_wchar_p, create_unicode_buffer, POINTER,
)

# ── 加载 ODBC 库 ──────────────────────────────────────────
_odbc = ctypes.windll.odbc32

# ── 类型定义（64 位 Windows）──────────────────────────────
SQLHANDLE  = c_void_p
SQLHENV    = c_void_p
SQLHDBC    = c_void_p
SQLHSTMT   = c_void_p
SQLSMALLINT  = c_short
SQLUSMALLINT = c_ushort
SQLINTEGER   = c_int
SQLUINTEGER  = c_uint
SQLLEN  = c_ssize_t
SQLULEN = c_size_t
SQLRETURN = SQLSMALLINT

# ── 常量 ──────────────────────────────────────────────────
SQL_HANDLE_ENV  = 1
SQL_HANDLE_DBC  = 2
SQL_HANDLE_STMT = 3

SQL_ATTR_ODBC_VERSION = 200
SQL_OV_ODBC3 = 3

SQL_DRIVER_NOPROMPT   = 0
SQL_DRIVER_COMPLETE   = 1

SQL_SUCCESS           = 0
SQL_SUCCESS_WITH_INFO = 1
SQL_NO_DATA           = 100
SQL_ERROR             = -1
SQL_INVALID_HANDLE    = -2
SQL_NULL_HANDLE       = 0

SQL_NTS        = -3
SQL_NULL_DATA  = -1
SQL_NO_TOTAL   = -4
SQL_DATA_AT_EXEC = -4

SQL_COMMIT   = 0
SQL_ROLLBACK = 1

SQL_PARAM_INPUT = 1

# C 数据类型（用于 SQLGetData / SQLBindParameter）
SQL_C_CHAR    = 1
SQL_C_LONG    = 4
SQL_C_DOUBLE  = 8
SQL_C_DEFAULT = 99
SQL_C_WCHAR   = -8
SQL_C_BINARY  = -3

# SQL 数据类型
SQL_UNKNOWN_TYPE = 0
SQL_CHAR         = 1
SQL_NUMERIC      = 2
SQL_DECIMAL      = 3
SQL_INTEGER      = 4
SQL_SMALLINT     = 5
SQL_FLOAT        = 6
SQL_REAL         = 7
SQL_DOUBLE       = 8
SQL_DATETIME     = 9
SQL_DATE         = 9
SQL_INTERVAL     = 10
SQL_TIME         = 10
SQL_TIMESTAMP    = 11
SQL_VARCHAR      = 12
SQL_TYPE_DATE      = 91
SQL_TYPE_TIME      = 92
SQL_TYPE_TIMESTAMP = 93
SQL_LONGVARCHAR  = -1
SQL_BINARY       = -2
SQL_VARBINARY    = -3
SQL_LONGVARBINARY = -4
SQL_BIGINT       = -5
SQL_TINYINT      = -6
SQL_BIT          = -7
SQL_WCHAR        = -8
SQL_WVARCHAR     = -9
SQL_WLONGVARCHAR = -10
SQL_GUID         = -11

SQL_NULLABLE         = 1
SQL_NO_NULLS         = 0
SQL_NULLABLE_UNKNOWN = 2

# ── 函数原型 ──────────────────────────────────────────────
_odbc.SQLAllocHandle.argtypes = [SQLSMALLINT, SQLHANDLE, POINTER(SQLHANDLE)]
_odbc.SQLAllocHandle.restype  = SQLRETURN

_odbc.SQLSetEnvAttr.argtypes = [SQLHENV, SQLINTEGER, c_void_p, SQLINTEGER]
_odbc.SQLSetEnvAttr.restype  = SQLRETURN

_odbc.SQLDriverConnectW.argtypes = [
    SQLHDBC, c_void_p, c_wchar_p, SQLSMALLINT,
    c_wchar_p, SQLSMALLINT, POINTER(SQLSMALLINT), SQLUSMALLINT,
]
_odbc.SQLDriverConnectW.restype = SQLRETURN

_odbc.SQLDisconnect.argtypes = [SQLHDBC]
_odbc.SQLDisconnect.restype  = SQLRETURN

_odbc.SQLAllocStmt.argtypes = [SQLHDBC, POINTER(SQLHSTMT)]
_odbc.SQLAllocStmt.restype  = SQLRETURN

_odbc.SQLExecDirectW.argtypes = [SQLHSTMT, c_wchar_p, SQLINTEGER]
_odbc.SQLExecDirectW.restype  = SQLRETURN

_odbc.SQLPrepareW.argtypes = [SQLHSTMT, c_wchar_p, SQLINTEGER]
_odbc.SQLPrepareW.restype  = SQLRETURN

_odbc.SQLBindParameter.argtypes = [
    SQLHSTMT, SQLUSMALLINT, SQLSMALLINT, SQLSMALLINT, SQLSMALLINT,
    SQLULEN, SQLSMALLINT, c_void_p, SQLLEN, POINTER(SQLLEN),
]
_odbc.SQLBindParameter.restype = SQLRETURN

_odbc.SQLExecute.argtypes = [SQLHSTMT]
_odbc.SQLExecute.restype  = SQLRETURN

_odbc.SQLNumResultCols.argtypes = [SQLHSTMT, POINTER(SQLSMALLINT)]
_odbc.SQLNumResultCols.restype  = SQLRETURN

_odbc.SQLDescribeColW.argtypes = [
    SQLHSTMT, SQLUSMALLINT, c_wchar_p, SQLSMALLINT,
    POINTER(SQLSMALLINT), POINTER(SQLSMALLINT), POINTER(SQLULEN),
    POINTER(SQLSMALLINT), POINTER(SQLSMALLINT),
]
_odbc.SQLDescribeColW.restype = SQLRETURN

_odbc.SQLFetch.argtypes = [SQLHSTMT]
_odbc.SQLFetch.restype  = SQLRETURN

_odbc.SQLGetData.argtypes = [
    SQLHSTMT, SQLUSMALLINT, SQLSMALLINT,
    c_void_p, SQLLEN, POINTER(SQLLEN),
]
_odbc.SQLGetData.restype = SQLRETURN

_odbc.SQLTablesW.argtypes = [
    SQLHSTMT, c_wchar_p, SQLSMALLINT,
    c_wchar_p, SQLSMALLINT,
    c_wchar_p, SQLSMALLINT,
    c_wchar_p, SQLSMALLINT,
]
_odbc.SQLTablesW.restype = SQLRETURN

_odbc.SQLRowCount.argtypes = [SQLHSTMT, POINTER(SQLLEN)]
_odbc.SQLRowCount.restype  = SQLRETURN

_odbc.SQLEndTran.argtypes = [SQLSMALLINT, SQLHANDLE, SQLSMALLINT]
_odbc.SQLEndTran.restype  = SQLRETURN

_odbc.SQLFreeHandle.argtypes = [SQLSMALLINT, SQLHANDLE]
_odbc.SQLFreeHandle.restype  = SQLRETURN

_odbc.SQLGetDiagRecW.argtypes = [
    SQLSMALLINT, SQLHANDLE, SQLSMALLINT,
    c_wchar_p, POINTER(SQLINTEGER),
    c_wchar_p, SQLSMALLINT, POINTER(SQLSMALLINT),
]
_odbc.SQLGetDiagRecW.restype = SQLRETURN


# ── 异常 ──────────────────────────────────────────────────
class DatabaseError(Exception):
    pass


def _get_diag(handle_type, handle):
    """读取 ODBC 诊断记录，返回错误描述字符串。"""
    sqlstate = create_unicode_buffer(6)
    message  = create_unicode_buffer(1024)
    native    = SQLINTEGER(0)
    text_len  = SQLSMALLINT(0)
    parts = []
    for i in range(1, 8):
        ret = _odbc.SQLGetDiagRecW(
            handle_type, handle, i,
            sqlstate, byref(native),
            message, 1024, byref(text_len),
        )
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            break
        parts.append(message.value)
    return "; ".join(parts) if parts else "未知 ODBC 错误"


# ── Row 类（模拟 pyodbc.Row）──────────────────────────────
class Row:
    """支持索引访问和属性访问的行对象。"""
    def __init__(self, values, col_names=None):
        self._values = list(values)
        self._col_names = col_names or []
        for i, name in enumerate(self._col_names):
            safe = name.lower().replace(" ", "_").replace(".", "_")
            if safe and not safe[0].isdigit():
                setattr(self, safe, self._values[i])

    def __getitem__(self, index):
        return self._values[index]

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return repr(tuple(self._values))


# ── Cursor 类 ─────────────────────────────────────────────
class Cursor:
    def __init__(self, conn):
        self._conn = conn
        self._stmt = SQLHANDLE(0)
        self._description = None
        self._col_names = []
        self._col_types = []
        self._param_refs = []

        ret = _odbc.SQLAllocHandle(SQL_HANDLE_STMT, conn._dbc, byref(self._stmt))
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            raise DatabaseError(_get_diag(SQL_HANDLE_DBC, conn._dbc))

    # ── 属性 ──
    @property
    def description(self):
        return self._description

    # ── 内部方法 ──
    def _check(self, ret, ht=None, h=None):
        if ret == SQL_SUCCESS or ret == SQL_SUCCESS_WITH_INFO:
            return
        if ht is None:
            ht = SQL_HANDLE_STMT
            h  = self._stmt
        raise DatabaseError(_get_diag(ht, h))

    def _refresh_description(self):
        """执行 SQL 后刷新列信息。"""
        num_cols = SQLSMALLINT(0)
        _odbc.SQLNumResultCols(self._stmt, byref(num_cols))
        n = num_cols.value
        if n == 0:
            self._description = None
            self._col_names = []
            self._col_types = []
            return

        desc = []
        names = []
        types = []
        for i in range(1, n + 1):
            col_name = create_unicode_buffer(256)
            name_len = SQLSMALLINT(0)
            data_type = SQLSMALLINT(0)
            col_size  = SQLULEN(0)
            decimals  = SQLSMALLINT(0)
            nullable  = SQLSMALLINT(0)
            _odbc.SQLDescribeColW(
                self._stmt, i, col_name, 256, byref(name_len),
                byref(data_type), byref(col_size), byref(decimals), byref(nullable),
            )
            cname = col_name.value
            names.append(cname)
            types.append(data_type.value)
            desc.append((
                cname,             # 0: name
                data_type.value,   # 1: type code
                col_size.value,    # 2: display size
                col_size.value,    # 3: internal size
                col_size.value,    # 4: precision
                decimals.value,    # 5: scale
                nullable.value == SQL_NULLABLE,  # 6: null_ok
            ))
        self._description = desc
        self._col_names = names
        self._col_types = types

    def _fetch_row(self):
        """fetch 一行，返回 Row 或 None。"""
        ret = _odbc.SQLFetch(self._stmt)
        if ret == SQL_NO_DATA:
            return None
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            raise DatabaseError(_get_diag(SQL_HANDLE_STMT, self._stmt))

        values = []
        for i in range(1, len(self._col_names) + 1):
            values.append(self._get_col_data(i))
        return Row(values, self._col_names)

    def _get_col_data(self, col_num):
        """用 SQLGetData 获取一列数据，自动处理截断。"""
        buf_chars = 8192
        buf = create_unicode_buffer(buf_chars)
        indicator = SQLLEN(0)

        ret = _odbc.SQLGetData(
            self._stmt, col_num, SQL_C_WCHAR,
            buf, buf_chars * 2, byref(indicator),
        )

        if ret == SQL_ERROR:
            raise DatabaseError(_get_diag(SQL_HANDLE_STMT, self._stmt))

        if indicator.value == SQL_NULL_DATA:
            return None

        if ret == SQL_SUCCESS:
            if indicator.value >= 0:
                nc = indicator.value // 2
                return buf.value[:nc] if nc < len(buf.value) else buf.value
            return buf.value

        # SQL_SUCCESS_WITH_INFO — 数据被截断，需要继续读取
        chunks = [buf.value]
        while True:
            buf2 = create_unicode_buffer(buf_chars)
            ind2 = SQLLEN(0)
            r2 = _odbc.SQLGetData(
                self._stmt, col_num, SQL_C_WCHAR,
                buf2, buf_chars * 2, byref(ind2),
            )
            if r2 == SQL_ERROR:
                raise DatabaseError(_get_diag(SQL_HANDLE_STMT, self._stmt))
            if ind2.value == SQL_NULL_DATA:
                break
            if r2 == SQL_SUCCESS:
                if ind2.value >= 0:
                    nc = ind2.value // 2
                    chunks.append(buf2.value[:nc] if nc < len(buf2.value) else buf2.value)
                else:
                    chunks.append(buf2.value)
                break
            # 仍然截断
            chunks.append(buf2.value)
        return "".join(chunks)

    # ── 公开方法 ──
    def execute(self, sql, params=None):
        self._param_refs = []

        if params:
            ret = _odbc.SQLPrepareW(self._stmt, sql, SQL_NTS)
            self._check(ret)

            for i, p in enumerate(params):
                pnum = i + 1
                if p is None:
                    ind = SQLLEN(SQL_NULL_DATA)
                    self._param_refs.append(ind)
                    r = _odbc.SQLBindParameter(
                        self._stmt, pnum, SQL_PARAM_INPUT,
                        SQL_C_WCHAR, SQL_WVARCHAR,
                        1, 0, None, 0, byref(ind),
                    )
                    self._check(r)
                else:
                    s = str(p)
                    buf = create_unicode_buffer(s)
                    slen = len(s)
                    ind = SQLLEN(slen * 2)
                    self._param_refs.append((buf, ind))
                    r = _odbc.SQLBindParameter(
                        self._stmt, pnum, SQL_PARAM_INPUT,
                        SQL_C_WCHAR, SQL_WVARCHAR,
                        slen if slen > 0 else 1, 0,
                        buf, slen * 2, byref(ind),
                    )
                    self._check(r)

            ret = _odbc.SQLExecute(self._stmt)
            self._check(ret)
        else:
            ret = _odbc.SQLExecDirectW(self._stmt, sql, SQL_NTS)
            self._check(ret)

        self._refresh_description()
        return self

    def fetchone(self):
        if not self._description:
            return None
        return self._fetch_row()

    def fetchall(self):
        if not self._description:
            return []
        rows = []
        while True:
            row = self._fetch_row()
            if row is None:
                break
            rows.append(row)
        return rows

    def tables(self, tableType=None):
        """返回表列表，每行包含 table_name 属性。"""
        tt = tableType if tableType else None
        ret = _odbc.SQLTablesW(
            self._stmt,
            None, 0,       # catalog
            None, 0,       # schema
            None, 0,       # table
            tt, SQL_NTS if tt else 0,  # type
        )
        self._check(ret)
        self._refresh_description()
        return self.fetchall()

    def close(self):
        if self._stmt.value:
            _odbc.SQLFreeHandle(SQL_HANDLE_STMT, self._stmt)
            self._stmt = SQLHANDLE(0)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


# ── Connection 类 ─────────────────────────────────────────
class Connection:
    def __init__(self, conn_str):
        self._env = SQLHANDLE(0)
        self._dbc  = SQLHANDLE(0)

        # 分配环境句柄
        ret = _odbc.SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, byref(self._env))
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            raise DatabaseError("无法分配 ODBC 环境句柄")

        _odbc.SQLSetEnvAttr(self._env, SQL_ATTR_ODBC_VERSION, SQL_OV_ODBC3, 0)

        # 分配连接句柄
        ret = _odbc.SQLAllocHandle(SQL_HANDLE_DBC, self._env, byref(self._dbc))
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            raise DatabaseError(_get_diag(SQL_HANDLE_ENV, self._env))

        # 连接
        out_buf = create_unicode_buffer(1024)
        out_len = SQLSMALLINT(0)
        ret = _odbc.SQLDriverConnectW(
            self._dbc, 0, conn_str, SQL_NTS,
            out_buf, 1024, byref(out_len), SQL_DRIVER_NOPROMPT,
        )
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            msg = _get_diag(SQL_HANDLE_DBC, self._dbc)
            raise DatabaseError(msg)

    def cursor(self):
        return Cursor(self)

    def commit(self):
        _odbc.SQLEndTran(SQL_HANDLE_DBC, self._dbc, SQL_COMMIT)

    def rollback(self):
        _odbc.SQLEndTran(SQL_HANDLE_DBC, self._dbc, SQL_ROLLBACK)

    def close(self):
        if self._dbc.value:
            _odbc.SQLDisconnect(self._dbc)
            _odbc.SQLFreeHandle(SQL_HANDLE_DBC, self._dbc)
            self._dbc = SQLHANDLE(0)
        if self._env.value:
            _odbc.SQLFreeHandle(SQL_HANDLE_ENV, self._env)
            self._env = SQLHANDLE(0)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


# ── 模块级函数 ────────────────────────────────────────────
def connect(conn_str):
    """连接数据库，conn_str 格式与 pyodbc 相同。"""
    return Connection(conn_str)


def drivers():
    """列出已安装的 ODBC 驱动名称。"""
    env = SQLHANDLE(0)
    _odbc.SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, byref(env))
    _odbc.SQLSetEnvAttr(env, SQL_ATTR_ODBC_VERSION, SQL_OV_ODBC3, 0)

    desc = create_unicode_buffer(1024)
    desc_len = SQLSMALLINT(0)
    direction = SQL_FETCH_FIRST   # 2
    result = []
    while True:
        ret = _odbc.SQLDriversW(
            env, direction,
            desc, 1024, byref(desc_len),
            None, 0, None,
        )
        direction = SQL_FETCH_NEXT   # 1
        if ret != SQL_SUCCESS and ret != SQL_SUCCESS_WITH_INFO:
            break
        result.append(desc.value)
    _odbc.SQLFreeHandle(SQL_HANDLE_ENV, env)
    return result


# SQLDrivers 常量
SQL_FETCH_FIRST = 2
SQL_FETCH_NEXT  = 1

# SQLDriversW 原型
_odbc.SQLDriversW.argtypes = [
    SQLHENV, SQLUSMALLINT,
    c_wchar_p, SQLSMALLINT, POINTER(SQLSMALLINT),
    c_wchar_p, SQLSMALLINT, POINTER(SQLSMALLINT),
]
_odbc.SQLDriversW.restype = SQLRETURN
