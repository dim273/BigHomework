import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import json

# 添加父目录到路径
sys.path.append('.')

from main import (
    ConvNeXt, Animal10Dataset, Trainer, 
    create_data_loaders, set_seed, plot_class_accuracy
)

def run_ablation_experiment(experiment_name, model_config, data_config, train_config):
    """运行消融实验"""
    set_seed(42)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 创建数据加载器
    train_loader, val_loader, test_loader, class_names = create_data_loaders(
        data_config['data_dir'], 
        data_config['csv_dir'], 
        train_config['batch_size'],
        data_config.get('subset_ratio', 1.0)
    )
    
    # 创建模型
    model = ConvNeXt(
        num_classes=len(class_names),
        depths=model_config.get('depths', [3, 3, 9, 3]),
        dims=model_config.get('dims', [96, 192, 384, 768])
    )
    
    # 创建训练器
    results_dir = f"../results/ablation/{experiment_name}"
    os.makedirs(results_dir, exist_ok=True)
    trainer = Trainer(model, device, results_dir=results_dir)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(), 
        lr=train_config['lr'],
        weight_decay=train_config.get('weight_decay', 0.05)
    )
    
    # 训练
    best_val_acc = 0.0
    for epoch in range(train_config['epochs']):
        train_loss, train_acc = trainer.train_epoch(
            train_loader, criterion, optimizer, epoch
        )
        val_loss, val_acc = trainer.validate(val_loader, criterion)
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), f'{results_dir}/best_model.pth')
    
    # 测试
    model.load_state_dict(torch.load(f'{results_dir}/best_model.pth'))
    test_acc, preds, labels = trainer.test(test_loader)
    
    # 保存结果
    results = {
        'experiment_name': experiment_name,
        'model_config': model_config,
        'train_config': train_config,
        'best_val_acc': best_val_acc,
        'test_acc': test_acc,
        'train_losses': trainer.train_losses,
        'val_losses': trainer.val_losses,
        'train_accs': trainer.train_accs,
        'val_accs': trainer.val_accs
    }
    
    with open(f'{results_dir}/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # 绘制训练曲线
    trainer.plot_training_curves()
    
    # 绘制混淆矩阵
    trainer.plot_confusion_matrix(preds, labels, class_names)
    
    # 绘制类别准确率
    plot_class_accuracy(preds, labels, class_names, results_dir)
    
    return results

def ablation_study():
    """消融研究主函数"""
    parser = argparse.ArgumentParser(description='Ablation Study for Animal-10')
    parser.add_argument('--data_dir', type=str, default='../data/Animals-10')
    parser.add_argument('--csv_dir', type=str, default='../data')
    parser.add_argument('--subset_ratio', type=float, default=0.2)
    
    args = parser.parse_args()
    
    # 基础配置
    base_config = {
        'data_dir': args.data_dir,
        'csv_dir': args.csv_dir,
        'subset_ratio': args.subset_ratio
    }
    
    train_config = {
        'epochs': 15,
        'batch_size': 32,
        'lr': 1e-3,
        'weight_decay': 0.05
    }
    
    # 定义消融实验
    experiments = [
        {
            'name': 'baseline',
            'model_config': {
                'depths': [3, 3, 9, 3],
                'dims': [96, 192, 384, 768]
            }
        },
        {
            'name': 'shallow',
            'model_config': {
                'depths': [2, 2, 4, 2],  # 更浅的网络
                'dims': [96, 192, 384, 768]
            }
        },
        {
            'name': 'narrow',
            'model_config': {
                'depths': [3, 3, 9, 3],
                'dims': [64, 128, 256, 512]  # 更窄的网络
            }
        },
        {
            'name': 'no_stem_norm',
            'model_config': {
                'depths': [3, 3, 9, 3],
                'dims': [96, 192, 384, 768],
                'no_stem_norm': True  # 需要在ConvNeXt类中实现这个选项
            }
        }
    ]
    
    # 运行所有实验
    all_results = {}
    for exp in experiments:
        print(f"\nRunning experiment: {exp['name']}")
        result = run_ablation_experiment(
            exp['name'],
            exp['model_config'],
            base_config,
            train_config
        )
        all_results[exp['name']] = result
    
    # 绘制消融实验比较图
    plot_ablation_comparison(all_results)

def plot_ablation_comparison(results):
    """绘制消融实验比较图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 准备数据
    experiment_names = list(results.keys())
    val_accs = [results[name]['best_val_acc'] for name in experiment_names]
    test_accs = [results[name]['test_acc'] for name in experiment_names]
    
    x = np.arange(len(experiment_names))
    
    # 绘制准确率比较
    width = 0.35
    ax1.bar(x - width/2, val_accs, width, label='Validation Accuracy', alpha=0.8)
    ax1.bar(x + width/2, test_accs, width, label='Test Accuracy', alpha=0.8)
    
    ax1.set_xlabel('Experiment')
    ax1.set_ylabel('Accuracy (%)')
    ax1.set_title('Ablation Study: Accuracy Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(experiment_names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, (val, test) in enumerate(zip(val_accs, test_accs)):
        ax1.text(i - width/2, val + 0.5, f'{val:.1f}%', ha='center')
        ax1.text(i + width/2, test + 0.5, f'{test:.1f}%', ha='center')
    
    # 绘制训练损失曲线比较
    ax2.set_title('Ablation Study: Training Loss Comparison')
    for exp_name, result in results.items():
        epochs = range(1, len(result['train_losses']) + 1)
        ax2.plot(epochs, result['train_losses'], label=exp_name, linewidth=2)
    
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Training Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/ablation/comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存汇总结果
    summary = {
        'experiments': experiment_names,
        'validation_accuracies': val_accs,
        'test_accuracies': test_accs,
        'parameters': [sum(p.numel() for p in torch.load(f'../results/ablation/{name}/best_model.pth').values())/1e6 
                      for name in experiment_names]
    }
    
    with open('../results/ablation/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nAblation Study Summary:")
    print("=" * 60)
    for name, val_acc, test_acc in zip(experiment_names, val_accs, test_accs):
        print(f"{name:15s} | Val Acc: {val_acc:6.2f}% | Test Acc: {test_acc:6.2f}%")
    print("=" * 60)

if __name__ == '__main__':
    ablation_study()