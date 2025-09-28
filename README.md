# 项目介绍
这是一个基于**Django**后端和**Vue.js**前端的 AI 角色扮演网站。用户可以自定义角色、多轮对话、语音聊天，并支持角色导入导出。
# 技术选型
```
前端：Vue 3 + Pinia + Axios
后端：Django + Django Channels + REST framework
语音聊天：七牛云TTS & 浏览器自带语音输入
LLM 模型：Grok Fast 4
```
# 使用教程
```
1.安装后端依赖文件：
在crane_bar目录下执行 pip install -r requirements.txt 命令
2.进行后端数据库迁移：
在crane_bar_django目录下执行 python manage.py migrate
3.安装前端依赖：
在crane_bar_vue目录下执行 npm install 命令
4.启动项目
分别打开startDjango.bat和startVue.bat，然后通过浏览器访问：http://localhost:5173/ 即可使用
```
# 测试环境
```
Python:3.13.7
npm:10.9.3
node:v22.20.0
浏览器:Edge/Chrome
```
# License
本项目仅用于七牛云校招展示，禁止商业用途，如需代码请注明。
