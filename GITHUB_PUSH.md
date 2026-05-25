# GitHub 一键上传（杨阳 / 任波）

## 最快方式：双击运行

1. 在 https://github.com/settings/tokens 生成 **classic token**，勾选 **repo**
2. 双击项目根目录下的 **`upload_to_github.bat`**
3. 按提示粘贴 `ghp_...` Token，回车等待完成

脚本会自动：创建仓库（若不存在）→ 提交所有文件 → 推送到 GitHub。

---

## 备用：PowerShell 带环境变量（免交互）

```powershell
$env:GITHUB_TOKEN = "ghp_你的token"
cd "e:\GITHUB\topic analysis with NMF"
.\scripts\upload_to_github.ps1
```

---

# 手动上传指南（备用）

本地 Git 仓库已初始化并完成提交，但因 **GitHub 身份验证** 需由您本人完成推送。

## 第一步：在 GitHub 创建空仓库

1. 登录 https://github.com/meetyangyang  
2. 点击 **New repository**  
3. 仓库名：`OptLitBench`  
4. 保持 **Public**，**不要**勾选 “Add a README”  
5. 创建仓库

## 第二步：配置认证（任选一种）

### 方式 A：GitHub CLI（推荐）

```powershell
winget install GitHub.cli
gh auth login
```

### 方式 B：Personal Access Token (HTTPS)

1. GitHub → Settings → Developer settings → Personal access tokens  
2. 生成 token（勾选 `repo` 权限）  
3. 推送时用 token 代替密码

## 第三步：推送

```powershell
cd "e:\GITHUB\topic analysis with NMF"
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

若远程已有 README，先执行：

```powershell
& "C:\Program Files\Git\bin\git.exe" pull origin main --rebase
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

## 仓库内容说明

| 目录/文件 | 说明 |
|-----------|------|
| `Data_Abstract/` | OptLitBench 原始摘要语料（37,664 篇） |
| `src/` | 分析代码 |
| `config/` | 实验配置 |
| `results/` | 基线与时空分析结果、图表 |
| `paper/icdm2026/` | ICDM 2026 论文 LaTeX 与 Overleaf ZIP |
| `requirements-lock.txt` | 锁定依赖版本 |

## 论文中的开源链接

论文已标注：**https://github.com/meetyangyang/OptLitBench**

推送成功后，请在 `main.tex` 中将通讯作者邮箱 `yangyang@cipuc.edu.cn` 替换为您的真实邮箱。

## Overleaf 导入

直接上传：`paper/icdm2026/OptLitBench_ICDM2026_overleaf.zip`

在 Overleaf：**New Project → Upload Project**，编译器选 pdfLaTeX，然后 Recompile。
