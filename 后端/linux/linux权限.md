## ubuntu 查询开放端口

```bash
ss -tuln
```

## ubuntu 修改文件夹所属 所有者

1.  sudo chown newuser /path/to/folder 修改当前文件夹 
1.  sudo chown -R newuser /path/to/folder  子文件夹递归 // 慎用  容易搞崩系统

## ubutn 修改文件 文件夹权限 

chmod [权限选项] /path/to/folder

1. 755 所有者有读写执行权限，其他用户有读执行权限
2. 777 所有用户都有读写执行权限

    八进制模式：

    4 表示读权限

    2 表示写权限

    1 表示执行权限

    组合这些数字来表示所需的权限

    7 (4+2+1) 表示读、写和执行权限

    6 (4+2) 表示读和写权限

    5 (4+1) 表示读和执行权限

## ubuntu 查询 文件 文件夹 权限所属

ls -ld /path/to/example_folder

## 将当前文件夹权限给到当前用户
chmod -R 777 .