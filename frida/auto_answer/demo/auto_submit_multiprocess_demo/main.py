# 只适配了比大小口算pk, 其他未测试
import argparse

from answer import Student
import concurrent.futures
import time

"""
通过 python main.py 启动时需要自己填写cookie和url
通过 python main.py --hookcookie 启动时会自动获取cookie和url
"""

"""
请填写cookie
(可能)只需要填下面3个关键cookie即可
ks_persistent, sess, userid
"""
cookies = {
    "YFD_U": "",
    "__sub_user_infos__": "",
    "g_loc": "",
    "g_sess": "",
    "ks_deviceid": "",
    "ks_persistent": "此处必填",
    "ks_sess": "",
    "persistent": "",
    "sess": "此处必填",
    "sid": "",
    "userid": "此处必填"
}

"""
此处填写获取试题答案和提交答案的url, 要带上参数, 每个人的YFD_U和version不一样, 但不会改变, 请自行抓包获取
注意把sign值替换成{sign}, 用于后续填充
"""
url = {
    "get_question": "https://xyks.yuanfudao.com/leo-game-pk/android/math/pk/match/v2?pointId=2&_productId=611&platform=android32&version=3.93.2&vendor=xiao_mi&av=5&sign={sign}&deviceCategory=pad",
    "submit_answer": "https://xyks.yuanfudao.com/leo-game-pk/android/math/pk/submit?_productId=611&platform=android32&version=3.93.2&vendor=xiao_mi&av=5&sign={sign}&deviceCategory=pad"
}

# cookie = hookcookie if cookie_type else cookies

"""
hook脚本位置, 保持默认的话, 请不要修改
"""
hook_script = {
    "jsFilePath_getSign": "hook/js/gan_sign_model.js",
    "jsFilePath_doMatchV2ByDataDecryptCommand": "hook/js/do_matchV2_byDataDecryptCommand_model.js",
    "jsFilePath_doAnswerEncrypt": "hook/js/do_answer_encrypt_model.js"
}

print(hook_script["jsFilePath_getSign"])

"""
单次测试执行
"""


# student = Student(cookies, url, "com.fenbi.android.leo", hook_script)
# student.answer()


# 封装执行逻辑的函数
def execute_student_task(cookies, url, hook_script):
    try:
        student = Student(cookies, url, "com.fenbi.android.leo", hook_script)
        student.answer()
    except Exception as e:
        print(f"Error occurred: {e}")


# 创建30个进程池，每个进程池不断执行任务
def run_student_tasks(cookies, url, hook_script, num_processes=30, timeout=5):
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        while True:
            # 提交任务到进程池中
            futures = {executor.submit(execute_student_task, cookies, url, hook_script): idx for idx in
                       range(num_processes)}

            # 监控每个任务的状态
            done, not_done = concurrent.futures.wait(futures, timeout=timeout,
                                                     return_when=concurrent.futures.FIRST_COMPLETED)

            # 处理完成的任务
            for future in done:
                try:
                    result = future.result()  # 获取任务结果
                except concurrent.futures.TimeoutError:
                    print(f"Task timeout after {timeout} seconds.")
                except Exception as e:
                    print(f"Task failed with error: {e}")
                finally:
                    # 重新提交完成或失败的任务
                    futures[executor.submit(execute_student_task, cookies, url, hook_script)] = futures[future]

            # 处理超时未完成的任务
            for future in not_done:
                if future.running():
                    future.cancel()  # 取消超时任务
                    print(f"Task exceeded {timeout} seconds and was cancelled.")
                    # 重新提交被取消的任务
                    futures[executor.submit(execute_student_task, cookies, url, hook_script)] = futures[future]


def hook_cookie():
    print("通过hook拿cookie和请求url参数方法暂不可用, 请手动填写cookie和url")
    exit(1)


def main():
    # 创建 ArgumentParser 对象并添加参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--hookcookie', action='store_true', help='Run hookcookie method if specified')

    # 解析命令行参数
    args = parser.parse_args()

    # 如果传入了 --hookcookie 参数，执行 hook_cookie 函数
    if args.hookcookie:
        hook_cookie()

    # 传递cookies, url, hook_script参数并开始运行任务
    run_student_tasks(cookies, url, hook_script)


if __name__ == "__main__":
    main()
