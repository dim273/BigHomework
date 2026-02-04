# 1. 项目概述
本项目旨在实现基于 ConvNeXt 模型的 Animal-10 数据集图像分类任务。

# 2. 项目结构

main.py                 # 主训练脚本（ConvNeXt模型）

ablation.py             # 消融实验脚本

compare.py             # 模型对比实验脚本

data_init.py           # 数据初始化脚本

utils.py               # 工具函数


# 3. 核心功能模块
## 3.1 模型架构
ConvNeXt：基于现代Transformer设计理念的纯卷积网络

SimpleCNN：传统卷积神经网络（用于对比）

MiniResNet：轻量级ResNet变体（用于对比）

## 3.2 数据管理
自动数据集划分（训练集/验证集/测试集 = 8:1:1）

数据增强策略（随机裁剪、翻转、颜色抖动）


## 3.3 训练框架
模块化训练器（Trainer类）

可配置的训练参数

自动保存最佳模型

学习率调度

# 4. 使用指南
## 4.1 环境准备

安装依赖

`pip install torch torchvision numpy pandas matplotlib seaborn scikit-learn tqdm`
## 4.2 数据初始化

`python data_init.py`

这将检查数据集结构，创建CSV划分文件，可视化样本图像

## 4.3 主训练流程
快速测试

`python main.py --subset_ratio 0.2 --epochs 5 --batch_size 16`

完整训练

`python main.py --epochs 20 --batch_size 32`

由于这个模型不是主要的，就没测试消融和对比这两个代码文件了

# 5. 实验结果
见results