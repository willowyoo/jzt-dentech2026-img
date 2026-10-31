#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键包：照片 -> 写实 3D 模型（GLB），供 3D 打印手办使用。
在本机（中国大陆网络）直接运行：python3 run_forge.py
原理：three.ws 免费通道里混元系引擎按请求 IP 判区域授权——只禁欧盟/英国/韩国，
中国 IP 可直通；云端 IP 被误判禁区，所以必须在本机跑。
只用 Python 标准库，无第三方依赖。强制直连（忽略系统代理）。
"""
import json, os, sys, time, urllib.request, urllib.error

BASE = "https://three.ws"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "run.log")

# 参考图（临时直链，2026-10-31 到期；主图为 02 全身正面）
REFS = {
    "01-face.jpg":       "https://muse.ai/files/1330517020147523/1670919884397555/449qt0cb20d9cuqdmbha8xsh/01-__.jpg",
    "02-fullbody.jpg":   "https://muse.ai/files/1330517020147523/2035816710469557/rogn3g4szqvry13kcuzbw4td/02-____.jpg",
    "03-fullbody2.jpg":  "https://muse.ai/files/1330517020147523/2601348070372739/yy6otm60feyld2nftpbcy4gq/03-_____.jpg",
    "04-phone.jpg":      "https://muse.ai/files/1330517020147523/2593996001042575/44vuz9idrxama4j290961mc5/04-_____.jpg",
    "05-far.jpg":        "https://muse.ai/files/1330517020147523/2144989976105241/kprqtrh55d7rti81hijytcl7/05-____.jpg",
}
MAIN_REF = "02-fullbody.jpg"
PROMPT = "woman in black blazer and skirt, standing full body, studio lighting"
BACKENDS = ["hunyuan3d", "huggingface", "trellis_selfhost"]  # 顺序不要改

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def http(method, url, body=None, timeout=120):
    data = None
    headers = {"User-Agent": "figurine-pack/1.0"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _opener.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "figurine-pack/1.0"})
    with _opener.open(req, timeout=300) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    return os.path.getsize(dest)

def run_backend(backend, image_url):
    log("提交任务 backend=%s" % backend)
    status, raw = http("POST", BASE + "/api/forge", {
        "image_urls": [image_url],
        "prompt": PROMPT,
        "path": "image",
        "tier": "standard",
        "backend": backend,
    })
    try:
        d = json.loads(raw.decode("utf-8"))
    except Exception:
        log("  创建任务返回不可解析 (HTTP %s): %s" % (status, raw[:200]))
        return None
    if status != 200 or not (d.get("job_id") or d.get("id")):
        log("  创建任务失败 HTTP %s: %s" % (status, json.dumps(d, ensure_ascii=False)[:300]))
        return None
    job = d.get("job_id") or d.get("id")
    log("  job=%s 已建，开始轮询" % job[:24])
    for i in range(120):  # 最长约 20 分钟
        time.sleep(10)
        s2, raw2 = http("GET", BASE + "/api/forge?job=" + urllib.parse.quote(job, safe=""))
        try:
            d2 = json.loads(raw2.decode("utf-8"))
        except Exception:
            log("  轮询 %d 返回异常，重试" % i)
            continue
        st = d2.get("status") or d2.get("state")
        if i % 6 == 0 or st in ("done", "failed", "error"):
            log("  轮询 %d status=%s elapsed=%ss" % (i, st, d2.get("elapsed_seconds")))
        if st == "done":
            url = d2.get("glb_url")
            if not url:
                log("  done 但没有 glb_url: %s" % json.dumps(d2)[:300])
                return None
            outdir = os.path.join(HERE, "output")
            os.makedirs(outdir, exist_ok=True)
            dest = os.path.join(outdir, "model-%s.glb" % backend)
            size = download(url, dest)
            log("  成功！模型已下载: %s (%d bytes)" % (dest, size))
            return dest
        if st in ("failed", "error"):
            log("  任务失败: %s" % json.dumps(d2, ensure_ascii=False)[:300])
            return None
    log("  轮询超时（20 分钟）")
    return None

def main():
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    log("=== run_forge 开始 ===")
    refs_dir = os.path.join(HERE, "refs")
    os.makedirs(refs_dir, exist_ok=True)
    for name, url in REFS.items():
        dest = os.path.join(refs_dir, name)
        if not os.path.exists(dest):
            try:
                sz = download(url, dest)
                log("参考图已存 %s (%d bytes)" % (name, sz))
            except Exception as e:
                log("参考图下载失败 %s: %s" % (name, e))
    main_url = REFS[MAIN_REF]
    for backend in BACKENDS:
        try:
            got = run_backend(backend, main_url)
        except Exception as e:
            log("backend=%s 异常: %s" % (backend, e))
            got = None
        if got:
            log("=== 完成：%s ===" % got)
            return 0
        log("backend=%s 未出模型，尝试下一个" % backend)
    log("=== 全部后端失败 ===")
    return 1

if __name__ == "__main__":
    sys.exit(main())
