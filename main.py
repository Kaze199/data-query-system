import sys
import os
import csv
import time
import odbc_lite as pyodbc
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MDBQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据查询系统")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        self.connection = None
        self.current_table = None
        self.current_data = None
        self.current_columns = []
        self.data_source_kind = "None"
        self.primary_key = None
        
        self.edit_history = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        top_frame = ttk.LabelFrame(self.root, text="数据库连接", padding="8")
        top_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        ttk.Button(top_frame, text="选择数据库", command=self._open_database, width=12).grid(row=0, column=0, padx=2)
        ttk.Button(top_frame, text="SQL Server", command=self._open_sql_server, width=12).grid(row=0, column=1, padx=2)
        self.lbl_db = ttk.Label(top_frame, text="未连接数据源", foreground="gray")
        self.lbl_db.grid(row=0, column=2, padx=10, sticky="w")
        
        query_frame = ttk.LabelFrame(self.root, text="查询条件", padding="8")
        query_frame.pack(fill=tk.X, padx=8, pady=(4, 4))
        
        ttk.Label(query_frame, text="数据表:").grid(row=0, column=0, sticky="w", pady=2)
        self.cmb_tables = ttk.Combobox(query_frame, state="readonly", width=20)
        self.cmb_tables.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.cmb_tables.bind("<<ComboboxSelected>>", self._on_table_selected)
        
        ttk.Label(query_frame, text="关键词:").grid(row=0, column=2, sticky="w", padx=(15, 0), pady=2)
        self.txt_keyword = ttk.Entry(query_frame, width=15)
        self.txt_keyword.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(query_frame, text="字段:").grid(row=0, column=4, sticky="w", padx=(15, 0), pady=2)
        self.cmb_fields = ttk.Combobox(query_frame, width=20)
        self.cmb_fields.grid(row=0, column=5, sticky="w", padx=5, pady=2)
        self.cmb_fields.bind("<<ComboboxSelected>>", self._on_field_selected)
        
        ttk.Label(query_frame, text="字段值:").grid(row=0, column=6, sticky="w", padx=(15, 0), pady=2)
        self.txt_field_value = ttk.Entry(query_frame, width=15)
        self.txt_field_value.grid(row=0, column=7, sticky="w", padx=5, pady=2)
        
        ttk.Label(query_frame, text="最多:").grid(row=0, column=8, sticky="w", padx=(15, 0), pady=2)
        self.num_limit = ttk.Spinbox(query_frame, from_=0, to=100000, increment=100, width=10)
        self.num_limit.set(1000)
        self.num_limit.grid(row=0, column=9, sticky="w", padx=5, pady=2)
        ttk.Label(query_frame, text="条").grid(row=0, column=10, sticky="w", pady=2)
        
        btn_frame = ttk.Frame(query_frame)
        btn_frame.grid(row=1, column=0, columnspan=8, sticky="e", pady=2)
        ttk.Button(btn_frame, text="查询", command=self._run_query, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导出CSV", command=self._export_csv, width=10).pack(side=tk.LEFT, padx=2)
        
        self.lbl_status = ttk.Label(self.root, text="请选择数据库开始。", relief=tk.SUNKEN, anchor="w")
        self.lbl_status.pack(fill=tk.X, padx=8, pady=(4, 4))
        
        edit_frame = ttk.LabelFrame(self.root, text="记录操作（选中行后输入列名和新值）", padding="8")
        edit_frame.pack(fill=tk.X, padx=8, pady=(4, 4))
        
        ttk.Label(edit_frame, text="列名:").grid(row=0, column=0, padx=5)
        self.txt_edit_col = ttk.Entry(edit_frame, width=15)
        self.txt_edit_col.grid(row=0, column=1, padx=5)
        
        ttk.Label(edit_frame, text="新值:").grid(row=0, column=2, padx=5)
        self.txt_new_value = ttk.Entry(edit_frame, width=30)
        self.txt_new_value.grid(row=0, column=3, padx=5)
        
        ttk.Button(edit_frame, text="应用修改", command=self._apply_edit, width=10).grid(row=0, column=4, padx=10)
        ttk.Button(edit_frame, text="撤回", command=self._undo_edit, width=10).grid(row=0, column=5, padx=10)
        ttk.Button(edit_frame, text="保存到数据库", command=self._save_changes, width=12).grid(row=0, column=6, padx=10)
        
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, show="headings", selectmode="browse")
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<Double-1>", self._on_double_click)
    
    def _escape_name(self, name):
        if self.data_source_kind == "SqlServer" and "." in name:
            parts = name.split(".")
            escaped = ["[" + p.replace("]", "]]") + "]" for p in parts]
            return ".".join(escaped)
        return "[" + name.replace("]", "]]") + "]"
    
    def _escape_like_value(self, value):
        return value.replace("'", "''").replace("[", "[[]")
    
    def _open_database(self):
        path = filedialog.askopenfilename(title="选择数据库文件", filetypes=[("Access 数据库", "*.mdb;*.accdb"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            self._close_connection()
            ext = os.path.splitext(path)[1].lower()
            drv_list = ["Microsoft Access Driver (*.mdb, *.accdb)"]
            if ext == ".mdb":
                drv_list.append("Microsoft Access Driver (*.mdb)")
            last_err = None
            for drv in drv_list:
                try:
                    conn_str = f"Driver={{{drv}}};DBQ={path};"
                    self.connection = pyodbc.connect(conn_str)
                    break
                except Exception as e:
                    last_err = e
            else:
                raise last_err
            self.data_source_kind = "Access"
            self.lbl_db.config(text=os.path.basename(path), foreground="black")
            self._load_tables()
            self.lbl_status.config(text="数据库已打开。")
        except Exception as e:
            messagebox.showerror("错误", f"打开数据库失败：{str(e)}")
    
    def _open_sql_server(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("连接 SQL Server")
        dialog.geometry("430x280")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="服务器:").place(x=24, y=24)
        txt_server = ttk.Entry(dialog, width=30)
        txt_server.place(x=100, y=20, width=280, height=28)
        txt_server.insert(0, "localhost")
        
        ttk.Label(dialog, text="数据库:").place(x=24, y=64)
        txt_database = ttk.Entry(dialog, width=30)
        txt_database.place(x=100, y=60, width=280, height=28)
        
        var_windows_auth = tk.BooleanVar(value=True)
        chk_windows = ttk.Checkbutton(dialog, text="使用 Windows 登录", variable=var_windows_auth)
        chk_windows.place(x=100, y=100)
        
        ttk.Label(dialog, text="用户名:").place(x=24, y=140)
        txt_user = ttk.Entry(dialog, width=30)
        txt_user.place(x=100, y=136, width=280, height=28)
        txt_user.config(state=tk.DISABLED)
        
        ttk.Label(dialog, text="密码:").place(x=24, y=180)
        txt_password = ttk.Entry(dialog, width=30, show="*")
        txt_password.place(x=100, y=176, width=280, height=28)
        txt_password.config(state=tk.DISABLED)
        
        def toggle_auth():
            state = tk.NORMAL if not var_windows_auth.get() else tk.DISABLED
            txt_user.config(state=state)
            txt_password.config(state=state)
        chk_windows.config(command=toggle_auth)
        
        def connect():
            server = txt_server.get().strip()
            database = txt_database.get().strip()
            if not server or not database:
                messagebox.showwarning("提示", "请填写服务器和数据库名称。")
                return
            try:
                self._close_connection()
                sql_drivers = [
                    "ODBC Driver 17 for SQL Server",
                    "ODBC Driver 13 for SQL Server",
                    "SQL Server Native Client 11.0",
                    "SQL Server",
                ]
                last_err = None
                for drv in sql_drivers:
                    try:
                        if var_windows_auth.get():
                            conn_str = f"Driver={{{drv}}};Server={server};Database={database};Trusted_Connection=yes;"
                        else:
                            conn_str = f"Driver={{{drv}}};Server={server};Database={database};UID={txt_user.get()};PWD={txt_password.get()};"
                        self.connection = pyodbc.connect(conn_str)
                        break
                    except Exception as e:
                        last_err = e
                else:
                    raise last_err
                self.data_source_kind = "SqlServer"
                self.lbl_db.config(text=f"{server}/{database}", foreground="black")
                self._load_tables()
                self.lbl_status.config(text="SQL Server 已连接。")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"连接失败：{str(e)}")
        
        ttk.Button(dialog, text="连接", command=connect).place(x=200, y=220, width=82, height=32)
        ttk.Button(dialog, text="取消", command=dialog.destroy).place(x=298, y=220, width=82, height=32)
    
    def _load_tables(self):
        self.cmb_tables["values"] = ()
        try:
            if self.data_source_kind == "SqlServer":
                cursor = self.connection.cursor()
                cursor.execute("SELECT TABLE_SCHEMA + '.' + TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME")
                tables = [row[0] for row in cursor.fetchall()]
            else:
                tables = []
                for row in self.connection.cursor().tables(tableType="TABLE"):
                    if not row.table_name.startswith("MSys"):
                        tables.append(row.table_name)
                tables.sort()
            self.cmb_tables["values"] = tables
            if tables:
                self.cmb_tables.current(0)
        except Exception as e:
            messagebox.showerror("错误", f"读取表失败：{str(e)}")
    
    def _get_table_columns(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT TOP 1 * FROM {self._escape_name(table_name)}")
        columns = []
        for col in cursor.description:
            col_info = {"name": col[0], "type": col[1], "nullable": col[6] if len(col) > 6 else True, "type_name": col[1]}
            if hasattr(pyodbc, 'SQL_TYPE_TIMESTAMP'):
                col_info["is_datetime"] = col[1] in [pyodbc.SQL_TYPE_DATE, pyodbc.SQL_TYPE_TIME, pyodbc.SQL_TYPE_TIMESTAMP]
            else:
                col_info["is_datetime"] = False
            columns.append(col_info)
        cursor.close()
        return columns
    
    def _get_primary_key(self, table_name):
        if self.data_source_kind == "SqlServer":
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = '{table_name.split('.')[-1]}' AND CONSTRAINT_NAME LIKE '%PK%'")
            pk = cursor.fetchone()
            cursor.close()
            return pk[0] if pk else None
        else:
            cursor = self.connection.cursor()
            try:
                cursor.execute(f"SELECT TOP 1 * FROM {self._escape_name(table_name)}")
                columns = [col[0] for col in cursor.description]
                cursor.close()
                return columns[0] if columns else None
            except:
                return None
    
    def _on_table_selected(self, event):
        table_name = self.cmb_tables.get()
        if not table_name:
            return
        try:
            self.current_table = table_name
            columns = self._get_table_columns(table_name)
            self.current_columns = columns
            self.primary_key = self._get_primary_key(table_name)
            col_names = [c["name"] for c in columns]
            self.cmb_fields["values"] = ["全部字段"] + col_names
            self.cmb_fields.current(0)
            self.lbl_status.config(text=f"已选表: {table_name}，主键: {self.primary_key or '未指定'}")
        except Exception as e:
            messagebox.showerror("错误", f"读取字段失败：{str(e)}")
    
    def _on_field_selected(self, event):
        pass
    
    def _run_query(self):
        if not self.connection or not self.cmb_tables.get():
            messagebox.showwarning("提示", "请先选择数据库和数据表。")
            return
        
        table_name = self.cmb_tables.get()
        keyword = self.txt_keyword.get().strip()
        field_name = self.cmb_fields.get() if self.cmb_fields.get() and self.cmb_fields.get() != "全部字段" else ""
        field_value = self.txt_field_value.get().strip()
        limit = int(self.num_limit.get())
        
        where_parts = []
        
        try:
            if keyword:
                columns = self._get_table_columns(table_name)
                blob_types = [pyodbc.SQL_BINARY, pyodbc.SQL_VARBINARY, pyodbc.SQL_LONGVARBINARY]
                or_parts = []
                for col in columns:
                    if col["type"] not in blob_types:
                        if self.data_source_kind == "SqlServer":
                            expr = f"ISNULL(CONVERT(NVARCHAR(MAX),{self._escape_name(col['name'])}),'')"
                        else:
                            expr = f"IIf(IsNull({self._escape_name(col['name'])}),'',CStr({self._escape_name(col['name'])}))"
                        or_parts.append(f"{expr} LIKE '%{self._escape_like_value(keyword)}%'")
                if or_parts:
                    where_parts.append("(" + " OR ".join(or_parts) + ")")
        except:
            pass
        
        if field_name and field_value:
            if self.data_source_kind == "SqlServer":
                expr = f"ISNULL(CONVERT(NVARCHAR(MAX),{self._escape_name(field_name)}),'')"
            else:
                expr = f"IIf(IsNull({self._escape_name(field_name)}),'',CStr({self._escape_name(field_name)}))"
            where_parts.append(f"{expr} LIKE '%{self._escape_like_value(field_value)}%'")
        
        top_clause = f"TOP {limit} " if limit > 0 else ""
        sql = f"SELECT {top_clause}* FROM {self._escape_name(table_name)}"
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        
        try:
            self.lbl_status.config(text="正在查询，请稍候...")
            self.root.update_idletasks()
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            cursor.close()
            
            self.current_data = {"columns": columns, "rows": rows}
            
            if not self.current_columns:
                self.current_columns = [{"name": col} for col in columns]
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, minwidth=50, stretch=True)
            
            row_count = 0
            for row in rows:
                values = ["" if val is None else str(val) for val in row]
                self.tree.insert("", tk.END, values=values)
                row_count += 1
            
            self.tree.update_idletasks()
            self.lbl_status.config(text=f"查询完成：{row_count} 条，{len(columns)} 列。可用列: {', '.join(columns)}")
        except Exception as e:
            import traceback
            messagebox.showerror("错误", f"查询失败：{str(e)}\n\n{traceback.format_exc()}")
            self.lbl_status.config(text="查询失败。")
    
    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        col_id = self.tree.identify_column(event.x)
        if not col_id or not col_id.startswith("#"):
            return
        
        try:
            col_index = int(col_id.replace("#", "")) - 1
        except:
            return
        
        values = self.tree.item(item, "values")
        if col_index < 0 or col_index >= len(values):
            return
        
        if self.current_data and self.current_data["columns"]:
            if col_index < len(self.current_data["columns"]):
                col_name = self.current_data["columns"][col_index]
                self.txt_edit_col.delete(0, tk.END)
                self.txt_edit_col.insert(0, col_name)
                self.txt_new_value.delete(0, tk.END)
                self.txt_new_value.insert(0, values[col_index])
                self.txt_new_value.focus()
                self.lbl_status.config(text=f"双击编辑: {col_name}")
    
    def _apply_edit(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一行记录。")
            return
        
        col_name_input = self.txt_edit_col.get().strip()
        if not col_name_input:
            messagebox.showwarning("提示", "请输入要编辑的列名。")
            return
        
        new_value = self.txt_new_value.get()
        
        if self.current_data and self.current_data["columns"]:
            columns = self.current_data["columns"]
        else:
            columns = [c["name"] for c in self.current_columns]
        
        col_index = -1
        for i, col in enumerate(columns):
            if col.lower() == col_name_input.lower():
                col_index = i
                col_name_input = col
                break
        
        if col_index == -1:
            messagebox.showerror("错误", f"未找到列名: {col_name_input}\n可用列名: {', '.join(columns)}")
            return
        
        item = selection[0]
        values = list(self.tree.item(item, "values"))
        
        if col_index >= len(values):
            messagebox.showerror("错误", f"列索引超出范围。")
            return
        
        old_value = values[col_index]
        self.edit_history.append({
            "item": item,
            "col_index": col_index,
            "old_value": old_value,
            "new_value": new_value,
            "col_name": col_name_input
        })
        
        values[col_index] = new_value
        self.tree.item(item, values=values)
        
        self.lbl_status.config(text=f"已修改：{col_name_input} = {new_value}（点击「保存到数据库」生效）")
    
    def _undo_edit(self):
        if not self.edit_history:
            messagebox.showwarning("提示", "没有可撤回的操作。")
            return
        
        last_edit = self.edit_history.pop()
        item = last_edit["item"]
        col_index = last_edit["col_index"]
        old_value = last_edit["old_value"]
        col_name = last_edit["col_name"]
        
        values = list(self.tree.item(item, "values"))
        values[col_index] = old_value
        self.tree.item(item, values=values)
        
        self.txt_edit_col.delete(0, tk.END)
        self.txt_edit_col.insert(0, col_name)
        self.txt_new_value.delete(0, tk.END)
        self.txt_new_value.insert(0, old_value)
        
        self.lbl_status.config(text=f"已撤回：{col_name} 恢复为 {old_value}")
    
    def _save_changes(self):
        if not self.connection or not self.current_table:
            messagebox.showwarning("提示", "请先选择数据库和数据表。")
            return
        
        if not self.primary_key:
            messagebox.showerror("错误", "无法保存：数据表没有主键。")
            return
        
        if not messagebox.askyesno("确认保存", "确定要保存所有修改到数据库吗？"):
            return
        
        try:
            cursor = self.connection.cursor()
            
            if self.current_data and self.current_data["columns"]:
                columns = self.current_data["columns"]
            else:
                columns = [c["name"] for c in self.current_columns]
            
            pk_index = -1
            for i, col in enumerate(columns):
                if col.lower() == self.primary_key.lower():
                    pk_index = i
                    break
            
            if pk_index == -1:
                messagebox.showerror("错误", f"无法确定主键位置。主键: {self.primary_key}")
                return
            
            update_count = 0
            for item in self.tree.get_children():
                values = self.tree.item(item, "values")
                pk_value = values[pk_index]
                
                sets = []
                params = []
                for i, col in enumerate(columns):
                    if i != pk_index:
                        sets.append(f"{self._escape_name(col)} = ?")
                        params.append(values[i] if values[i] != "" else None)
                
                params.append(pk_value)
                sql = f"UPDATE {self._escape_name(self.current_table)} SET {', '.join(sets)} WHERE {self._escape_name(self.primary_key)} = ?"
                cursor.execute(sql, params)
                update_count += 1
            
            self.connection.commit()
            cursor.close()
            
            self.edit_history = []
            self.lbl_status.config(text=f"保存成功！共更新 {update_count} 条记录。")
            messagebox.showinfo("成功", f"保存成功！共更新 {update_count} 条记录。")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def _export_csv(self):
        if not self.current_data or not self.current_data["rows"]:
            messagebox.showwarning("提示", "当前没有可导出的查询结果。")
            return
        path = filedialog.asksaveasfilename(title="保存 CSV 文件", defaultextension=".csv", filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")], initialfile=f"查询结果_{self.current_table}_{time.strftime('%Y%m%d_%H%M%S')}.csv")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.current_data["columns"])
                for row in self.current_data["rows"]:
                    writer.writerow(["" if val is None else str(val) for val in row])
            messagebox.showinfo("成功", f"导出完成！\n文件：{path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def _close_connection(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        self.data_source_kind = "None"
    
    def on_close(self):
        self._close_connection()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MDBQueryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
