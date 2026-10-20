# 私密匿名留言箱

基于 [lin037/qa_box](https://github.com/lin037/qa_box) 的 MIT 许可项目。
上游版权及 LICENSE 保留。本部署只提供文字留言，全部内容仅管理员可读。

- 留言入口：https://message.xjcpp.love/
- 管理入口：https://message.xjcpp.love/admin
- 管理员用户名：`admin`
- 独立项目运行配置：项目根目录 `.env`，权限 `0600`，不提交 Git、不进入镜像。
- 留言保存在 Docker volume `anonymous-message_message-data`，SQLite 每日自动备份，保留最近七份。
- 本机只监听 `127.0.0.1:3002`；API 不映射宿主机端口。
- 阿里云 `127.0.0.1:23002` 经独立 LaunchAgent 转发至本机 3002，Nginx 提供 HTTPS。
- 管理路径是公开信息，访问权限由密码及 JWT 控制。所有详情和批量读取必须登录；公开列表恒为空，回答也不能改为公开。
- 投稿最多 5000 字；From 称呼为选填，最多 40 字，留空显示“匿名朋友”。公网投稿和管理员登录分别限流；不记录发送者 IP 或留言正文。
- 管理页回答仅作为私密备注，不会发送给投稿人。投稿人可以在本次页面停留期间撤回尚未处理的留言。

## 运行与更新

已有 `.env` 时运行（不要用 `docker-compose config` 输出配置，避免泄露凭据）：

```sh
docker-compose up -d --build
docker-compose ps
curl --fail http://127.0.0.1:3002/health
```

首次部署须自行设置至少 16 位的 `ADMIN_PASSWORD`、至少 32 位随机 `SECRET_KEY` 和 `ADMIN_USERNAME=admin`。
修改密码后重新创建 API 容器；如需撤销既有登录，同时轮换 `SECRET_KEY`。

`docker-compose down` 保留数据，**不要使用 `down -v`**，该选项会删除留言卷。
自动备份和主库在同一个卷中，防宿主机或磁盘故障仍需另存卷备份。

公网配置源文件在 `deploy/`。LaunchAgent 安装在当前用户的 `~/Library/LaunchAgents/`。
阿里云配置在 `/www/server/panel/vhost/nginx/message.xjcpp.love.conf`。
HTTPS 由 Certbot 自动续期，`renew-nginx.sh` 安装为 deploy hook 后自动重载宝塔 Nginx。
现有 money/frontend 的配置、3001 端口及 23000/23001 隧道不变。

## 验收

上游未提供单元测试或测试命令。完成修改后运行完整 HTTP 验收：

```sh
python3 scripts/verify-deployment.py http://127.0.0.1:3002
python3 scripts/verify-deployment.py https://message.xjcpp.love
```

脚本只读取本项目已授权的 `.env` 完成管理员登录，不输出密码或 JWT；创建的验收留言在结束时删除。
