import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def create_train_val_test_split(data_dir, output_dir='../data'):
    """创建训练集、验证集和测试集的CSV文件"""
    categories = ['butterfly', 'cat', 'chicken', 'cow', 'dog', 
                  'elephant', 'horse', 'sheep', 'spider', 'squirrel']
    
    all_samples = []
    
    for category in categories:
        category_dir = os.path.join(data_dir, category)  # 直接读取类别文件夹
        if not os.path.exists(category_dir):
            print(f"Warning: {category_dir} does not exist")
            continue
            
        images = os.listdir(category_dir)
        for img in images:
            # 检查图像文件扩展名
            if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                all_samples.append({
                    'path': os.path.join(category, img),  # 路径格式: 类别/图片名
                    'label': category
                })
    
    # 转换为DataFrame
    df = pd.DataFrame(all_samples)
    
    # 划分数据集 (8:1:1)
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)
    
    # 保存CSV文件
    os.makedirs(output_dir, exist_ok=True)
    train_df.to_csv(os.path.join(output_dir, 'train.csv'), index=False)
    val_df.to_csv(os.path.join(output_dir, 'val.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'test.csv'), index=False)
    
    print(f"Dataset split created:")
    print(f"  Train: {len(train_df)} samples")
    print(f"  Validation: {len(val_df)} samples")
    print(f"  Test: {len(test_df)} samples")
    
    return train_df, val_df, test_df

def check_dataset_structure(data_dir):
    """检查数据集结构"""
    print(f"Checking dataset structure in: {data_dir}")
    
    categories = ['butterfly', 'cat', 'chicken', 'cow', 'dog', 
                  'elephant', 'horse', 'sheep', 'spider', 'squirrel']
    
    for category in categories:
        category_path = os.path.join(data_dir, category)
        if os.path.exists(category_path):
            images = [f for f in os.listdir(category_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
            print(f"  {category}: {len(images)} images")
        else:
            print(f"  {category}: NOT FOUND")


def calculate_class_weights(data_dir, csv_path):
    """计算类别权重用于不平衡数据"""
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    class_counts = df['label'].value_counts().sort_index()
    
    total_samples = len(df)
    num_classes = len(class_counts)
    
    # 计算类别权重
    class_weights = total_samples / (num_classes * class_counts)
    class_weights = class_weights / class_weights.sum() * num_classes
    
    return class_weights.to_dict()

def visualize_sample_images(data_dir, csv_path, num_samples=10, save_path='../results/sample_images.png'):
    """可视化样本图像"""
    import matplotlib.pyplot as plt
    from PIL import Image
    
    df = pd.read_csv(csv_path)
    samples = df.sample(num_samples)
    
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()
    
    for idx, (_, row) in enumerate(samples.iterrows()):
        if idx >= len(axes):
            break
            
        img_path = os.path.join(data_dir, row['path'])
        try:
            img = Image.open(img_path).convert('RGB')
            axes[idx].imshow(img)
            axes[idx].set_title(row['label'])
            axes[idx].axis('off')
        except:
            axes[idx].text(0.5, 0.5, 'Image not found', 
                          ha='center', va='center', transform=axes[idx].transAxes)
            axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Sample images saved to {save_path}")
