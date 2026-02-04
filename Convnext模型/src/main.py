import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import pandas as pd

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from PIL import Image
import torch.nn.functional as F

# 设置随机种子
def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True

set_seed(42)

class LayerNorm2d(nn.Module):
    """2D Layer Normalization，用于处理4D张量 [N, C, H, W]"""
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.bias = nn.Parameter(torch.zeros(dim))
        self.eps = eps
        self.dim = dim
    
    def forward(self, x):
        # x: [N, C, H, W]
        # 在通道维度上计算均值和方差
        u = x.mean(1, keepdim=True)  # [N, 1, H, W]
        s = (x - u).pow(2).mean(1, keepdim=True)  # [N, 1, H, W]
        x = (x - u) / torch.sqrt(s + self.eps)  # [N, C, H, W]
        
        # 应用可学习的缩放和偏移
        x = self.weight[None, :, None, None] * x + self.bias[None, :, None, None]
        return x

class ConvNeXtBlock(nn.Module):
    """ConvNeXt 基础块"""
    def __init__(self, dim, layer_scale=1e-6):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.norm = LayerNorm2d(dim)
        self.pwconv1 = nn.Conv2d(dim, 4 * dim, kernel_size=1)
        self.act = nn.GELU()
        self.pwconv2 = nn.Conv2d(4 * dim, dim, kernel_size=1)
        self.gamma = nn.Parameter(layer_scale * torch.ones((dim)), requires_grad=True) if layer_scale > 0 else None
        
    def forward(self, x):
        shortcut = x
        x = self.dwconv(x)
        # LayerNorm
        x = self.norm(x)
        
        # 点卷积
        x = self.pwconv1(x)
        x = self.act(x)
        x = self.pwconv2(x)
        
        # 缩放和残差连接
        if self.gamma is not None:
            x = self.gamma[None, :, None, None] * x
        
        return shortcut + x

class DownsampleLayer(nn.Module):
    """下采样层"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.norm = LayerNorm2d(in_channels)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=2, stride=2)
    
    def forward(self, x):
        x = self.norm(x)
        x = self.conv(x)
        return x

class ConvNeXt(nn.Module):
    """自定义ConvNeXt模型"""
    def __init__(self, num_classes=10, depths=[3, 3, 9, 3], dims=[96, 192, 384, 768]):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(3, dims[0], kernel_size=4, stride=4),
            LayerNorm2d(dims[0])
        )
        
        # 创建阶段
        self.stages = nn.ModuleList()
        current_dim = dims[0]
        stage_idx = 0
        
        for i in range(4):
            # 添加多个ConvNeXt块
            for _ in range(depths[i]):
                self.stages.append(ConvNeXtBlock(current_dim))
            
            # 如果不是最后一个阶段，添加下采样层
            if i < 3:
                self.stages.append(DownsampleLayer(current_dim, dims[i+1]))
                current_dim = dims[i+1]
        
        # 全局平均池化
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        # 分类头
        self.norm = nn.LayerNorm(current_dim, eps=1e-6)
        self.head = nn.Linear(current_dim, num_classes)
        
        # 权重初始化
        self._init_weights()
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.LayerNorm) or isinstance(m, LayerNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        x = self.stem(x)
        
        for stage in self.stages:
            x = stage(x)
        
        # 全局平均池化
        x = self.avgpool(x)  # [N, C, 1, 1]
        x = torch.flatten(x, 1)  # [N, C]
        
        # LayerNorm和分类头
        x = self.norm(x)
        x = self.head(x)
        
        return x

class Animal10Dataset(Dataset):
    """Animal-10 数据集"""
    def __init__(self, data_dir, csv_path, transform=None, subset_ratio=1.0):
        self.data_dir = data_dir
        self.transform = transform
        self.classes = ['butterfly', 'cat', 'chicken', 'cow', 'dog', 
                       'elephant', 'horse', 'sheep', 'spider', 'squirrel']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # 如果csv_path存在，读取CSV文件，否则直接从文件夹读取
        if os.path.exists(csv_path):
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} samples from CSV file")
        else:
            # 直接从文件夹结构创建数据集
            df = self._create_df_from_folders()
            print(f"Created {len(df)} samples from folder structure")
        
        # 如果需要子集，随机采样
        if subset_ratio < 1.0:
            df = df.sample(frac=subset_ratio, random_state=42)
            print(f"Using subset with {len(df)} samples ({subset_ratio*100}%)")
        
        self.samples = []
        for _, row in df.iterrows():
            img_path = os.path.join(self.data_dir, row['path'])
            label = self.class_to_idx[row['label']]
            self.samples.append((img_path, label))
    
    def _create_df_from_folders(self):
        """从文件夹结构创建DataFrame"""
        samples = []
        for category in self.classes:
            category_dir = os.path.join(self.data_dir, category)
            if not os.path.exists(category_dir):
                print(f"Warning: Category directory {category_dir} not found")
                continue
                
            # 获取所有图像文件
            for img_name in os.listdir(category_dir):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    samples.append({
                        'path': os.path.join(category, img_name),
                        'label': category
                    })
        return pd.DataFrame(samples)
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        try:
            # 尝试打开图像
            image = Image.open(img_path).convert('RGB')
            
            # 检查图像是否有效
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
        except Exception as e:
            # 如果图片损坏，创建黑色图片并记录错误
            print(f"Warning: Could not load image {img_path}: {e}")
            image = Image.new('RGB', (224, 224), (0, 0, 0))
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class Trainer:
    """训练器类"""
    def __init__(self, model, device, results_dir='../results'):
        self.model = model.to(device)
        self.device = device
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        self.train_losses = []
        self.val_losses = []
        self.train_accs = []
        self.val_accs = []
        
    def train_epoch(self, train_loader, criterion, optimizer, epoch):
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}')
        for inputs, labels in pbar:
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                'loss': running_loss/(pbar.n+1),
                'acc': 100.*correct/total
            })
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        
        self.train_losses.append(epoch_loss)
        self.train_accs.append(epoch_acc)
        
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader, criterion):
        self.model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * correct / total
        
        self.val_losses.append(val_loss)
        self.val_accs.append(val_acc)
        
        return val_loss, val_acc
    
    def test(self, test_loader):
        self.model.eval()
        all_preds = []
        all_labels = []
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, predicted = outputs.max(1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        test_acc = 100. * correct / total
        
        return test_acc, np.array(all_preds), np.array(all_labels)
    
    def plot_training_curves(self):
        """绘制训练曲线"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        ax1.plot(epochs, self.train_losses, 'b-', label='Training loss')
        ax1.plot(epochs, self.val_losses, 'r-', label='Validation loss')
        ax1.set_xlabel('Epochs')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True)
        
        ax2.plot(epochs, self.train_accs, 'b-', label='Training accuracy')
        ax2.plot(epochs, self.val_accs, 'r-', label='Validation accuracy')
        ax2.set_xlabel('Epochs')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Training and Validation Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{self.results_dir}/training_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_confusion_matrix(self, preds, labels, class_names):
        """绘制混淆矩阵"""
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(labels, preds)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(f'{self.results_dir}/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()

def create_data_loaders(data_dir, csv_dir, batch_size=32, subset_ratio=1.0):
    """创建数据加载器"""
    # 检查是否需要创建CSV文件
    train_csv = os.path.join(csv_dir, 'train.csv')
    val_csv = os.path.join(csv_dir, 'val.csv')
    test_csv = os.path.join(csv_dir, 'test.csv')
    
    if not all(os.path.exists(f) for f in [train_csv, val_csv, test_csv]):
        print("CSV files not found. Creating dataset split...")
        from utils import create_train_val_test_split
        create_train_val_test_split(data_dir, csv_dir)
    
    # 数据增强和预处理
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 创建数据集
    train_dataset = Animal10Dataset(
        data_dir=data_dir,
        csv_path=train_csv,
        transform=train_transform,
        subset_ratio=subset_ratio
    )
    
    val_dataset = Animal10Dataset(
        data_dir=data_dir,
        csv_path=val_csv,
        transform=val_test_transform,
        subset_ratio=subset_ratio
    )
    
    test_dataset = Animal10Dataset(
        data_dir=data_dir,
        csv_path=test_csv,
        transform=val_test_transform,
        subset_ratio=subset_ratio
    )
    
    print(f"Dataset sizes: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
    
    # 创建数据加载器
    num_workers = min(4, os.cpu_count())
    train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                             shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, 
                           shuffle=False, num_workers=num_workers, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, 
                            shuffle=False, num_workers=num_workers, pin_memory=True)
    
    return train_loader, val_loader, test_loader, train_dataset.classes

def main():
    # 以下部分为行参数定义
    parser = argparse.ArgumentParser(description='Animal-10 Image Classification')
    parser.add_argument('--data_dir', type=str, default='../data/Animals-10', 
                       help='Path to dataset directory')
    parser.add_argument('--csv_dir', type=str, default='../data', 
                       help='Path to CSV files directory')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--subset_ratio', type=float, default=1.0, 
                       help='Ratio of data to use for quick testing (0.2 for 20%)')
    parser.add_argument('--model_save_path', type=str, 
                       default='../results/best_model.pth', 
                       help='Path to save the best model')
    
    args = parser.parse_args()
    
    # 检查数据集结构
    from utils import check_dataset_structure
    check_dataset_structure(args.data_dir)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # 创建数据加载器
    print('Loading data...')
    train_loader, val_loader, test_loader, class_names = create_data_loaders(
        args.data_dir, args.csv_dir, args.batch_size, args.subset_ratio
    )
    
    # 创建模型
    print('Creating model...')
    model = ConvNeXt(num_classes=len(class_names))
    
    # 计算模型参数
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'Total parameters: {total_params/1e6:.2f}M')
    print(f'Trainable parameters: {trainable_params/1e6:.2f}M')
    
    # 创建训练器
    trainer = Trainer(model, device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.05)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    
    # 训练模型
    print('Training model...')
    best_val_acc = 0.0
    
    for epoch in range(args.epochs):
        train_loss, train_acc = trainer.train_epoch(train_loader, criterion, optimizer, epoch)
        val_loss, val_acc = trainer.validate(val_loader, criterion)
        
        print(f'Epoch {epoch+1}/{args.epochs}:')
        print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        
        scheduler.step()
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
            }, args.model_save_path)
            print(f'  Best model saved with val acc: {val_acc:.2f}%')
    
    # 绘制训练曲线
    trainer.plot_training_curves()
    
    # 测试最佳模型
    print('Testing best model...')
    checkpoint = torch.load(args.model_save_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    test_acc, preds, labels = trainer.test(test_loader)
    
    print(f'Test Accuracy: {test_acc:.2f}%')
    
    # 绘制混淆矩阵
    trainer.plot_confusion_matrix(preds, labels, class_names)
    
    # 保存结果到文件
    results = {
        'train_losses': trainer.train_losses,
        'val_losses': trainer.val_losses,
        'train_accs': trainer.train_accs,
        'val_accs': trainer.val_accs,
        'test_acc': test_acc,
        'best_val_acc': best_val_acc,
        'class_names': class_names,
        'predictions': preds.tolist(),
        'labels': labels.tolist()
    }
    
    import json
    with open(f'{trainer.results_dir}/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # 绘制类别准确率
    plot_class_accuracy(preds, labels, class_names, trainer.results_dir)
    
    print('Experiment completed! Results saved in', trainer.results_dir)

def plot_class_accuracy(preds, labels, class_names, save_dir):
    """绘制每个类别的准确率"""
    from sklearn.metrics import classification_report
    
    report = classification_report(labels, preds, target_names=class_names, output_dict=True)
    
    class_acc = []
    for i, class_name in enumerate(class_names):
        if class_name in report:
            class_acc.append(report[class_name]['recall'] * 100)
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(class_names)), class_acc)
    plt.xlabel('Class')
    plt.ylabel('Accuracy (%)')
    plt.title('Accuracy per Class')
    plt.xticks(range(len(class_names)), class_names, rotation=45, ha='right')
    
    # 添加数值标签
    for bar, acc in zip(bars, class_acc):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{acc:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{save_dir}/class_accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    main()