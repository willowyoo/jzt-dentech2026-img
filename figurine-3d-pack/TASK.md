# 任务：给照片人物生成写实 3D 模型（3D 打印手办用）

## 背景（一句）
云端服务器的出口 IP 被混元 3D 引擎的区域授权误判（其授权只禁欧盟/英国/韩国），
只有在本机（中国大陆网络）发请求才能直通这台免费引擎，所以这个任务必须在本机跑。

## 你要做的（按顺序）
1. 在本仓库根目录的 `figurine-3d-pack/` 文件夹里运行：
   `python3 run_forge.py`
   - 只用 Python 标准库，macOS 自带 python3 即可，不用装任何东西。
   - 全程约 5–25 分钟（生成+轮询），让它跑完，不要中途杀掉。
2. 结束码为 0 = 成功：模型在 `figurine-3d-pack/output/model-<后端名>.glb`。
3. 把 `figurine-3d-pack/output/` 整个目录和 `figurine-3d-pack/run.log`
   一起 commit 并 push 回本仓库 main 分支，提交信息写：`results: figurine model`。
4. 若结束码非 0（失败）：同样把 `run.log` 推回来（提交信息：`results: failed log`），
   并在回复用户时贴出 run.log 的最后 20 行。

## 红线（别越）
- 不注册任何账号、不登录、不付款、不订阅任何服务。
- 不把参考照片上传到 three.ws 以外的任何网站或服务；照片只从脚本里写死的链接下载。
- 不修改 run_forge.py 里的后端顺序、参数和那几个链接。
- 参考图链接 2026-10-31 到期；若下载返回 404/403，是链接过期，在回复里说明即可，不要自己找别的图源。

## 验收标准
仓库里出现 `figurine-3d-pack/output/model-*.glb`（约数 MB）即算完成。
后续验脸、修网格、加底座、导 STL 由 Muse 那边接手，你不用管。
