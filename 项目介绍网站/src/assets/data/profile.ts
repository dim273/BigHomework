export interface EducationItem {
  period: string
  degree: string
  school: string
}

export interface TimelineItem {
  period: string
  title: string
  org: string
  description: string
}

export interface SocialLink {
  platform: string
  url: string
  icon: string
  desc: string
}

export interface Profile {
  name: string
  title: string
  affiliation: string
  bio: string
  email: string
  github: string
  location: string
  skills: string[]
  education: EducationItem[]
  experiences: TimelineItem[]
  socials: SocialLink[]
}

export const profile: Profile = {
  name: 'code-assistant-live2d',
  title: '基于心流理论的编程学习支持系统',
  affiliation: '本科生科研训练与创新创业项目',
  bio: 'code-assistant-live2d 是一款基于心流理论的编程学习支持系统，以心流理论为核心指导，通过动态难度调节子系统维持挑战难度与能力水平的平衡（提高心流触发概率），依托沉浸感优化子系统营造无干扰的专注环境（延长心流停留时间）。两大子系统相辅相成，共同致力于将高认知负荷的编程学习，转换为目标清晰、反馈及时的「心流旅程」。',
  email: 'tpet@example.com',
  github: 'https://github.com/dim273/t-pet',
  location: '中国',
  skills: [
    '心流理论',
    '最近发展区理论（ZPD）',
    'VS Code Extension API',
    '知识图谱',
    'DeepSeek API',
    'Live2D Cubism SDK',
    'Pixi.js',
    'Electron',
  ],
  education: [],
  experiences: [
    {
      period: '2024 · 项目立项',
      title: '心流理论框架与架构设计',
      org: 't-pet 项目',
      description: '确立以心流理论为核心的系统设计框架，设计单 Webview 多页面 SPA 架构，规划动态难度调节与沉浸感优化两大子系统共 8 个模块。',
    },
    {
      period: '2024 · 动态难度调节子系统',
      title: '能力评估 · 挑战评估 · 动态匹配 · 问题分解',
      org: 't-pet 项目',
      description: '完成动态难度调节子系统四大模块：基于知识图谱的能力评估模型、四维适配性量化的挑战评估模型、Top-5 动态匹配算法，以及将大模型从「答案提供者」转为「学习辅助者」的问题分解算法。',
    },
    {
      period: '2024 · 沉浸感优化子系统',
      title: '目标可视化 · 多模态交互 · 聚焦模式 · 情感萌伴',
      org: 't-pet 项目',
      description: '完成沉浸感优化子系统四大模块：基于 NOI 大纲的知识图谱闯关设计、里程碑反馈的多模态交互系统、单 Webview 聚焦模式，以及通过 Hack workbench.js 注入的 Live2D 认知-情感协同萌伴。',
    },
    {
      period: '2024 · 系统集成',
      title: '两大子系统协同与心流闭环',
      org: 't-pet 项目',
      description: '完成两大子系统集成，动态难度调节子系统主动塑造心流触发条件，沉浸感优化子系统延长心流停留时间，形成完整的「学—练—评—反馈」心流闭环。',
    },
  ],
  socials: [
    {
      platform: 'GitHub',
      url: 'https://github.com/dim273/t-pet',
      icon: 'GH',
      desc: 't-pet 源码仓库',
    },
    {
      platform: 'VS Code Marketplace',
      url: 'https://marketplace.visualstudio.com/search?term=Code%20Assistant%20Live2d',
      icon: 'VS',
      desc: '搜索安装插件 Code Assistant Live2d',
    },
    {
      platform: '项目文档',
      url: 'https://github.com/dim273/t-pet/blob/master/README.md',
      icon: 'DOC',
      desc: 'README 技术文档与使用指南',
    },
    {
      platform: 'Issue 反馈',
      url: 'https://github.com/dim273/t-pet/issues',
      icon: 'IS',
      desc: '问题反馈与功能建议',
    },
  ],
}
