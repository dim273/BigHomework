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
    Animal10Dataset, Trainer, create_data_loaders, 
    set_seed, plot_class_accuracy
)

class SimpleCNN(nn.Module):
    """简单的CNN模型作为对比"""
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            # 第一层
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # 第二层
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # 第三层
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # 第四层
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512 * 14 * 14, 1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, num_classes)
        )
        
        self._init_weights()
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

class ResNetBlock(nn.Module):
    """ResNet基础块"""
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                              stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                              padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1,
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
        
        out += identity
        out = self.relu(out)
        
        return out

class MiniResNet(nn.Module):
    """迷你ResNet作为对比"""
    def __init__(self, num_classes=10):
        super().__init__()
        self.in_channels = 64
        
        self.stem = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        
        self.layer1 = self._make_layer(64, 64, 2, stride=1)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)
        self.layer4 = self._make_layer(256, 512, 2, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
        
        self._init_weights()
    
    def _make_layer(self, in_channels, out_channels, blocks, stride):
        layers = []
        layers.append(ResNetBlock(in_channels, out_channels, stride))
        
        for _ in range(1, blocks):
            layers.append(ResNetBlock(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        x = self.stem(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x

def run_comparison_experiment(model_class, model_name, data_config, train_config):
    """运行对比实验"""
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
    model = model_class(num_classes=len(class_names))
    print(f"{model_name} parameters: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")
    
    # 创建训练器
    results_dir = f"../results/comparison/{model_name}"
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
        'model_name': model_name,
        'best_val_acc': best_val_acc,
        'test_acc': test_acc,
        'parameters': sum(p.numel() for p in model.parameters())/1e6,
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

def comparison_study():
    """对比研究主函数"""
    parser = argparse.ArgumentParser(description='Model Comparison Study for Animal-10')
    parser.add_argument('--data_dir', type=str, default='../data/Animals-10')
    parser.add_argument('--csv_dir', type=str, default='../data')
    parser.add_argument('--subset_ratio', type=float, default=0.2)
    
    args = parser.parse_args()
    
    # 基础配置
    data_config = {
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
    
    # 定义要对比的模型
    models_to_compare = [
        ('SimpleCNN', SimpleCNN),
        ('MiniResNet', MiniResNet),
        ('ConvNeXt', lambda num_classes: __import__('main').ConvNeXt(num_classes=num_classes))
    ]
    
    # 运行所有对比实验
    all_results = {}
    for model_name, model_class in models_to_compare:
        print(f"\nRunning comparison for: {model_name}")
        result = run_comparison_experiment(
            model_class, model_name, data_config, train_config
        )
        all_results[model_name] = result
    
    # 绘制对比实验比较图
    plot_comparison_results(all_results)

def plot_comparison_results(results):
    """绘制对比实验结果"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 准备数据
    model_names = list(results.keys())
    val_accs = [results[name]['best_val_acc'] for name in model_names]
    test_accs = [results[name]['test_acc'] for name in model_names]
    params = [results[name]['parameters'] for name in model_names]
    
    x = np.arange(len(model_names))
    
    # 1. 准确率比较
    width = 0.35
    bars1 = ax1.bar(x - width/2, val_accs, width, label='Validation', alpha=0.8, color='skyblue')
    bars2 = ax1.bar(x + width/2, test_accs, width, label='Test', alpha=0.8, color='lightcoral')
    
    ax1.set_xlabel('Model')
    ax1.set_ylabel('Accuracy (%)')
    ax1.set_title('Model Comparison: Accuracy')
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, (val, test) in enumerate(zip(val_accs, test_accs)):
        ax1.text(i - width/2, val + 0.5, f'{val:.1f}%', ha='center', va='bottom')
        ax1.text(i + width/2, test + 0.5, f'{test:.1f}%', ha='center', va='bottom')
    
    # 2. 参数量比较
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    bars3 = ax2.bar(x, params, color=colors[:len(model_names)])
    ax2.set_xlabel('Model')
    ax2.set_ylabel('Parameters (M)')
    ax2.set_title('Model Comparison: Parameters')
    ax2.set_xticks(x)
    ax2.set_xticklabels(model_names, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, param in enumerate(params):
        ax2.text(i, param + 0.1, f'{param:.2f}M', ha='center', va='bottom')
    
    # 3. 训练损失曲线比较
    ax3.set_title('Training Loss Comparison')
    for model_name, result in results.items():
        epochs = range(1, len(result['train_losses']) + 1)
        ax3.plot(epochs, result['train_losses'], label=model_name, linewidth=2)
    
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('Loss')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 验证准确率曲线比较
    ax4.set_title('Validation Accuracy Comparison')
    for model_name, result in results.items():
        epochs = range(1, len(result['val_accs']) + 1)
        ax4.plot(epochs, result['val_accs'], label=model_name, linewidth=2)
    
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Accuracy (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/comparison/model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存汇总结果
    summary = {
        'models': model_names,
        'validation_accuracies': val_accs,
        'test_accuracies': test_accs,
        'parameters_millions': params,
        'parameter_efficiency': [test_accs[i]/params[i] for i in range(len(model_names))]
    }
    
    with open('../results/comparison/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nModel Comparison Summary:")
    print("=" * 80)
    print(f"{'Model':15s} | {'Val Acc':>10s} | {'Test Acc':>10s} | {'Params (M)':>12s} | {'Eff.':>8s}")
    print("-" * 80)
    for i, name in enumerate(model_names):
        efficiency = summary['parameter_efficiency'][i]
        print(f"{name:15s} | {val_accs[i]:9.2f}% | {test_accs[i]:9.2f}% | {params[i]:11.2f} | {efficiency:7.2f}")
    print("=" * 80)

if __name__ == '__main__':
    comparison_study()