#!/usr/bin/env python

import paramiko, sys, time, email_report

from asa_config import ip_blocks, device_username, device_pass

ip_block_1, ip_block_2, ip_block_3 = ip_blocks

dnr_captures = []
dnr_capture_devices = []
captures_removed = []
device_with_error = []

with open('Capture_removal.log', 'w'): pass


def connect(ip):
    remote_connection = paramiko.SSHClient()
    remote_connection.set_missingh_host_key_policy(paramiko.AutoAddPolicy())
    remote_connection.connect(
    ip,
    username=device_username,
    password=device_pass,
    allow_agent=False,
    look_for_keys=False
    )
    get_captures(remote_connection, ip)


def get_captures(remote_connection, ip):
    ssh_shell = remote_connection.invoke_shell()
    ssh_shell.send('enable\n')
    ssh_shell.send(assured_password)
    ssh_shell.send('\n')
    ssh_shell.send('terminal pager 0\n')
    shell_output = ssh_shell.recv(10000)
    ssh_shell.send('show capture\n')
    time.sleep(1)
    shell_output = ssh_shell.recv(10000)
    time.sleep(1)
    capture_output = shell_output
    format_check(remote_connection, ssh_shell, capture_output, ip)


def format_check(remote_connection, ssh_shell, capture_output, ip):
    words_for_format = []
    captures = []
    capture_output_format = capture_output.split('show capture')[1]
    capture_output_eachline = capture_output_format.split('\n')
    capture_output_eachline.pop(-1)
    capture_output_eachline = [x for x in capture_output_eachline if x != '\r']
    for each_line in capture_output_eachline:
        each_word = each_line.split()
        words_for_format.append(each_word)
    for i in range(len(words_for_format)):
        captures.append(words_for_format[i][1])
    captures_format = captures[::2]
    for capture_name in captures_format:
        if ("dnr" in capture_name) or ("DNR" in capture_name):
            dnr_captures.append(capture_name)
            dnr_capture_devices.append(ip)
            print("stays")
        elif ("dnr" not in capture_name) or ("DNR" not in capture_name):
            captures_removed.append(capture_name)
            ssh_shell.send("no capture " + capture_name + '\n')
            time.sleep(1)
            print("goes")
    remote_connection.close()


def email_report_dnr():
    email_message = ("The packet capture removal script has been successfully run which has resulted in %s captures being removed.\n") % (str(len(captures_removed)))
    email_message += ("There are %s captures that contain dnr or DNR within their name and therefore have not been removed.\n") % (str(len(dnr_captures)))
    email_message += ("The following captures were excluded for this reason: \n")
    email_message += ('\n')
    for dnr_count in range(len(dnr_capture_devices)):
        email_message += str(dnr_capture_devices[dnr_count]) + ":\n"
        email_message += str(dnr_captures[dnr_count]) + "\n"
        email_message += ('\n')
    email_message += ('If any of these captures are no longer required could you please ensure that they are removed from the devices.')
    if len(device_with_error) > 0:
        email_message += "An Error occured on the following device(s):\n")
        email_message += ('\n')
        for error_count in range(len(device_with_error)):
            email_message += str(device_with_error[error_count]) + '\n'
        email_message += ('\n')
        email_message += ("Please check Capture_removal.log for more information")
    email_report.send_email_report(email_message)


def main():
    with open("Capture_removal.log", "a") as log_file:
        for ip_counter in range(len(ip_block_1)):
            each_ip = ip_block_1[ip_counter]
            try:
                print("Connecting to " + each_ip)
                connect(each_ip)
            except Exception as e:
                log_file.write(str(e))
                device_with_error.append(each_ip)
                pass
        for ip_counter in range(len(ip_block_2)):
            each_ip = ip_block_2[ip_counter]
            try:
                print("Connecting to " + each_ip)
                connect(each_ip)
            except Exception as e:
                log_file.write(str(e))
                device_with_error.append(each_ip)
                pass
        for ip_counter in range(len(ip_block_3)):
            each_ip = ip_block_3[ip_counter]
            try:
                print("Connecting to " + each_ip)
                connect(each_ip)
            except Exception as e:
                log_file.write(str(e))
                device_with_error.append(each_ip)
                pass
        email_report_dnr()


if __name__ == "__main__":
    main()
