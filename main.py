import requests, json, re, os, sys, traceback

session = requests.session()

# 配置
email = os.environ.get('EMAIL')
passwd = os.environ.get('PASSWD')
SCKEY = os.environ.get('SCKEY')

BASE = 'https://ikuuu.art'
login_url = f'{BASE}/auth/login'
check_url = f'{BASE}/user/checkin'
info_url = f'{BASE}/user/profile'

headers = {
    'origin': BASE,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    if not email or not passwd:
        raise ValueError("EMAIL 或 PASSWD 环境变量未设置")

    print('[1/3] 登录...')
    resp = session.post(url=login_url, headers=headers, data={'email': email, 'passwd': passwd}, timeout=15)
    result = resp.json()
    print(f'   → {result.get("msg", "未知")}')

    if result.get('ret') != 1:
        raise Exception(f'登录失败: {result.get("msg", resp.text[:200])}')

    print('[2/3] 签到...')
    resp = session.post(url=check_url, headers=headers, timeout=15)
    result = resp.json()
    msg = result.get('msg', '未知')
    print(f'   → {msg}')

    print('[3/3] 获取账户信息...')
    info_html = session.get(url=info_url, headers=headers, timeout=15).text
    print(f'   完成')

    # Server酱推送
    if SCKEY:
        push_url = f'https://sctapi.ftqq.com/{SCKEY}.send'
        push_data = {'title': f'ikuuu签到-{msg}', 'desp': f'签到结果: {msg}\n时间: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'}
        push_resp = requests.post(url=push_url, data=push_data, timeout=10)
        push_result = push_resp.json()
        if push_result.get('code') == 0:
            print('   ✓ 推送成功')
        else:
            print(f'   ✗ 推送失败: {push_result.get("message", push_resp.text[:200])}')

except Exception as e:
    error_msg = f'签到失败: {str(e)}'
    print(f'\n✗ {error_msg}')
    traceback.print_exc()

    # 失败也推送
    if SCKEY:
        push_url = f'https://sctapi.ftqq.com/{SCKEY}.send'
        try:
            requests.post(url=push_url, data={'title': f'ikuuu签到-失败', 'desp': f'错误: {error_msg}\n{traceback.format_exc()}'}, timeout=10)
        except:
            pass

    sys.exit(1)
