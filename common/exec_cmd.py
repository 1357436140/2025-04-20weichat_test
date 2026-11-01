# -*- coding: utf-8 -*-

# @author: Jason
# @File: exec_cmd.py
# @Time: 4月 20, 2025
# @description: 执行命令


import subprocess
import platform


class ExecuteCommand:

    def __init__(self, serial=None, shell=False):
        self.serial = serial
        self.shell = shell
        os_type = platform.system()
        if os_type == "Linux" or os_type == "Darwin":
            self.shell = True

    def execute_shell(self, cmd):
        '''
        description: 执行adb shell命令，不返回命令行结果
        :param cmd: adb shell 命令，如：adb shell ls /data/local/tmp 输入ls /data/local/tmp即可
        :param shell: 是否使用shell执行命令
        :return:
        '''
        if self.serial is None:
            target_cmd = "adb shell {}".format(cmd)
        else:
            target_cmd = "adb -s {0} shell {1}".format(self.serial, cmd)
        Process = subprocess.Popen(target_cmd, shell=self.shell)

    def execute_shell_output(self, cmd):
        '''
        description: 执行adb shell命令，返回执行结果
        :param cmd: adb shell 命令，如：adb shell ls /data/local/tmp 输入ls /data/local/tmp即可
        :param shell: 是否使用shell执行命令
        :return: cmd窗口的输出，列表格式
        '''
        if self.serial is None:
            target_cmd = "adb shell {}".format(cmd)
        else:
            target_cmd = "adb -s {0} shell {1}".format(self.serial, cmd)
        Process = subprocess.Popen(target_cmd, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, errors='ignore')
        out = [res.replace('\n', '') for res in Process.stdout.readlines()]
        err = [res.replace('\n', '') for res in Process.stderr.readlines()]
        return out + err

    def execute_shell_output_str(self, cmd):
        '''
        description: 执行adb shell命令，返回执行结果
        :param cmd: adb shell 命令，如：adb shell ls /data/local/tmp 输入ls /data/local/tmp即可
        :param shell: 是否使用shell执行命令
        :return: cmd窗口的输出，字符串格式
        '''
        return "\n".join(self.execute_shell_output(cmd))

    def execute_adb(self, cmd):
        '''
        description: 执行adb命令，不返回adb窗口的输出
        :param cmd: adb命令, 参数无需输入adb，如：adb root 输入root即可
        :param shell: 是否使用shell执行命令
        :return:
        '''
        if not self.serial:
            target_cmd = "adb -s {0}".format(cmd)
        else:
            target_cmd = "adb -s {0} {1}".format(self.serial, cmd)
        Process = subprocess.Popen(target_cmd, shell=self.shell)

    def execute_adb_output(self, cmd):
        '''
        description: 执行adb命令，返回命令行结果
        :param cmd: adb命令, 参数无需输入adb，如：adb root 输入root即可
        :param shell: 是否使用shell执行命令
        :return: 返回cmd窗口的输出，列表格式
        '''
        if not self.serial:
            target_cmd = "adb -s {0}".format(cmd)
        else:
            target_cmd = "adb -s {0} {1}".format(self.serial, cmd)
        Process = subprocess.Popen(target_cmd, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, errors='ignore')
        out = [res.replace('\n', '') for res in Process.stdout.readlines()]
        err = [res.replace('\n', '') for res in Process.stderr.readlines()]
        return out + err

    def execute_adb_output_str(self, cmd):
        '''
        description: 执行adb命令，返回命令行结果
        :param cmd: adb命令, 参数无需输入adb，如：adb root 输入root即可
        :param shell: 是否使用shell执行命令
        :return: 返回cmd窗口的输出，字符串格式
        '''
        return "\n".join(self.execute_adb_output(cmd))

    def execute_cmd(self, cmd):
        '''
        description: 执行cmd命令，不返回cmd窗口的输出
        :param cmd: cmd命令, 参数无需输入adb，如：adb root 输入adb root即可
        :param shell: 是否使用shell执行命令
        :return:
        '''
        Process = subprocess.Popen(cmd, shell=self.shell)

    def execute_cmd_output(self, cmd):
        '''
        description: 执行cmd命令，返回cmd窗口的结果
        :param cmd: cmd命令, 参数无需输入adb，如：adb root 输入adb root
        :param shell: 是否使用shell执行命令
        :return: 返回cmd窗口的输出，列表格式
        '''
        Process = subprocess.Popen(cmd, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, errors='ignore')
        out = [res.replace('\n', '') for res in Process.stdout.readlines()]
        err = [res.replace('\n', '') for res in Process.stderr.readlines()]
        return out + err

    def execute_cmd_output_str(self, cmd):
        '''
        description: 执行cmd命令，返回cmd窗口的结果
        :param cmd: cmd命令, 参数无需输入adb，如：adb root 输入adb root
        :param shell: 是否使用shell执行命令
        :return: 返回cmd窗口的输出，字符串格式
        '''
        return "\n".join(self.execute_cmd_output(cmd))

    def run_shell(self, cmds) -> list:
        '''
        description: 执行adb shell命令
        :param cmds: 支持list和str类型的shell命令
        :param shell:
        :return: list
        '''
        if self.serial is None:
            adb_cmds = ['adb', 'shell']
        else:
            adb_cmds = ['adb', '-s', self.serial, 'shell']
        if type(cmds) is list:
            adb_cmds.extend(cmds)
        elif type(cmds) is str:
            adb_cmds.append(cmds)
        else:
            return []
        Process = subprocess.Popen(adb_cmds, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = [res.decode(errors='ignore').strip() for res in Process.stdout.readlines()]
        err = [res.decode(errors='ignore').strip() for res in Process.stderr.readlines()]
        return out + err

    def run_shell_str(self, cmds) -> str:
        out = self.run_shell(cmds)
        return '\n'.join(out)

    def run_cmds(self, cmds: list) -> str:
        Process = subprocess.Popen(cmds, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        out = [res.decode(errors='ignore').strip() for res in Process.stdout.readlines()]
        return '\n'.join(out)


