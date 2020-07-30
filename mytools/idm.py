from subprocess import call

"""
	使用：
	idman /s
	或
	idman /d URL [/p local_path] [/f local_file_name] [/q] [/h][/n] [/a]
	可以进行下载
	参数解释：
	/d URL  #根据URL下载文件
	/s      #开始下载队列中的任务
	/p      #定义文件要存储在本地的地址
	/f      #定义文件存储在本地的文件名
	/q      #下载成功后IDM将退出。
	/h      #下载成功后IDM将挂起你的链接
	/n      #当IDM不出问题时启动静默模式
	/a      #添加指定文件到/d的下载队列，但是不进行下载
————————————————
原文链接：https://blog.csdn.net/mrzhy1/article/details/104098007
"""

def add_to_idm_queue(file_url, save_path):
    IDM = r"D:\Software\Internet Download Manager 6.36.2\IDMan.exe"
    call([IDM, '/d', file_url, '/p', save_path, '/n', '/a'])

# if __name__ == '__main__':
#
#     add_to_idm_queue('https://files.yande.re/image/ca39a7c40c53d2c83887f18ba70dbfe7/yande.re%20611242%20peach_candy%20tagme%20yukie.png',
#       r'F:\Start_Here_Mac.app\Contents\yande_pool\a')