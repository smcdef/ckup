#!/usr/bin/env python3
# 作者：宋牧春(smcdef@163.com)
#
import os
import sys
import datetime
import subprocess

# 文件跟踪路径，多个路径（相对路径）使用“，”隔开
ck_path = ['board/samsung/s5pv210_smc/', 'arch/arm/']
#ck_path = ['test']
# 源码修改目录文件路径(一般是共享文件夹路径)
src_code_path_cp_from = '/mnt/hgfs/winshare/uboot/u-boot-2017.01/'
#src_code_path_cp_from = "/mnt/hgfs/winshare/shell/from"
# 编译源码目录文件路径
src_code_path_cp_to = '/home/smc/workspace/uboot/uboot-2017.01/'
#src_code_path_cp_to = "/mnt/hgfs/winshare/shell/to"


def find_file_by_single_path(path):
    list_all = []
    filelist = os.listdir(path)
    for f in filelist:
        path_single = os.path.join(path, f)
        if os.path.isfile(path_single):
            m_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(path_single))
            file_name_time = path_single + ' ' + \
                m_time.strftime('%Y-%m-%d %H:%M:%S')
            list_all.append(file_name_time)
        elif os.path.isdir(path_single):
            list_all += (find_file_by_single_path(path_single))
    return list_all


def find_file_by_paths(path):
    list_all = []
    for path_single in path:
        list_all += find_file_by_single_path(path_single)
    return list_all


def get_full_path(path_prefix, path):
    path_tmp = []
    for i in range(0, len(path)):
        path_tmp.append(os.path.join(path_prefix, path[i]))

    return path_tmp


# 在path路径下创建log日志文件，并返回已经创建完成的log日志文件路径
# 默认是获取src_code_path_cp_from路径下文件的修改时间
def creat_log_file(log_path, src_code_path=src_code_path_cp_from, log_file_name='.now.log'):
    log_file_dir = os.path.join(log_path, log_file_name)
    file_list = find_file_by_paths(
        get_full_path(src_code_path, ck_path))
    fp = open(log_file_dir, 'w+')
    fp.writelines([line + '\n' for line in file_list])
    fp.close()

    return log_file_dir


# 比较file1和file2文件，如果file2文件更新则更新文件
def cmp_and_copy(file1, file2):
    shell_cmd = 'grep -vwf ' + file1 + ' ' + file2
    status, cmp_dif_out = subprocess.getstatusoutput(shell_cmd)

    # 有文件更新或者创建新文件
    if status == 0:
        # 输出信息按照'\n'拆分
        out_single = cmp_dif_out.split('\n')
        for line in out_single:
            line = line.split()
            cp_file_name = line[0].split(src_code_path_cp_from)[1]
            # os.path.join使用的时候必须保证第二个参数的开始不能是'/'，否则认为根目录
            if cp_file_name[0] == '/':
                cp_file_name = cp_file_name[1:-1]

            # 复制更新或者新建的文件
            shell_cmd = 'cp ' + \
                line[0] + ' ' + \
                os.path.join(src_code_path_cp_to, cp_file_name) + ' -f'
            os.system(shell_cmd)

            # 更新修改时间日志文件
            shell_cmd = 'cp ' + file2 + ' ' + file1 + ' -f'
            os.system(shell_cmd)

            # 输出提示信息，自带颜色
            print('\033[1;33m' + line[1] + " " + line[2] + '\033[0m   \033[1;36m' +
                  cp_file_name + '\033[0m\033[1;31m  update!\033[0m')

# 获得.ck_log路径
log_dir = os.path.join(src_code_path_cp_to, '.ck_log')
# 检查参数时候含有“clean”命令
if len(sys.argv) > 1:
    if sys.argv[1] == 'clean':
        shell_cmd = 'rm -rf ' + log_dir
        os.system(shell_cmd)
        sys.exit(0)

if os.path.exists(log_dir):
    now_log_file_dir = creat_log_file(log_dir)
    cmp_and_copy(os.path.join(log_dir, '.his.log'), now_log_file_dir)
else:
    os.mkdir(log_dir)
    now_log_file_dir = creat_log_file(log_dir)
    shell_cmd = 'cp ' + now_log_file_dir + ' ' + \
        os.path.join(log_dir, '.his.log') + ' -f'
    os.system(shell_cmd)
