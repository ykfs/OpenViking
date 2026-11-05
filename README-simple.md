## 背景
本md介绍服务端的各项服务，非管理员用户，请忽略，不需要在个人电脑上部署。

### openviking
- 服务端是非传统RAG管理，可同时云端管理skills、会话、记忆、资产，见https://docs.openviking.ai/zh/getting-started/01-introduction
- 安装 
```bash
# 基于已经编译的包安装
pip install openviking --upgrade
# 基于源码安装
OPENSSL_NO_VENDOR=1 SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENVIKING=0.0.0 pip install . --no-build-isolation
openviking-server init      # 交互式向导：提供商、模型、ov.conf
```
- ~/.openviking/ov.conf 配置
```json
{
  "storage": {
    "workspace": "~/.openviking/data",
    "vectordb": {
      "name": "context",
      "backend": "local"
    },
    "agfs": {
      "backend": "local"
    }
  },
  "embedding": {
    "dense": {
      "api_base" : "https://api.siliconflow.cn/v1",
      "api_key"  : "sk-xxx",
      "provider" : "openai",
      "dimension": 1024,
      "model"    : "BAAI/bge-m3"
    }
  },
  "vlm": {
    "api_base" : "http://<your-vlm-host>:8080/v1",
    "api_key"  : "xxx",
    "provider" : "openai",
    "model"    : "deepseek-flash",
    "temperature": 0.0,
    "max_retries": 2
  },
  "log": {
    "level": "INFO",
    "output": "file"
  },
  "allow_private_networks": true,
  "server": {
    "host": "0.0.0.0",
    "port": 1933,
    "auth_mode": "api_key", # trusted 模式使用root_api_key访问，用请求头上的account做区分；api_key 模式使用api_key访问，通过api_key区分account
    "root_api_key": "xxx"
  }
}

```
- 运行
```bash
openviking-server doctor    # 校验配置
openviking-server           # 启动
```

#### 日常操作

一般来说应该是系统管理员创建好account（产品），将产品级api_key告知产品管理员，产品管理员再上传资源。

- ~/.openviking/ovcli.conf 配置
```json
{
  "account": "default",
  "user": "default",
  "url": "http://127.0.0.1:1933",
  "root_api_key": "xxx"
}
```

- 新增account，一个account对应一个产品
```bash
ov --sudo -o admin create-account 产品名称 --admin 管理员名称
```

- 重置account的api_key
```bash
curl -X POST http://127.0.0.1:1933/api/v1/admin/accounts/产品名称/users/管理员名称/key \
  -H "X-API-Key: root_api_key"
```


- 在account下上传资产，目录结构可以和本地资产目录一致，
  
  -p 是没有目录时自动创建\
  --args parse_mode:no_split 是不切分资产，直接上传,但是大文件向量化会报错，需要切分\
  把下面这个命令放到一个shell脚本中，
  ```bash
  #!/bin/bash

  # 1. 强制指定 NVM 的安装目录（通常是在家目录下的 .nvm）
  export NVM_DIR="$HOME/.nvm"

  # 2. 加载 nvm 的初始化脚本
  # 注意：如果你的 Mac 上是用 brew 安装的 nvm，路径可能是 /usr/local/opt/nvm/nvm.sh 或 /opt/homebrew/opt/nvm/nvm.sh
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 

  # 3. 切换到你需要的 Node 版本
  nvm use 24

  # 先删除再上传，否则会新生成一份新的资产
  ov --account 产品名称 rm -r viking://resources/xxx
  ov --account 产品名称 add-resource xxx/knowledge/example --to viking://resources/knowledge/example
  ```
  然后给脚本执行权限：chmod +x xxx.sh，\
  最后`crontab -e`，添加一行：`0 10 * * * xxx.sh >> xxx.log 2>&1`\
  mac上sh和log要放到有权限的目录，不能是Documents目录

- 查看任务列表
```bash
ov --account 产品名称 task list
```

- 停止任务
```bash
ov --account 产品名称 task cancel 任务id
```
