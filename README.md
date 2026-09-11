[![VibeShotClub](./assets/brand/vibeshotclub-banner.svg)](https://vibeshot.club)

# VSC Skills

由 [VibeShotClub](https://vibeshot.club) 出品的开源的图像/视频创作Skills 集合，面向 AIGC 创作、提示词设计、视觉风格探索、视频工作流和生成资产管理。

这个仓库将可重复使用的创作方法封装成独立 Skill。安装后，可以在 Codex 中通过 `$vsc` 描述需求，由统一入口选择合适的技能并直接执行；也可以通过 `$skill-name` 直接调用具体技能。

[探索 VibeShotClub](https://vibeshot.club) · [交流创作](https://vibeshot.club/forum) · [商务合作](mailto:support@vescend.com)

## Skill 导航

| Skill | 作者（X） | 用途 | 适合场景 |
| --- | --- | --- | --- |
| [`vsc`](./vsc/) | VibeShotClub | 根据当前对话选择可用的 VSC 技能并直接执行 | 不知道该选哪个技能、查看能力、统一创作入口 |
| [`character-candid-photography`](./character-candid-photography/) | [Voxcat](https://x.com/VoxcatAI) | 将成年角色转译为虚构摆拍的遮挡观察与抓拍摄影提示词 | 真人 COS、角色转译、手机快拍、十组差异化构图 |
| [`codex-image-to-eagle`](./codex-image-to-eagle/) | [古一](https://x.com/MANISH1027512) | 将 Codex 生成图片归档到 Eagle，并保存提示词、标签和文件夹信息 | 图片归档、素材管理、提示词复盘 |
| [`rare-style-explorer`](./rare-style-explorer/) | [古一](https://x.com/MANISH1027512) | 从 620 条稀有视觉亚风格中组合中文生图提示词 | 风格探索、产品图、人物、海报、场景创意 |
| [`shan-ze-school`](./shan-ze-school/) | [Richmond](https://x.com/zhurichmond) | 生成新东方神话、山海经异兽、工笔水墨奇幻方向的提示词 | 东方神怪、异兽、国风神话插画 |
| [`summer-boyfriend-pov`](./summer-boyfriend-pov/) | [𝟡𝟜 ᴾᴸᴬʸᶠᴼᴿᴳᴱ](https://x.com/94vanAI) | 生成一张成年人物夏季泳装自然抓拍照片，支持多人同框、分职责垫图和任意媒介角色 COS | 伴侣 / 朋友视角、夏季旅行、真人 COS、角色泳装转译 |
| [`vibeshot-candid-photography`](./vibeshot-candid-photography/) | [古一](https://x.com/MANISH1027512) | 生成真实生活感、偶然抓拍感、非常规机位的人像摄影提示词 | 韩系人像、生活写真、自然遮挡、批量摄影提示词 |
| [`virtual-couple-travel-vlog`](./virtual-couple-travel-vlog/) | [Valentin LOU](https://x.com/valentinlulu) | 从旅行主题生成虚拟情侣照片墙、角色卡、视频提示词和成片工作流 | 虚拟情侣、旅行 Vlog、连续人物资产、视频制作 |

每个 Skill 的详细能力、依赖和示例，请进入对应目录查看 `README.md`。

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/vibeshotclub/vsc-skills.git
cd vsc-skills
```

### 2. 安装单个 Skill

以 `vibeshot-candid-photography` 为例：

```bash
mkdir -p ~/.codex/skills
cp -R vibeshot-candid-photography ~/.codex/skills/
```

安装其他 Skill 时，将目录名替换成对应的 Skill 名称即可。

### 3. 安装仓库中的全部 Skill

在仓库根目录执行：

```bash
mkdir -p ~/.codex/skills
for skill_dir in */; do
  if [ -f "${skill_dir}SKILL.md" ]; then
    cp -R "${skill_dir%/}" ~/.codex/skills/
  fi
done
```

如果使用了自定义 `CODEX_HOME`，请将 `~/.codex/skills` 替换为对应的 Skills 目录。安装后新开一个 Codex 对话；如果 Skill 没有立即出现，请重启 Codex。

推荐安装全部技能后使用 `$vsc`。也可以只安装 `vsc` 与需要的创作技能；入口不会自动安装缺少的技能。运行技能发现脚本需要 Python 3.10+，无需额外 Python 包。

## 如何使用

### 统一入口

在 Codex 中写出 `$vsc`，再描述想做的作品，无需先记住具体技能名称：

```text
$vsc 给「陶瓷猫香水瓶」探索 8 种稀有视觉风格，只要提示词。
$vsc 两位成年朋友在泳池泼水，泳装、朋友视角，生成一张照片。
$vsc 把刚刚由 Codex 生成的图片和原始提示词归档到 Eagle。
```

已有需求时，单独输入 `$vsc` 可以接着处理；没有上下文时，会简短引导你描述创作目标。默认选择一个技能并直接执行，涉及图片、视频或 Eagle 时仍需相应工具可用。

`/vsc` 也写入了技能的文本触发说明；能否作为客户端原生斜杠命令取决于宿主和安装方式。当前文档以 Codex 的 `$vsc` 为准。详见 [VSC 入口说明](./vsc/README.md)。

已经知道需要哪个技能时，仍可直接写出 `$skill-name`，再描述具体任务。

### 生成真实抓拍人像提示词

```text
使用 $vibeshot-candid-photography，生成 5 组，全部使用荷塘场景，BM 风，低机位为主。
```

### 探索稀有视觉风格

```text
使用 $rare-style-explorer，给「陶瓷猫香水瓶」生成 8 个稀有风格生图提示词，偏产品图方向。
```

### 生成东方神话异兽提示词

```text
使用 $shan-ze-school，为「九尾狐衔灯走过雪夜竹林」生成一组东方神怪工笔水墨提示词。
```

### 创建虚拟情侣旅行 Vlog

```text
使用 $virtual-couple-travel-vlog，制作一对中国情侣在巴塞罗那旅行的虚拟 Vlog。
```

### 生成夏季泳装自然抓拍单图

```text
使用 $summer-boyfriend-pov，两位成年朋友 COS 蒂法与爱丽丝，在泳池泼水，Friend POV，一张独立照片。
```

支持人物、姿势、构图与摄影风格参考。一次只生成一张独立照片，单图可以多人同框。

### 归档 Codex 生成图片

```text
使用 $codex-image-to-eagle，把刚刚生成的图片和提示词归档到 Eagle。
```

## 仓库结构

```text
vsc-skills/
├── README.md
├── assets/brand/          # VibeShotClub 品牌横图
├── vsc/                   # 统一入口与随包技能目录
├── tools/                 # 目录构建与维护依赖
├── tests/                 # 发现脚本检查与路由行为验收用例
├── character-candid-photography/
├── codex-image-to-eagle/
├── rare-style-explorer/
├── shan-ze-school/
├── summer-boyfriend-pov/
├── vibeshot-candid-photography/
└── virtual-couple-travel-vlog/
```

一个 Skill 通常包含：

```text
skill-name/
├── SKILL.md              # Codex 读取的核心指令
├── README.md             # 面向使用者的说明和示例
├── agents/openai.yaml    # 可选的界面与调用元数据
├── references/           # 可选的参考资料
├── scripts/              # 可选的自动化脚本
└── assets/               # 可选的模板或素材
```

其中 `SKILL.md` 是必需文件，其余内容根据工作流需要添加。

## 创建或贡献 Skill

提交新 Skill 前，请确认：

- Skill 使用小写字母、数字和连字符命名
- `SKILL.md` 包含有效的 `name` 与 `description` YAML 元数据
- 触发条件明确，不会误匹配大量无关任务
- 创作技能的 metadata 包含 `vsc-category`、`vsc-deliverables`、`vsc-distinction`，明确分类、实际交付类型和相邻能力边界
- 用户指定的条件优先于默认规则
- README 至少说明用途、安装方式和一组输入输出示例
- 脚本、引用文件和资源都能从 `SKILL.md` 中找到明确入口
- 没有提交密钥、账号、私人路径或生成缓存

可以使用 Codex 自带的校验脚本检查 Skill：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ./skill-name
```

新增或修改技能后，重新生成并校验统一入口目录（维护环境需要 `tools/requirements.txt` 中的 PyYAML）：

```bash
python3 tools/build_vsc_catalog.py
python3 tools/build_vsc_catalog.py --check
python3 -m unittest discover -s tests -v
```

同时提交生成的目录，避免技能更新后入口仍使用旧的能力信息。元数据示例见 [VSC 维护说明](./vsc/README.md#新增或更新技能)，模型选择和交付范围见 [路由行为验收用例](./tests/vsc-routing-cases.md)。

建议每次提交只解决一个清晰问题，并在 Pull Request 中说明：

1. Skill 解决什么任务
2. 什么情况下应该触发
3. 用户输入与预期输出
4. 是否需要额外工具、服务或本地依赖

## 使用说明

- 不同 Skill 的外部依赖不同，请以各目录 README 为准。
- 涉及第三方平台、API、付费生成或本地软件时，请先确认权限、费用和运行环境。
- 生成内容仍需使用者根据实际模型、平台规则和发布场景进行审核。

## 关于 VibeShotClub

**让灵感成为作品，让创作经验被更多人复用。**

[VibeShotClub](https://vibeshot.club)（VSC）是目前 X 上最大的 AIGC 视觉创作社区，专注 **AI 生图与 AI 视频创作**，连接热爱视觉表达的创作者、设计师与影像探索者。

我们关注工具与模型的进步，也关注画面背后的审美、情绪与叙事。从一张图的光影、构图和风格，到一段视频的角色一致性、镜头语言与节奏，社区围绕真实作品展开交流，让创作方法可以被理解、复现和继续改进。

- **AI 生图**：探索人像写真、商业视觉、艺术风格与创意表达，分享提示词、参数和创作过程。
- **AI 视频**：交流图生视频、角色塑造、分镜设计与短片制作，把单张画面的灵感延伸为动态叙事。
- **创作工作流**：拆解从灵感、生成到后期与交付的完整流程，将有效方法整理为可复用的工具与 Skills。
- **交流与共创**：发布作品、获得反馈、分享教程与实验，找到审美相近、愿意一起探索的创作伙伴。

**VSC Skills 是社区创作经验的开源延伸。** 我们把提示词设计、视觉探索和资产管理中的实用方法封装成可直接调用的 Skill，让经验走出讨论，进入每个人的创作流程。

[探索社区](https://vibeshot.club) · [看作品与交流方法](https://vibeshot.club/forum) · [加入 VSC](https://vibeshot.club/join)

### 商务合作

欢迎围绕 AIGC 内容创作、品牌共创、工具与工作流展开合作。

联系：[support@vescend.com](mailto:support@vescend.com) · [官网联系页面](https://vibeshot.club/support)
